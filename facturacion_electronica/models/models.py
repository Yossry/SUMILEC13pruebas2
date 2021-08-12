# -*- coding: utf-8 -*-
import base64

from odoo import models, fields, api
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import xml.etree.ElementTree as ET
import os
import requests
import zipfile
from datetime import datetime, date
import functools
import operator


class AccountDebitNote(models.TransientModel):
    _inherit = 'account.debit.note'

    concept_debit_note_id = fields.Many2one("dian.debitnoteconcept", string="Concepto")


class MoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    concept_note_credit_id = fields.Many2one("dian.creditnoteconcept", string="Concepto")


class ConceptNoteDebit(models.Model):
    _name = 'dian.debitnoteconcept'

    name = fields.Char(String='Descripción')
    code = fields.Char(String='Codigo')


class ConceptNoteCredit(models.Model):
    _name = 'dian.creditnoteconcept'

    name = fields.Char(String='Descripción')
    code = fields.Char(String='Codigo')


class PaymentMethod(models.Model):
    _name = 'dian.paymentmethod'

    name = fields.Char(String='Nombre')
    code = fields.Char(String='Codigo')


class FormaPago(models.Model):
    _name = 'dian.paymentmean'

    name = fields.Char(String='Nombre')
    code = fields.Char(String='Codigo')


class AccountInvoiceSend(models.TransientModel):
    _inherit = 'account.invoice.send'

    @api.onchange('template_id')
    def onchange_template_id(self):
        # r = super(AccountInvoiceSend, self).create(vals)

        ai_id = self._context['active_ids'][0]
        account_move = self.env['account.move'].search([('id', '=', ai_id)])
        ids = []
        if account_move.invoice_status_dian == "Exitoso":
            for line in account_move:
                for lines_attachment in line.attachment_ids:
                    ids.append(lines_attachment.id)
            attach = self.env['ir.attachment']
            for lines_attach in attach.search([('res_id', '=', ai_id)]):
                if lines_attach.mimetype == 'application/zip':
                    ids.append(lines_attach.id)

            self.attachment_ids = [(6, 0, ids)]
        else:
            super(AccountInvoiceSend, self).onchange_template_id()


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _default_payment_method(self):
        return self.env['dian.paymentmethod'].search([('code', '=', '1')], limit=1).id

    payment_method_id = fields.Many2one("dian.paymentmethod", string='Método de pago', default=_default_payment_method)

    payment_mean_id = fields.Many2one('dian.paymentmean', string='Forma de pago')
    description_code_credit = fields.Many2one("dian.creditnoteconcept", string='Concepto Nota de Credito')
    description_code_debit = fields.Many2one("dian.debitnoteconcept", string='Concepto Nota de Débito')
    debit_note = fields.Boolean(string='Nota débito', related='journal_id.debit_note')
    url_pdf = fields.Char(string='Representación grafica', track_visibility='onchange', copy=False)
    url_xml = fields.Char(string='Archivo XML', track_visibility='onchange', copy=False)
    invoice_status_dian = fields.Selection(selection=[('Exitoso', 'Exitoso'), ('Fallida', 'Fallida')],
                                           string='Estado de la factura DIAN', copy=False, track_visibility='onchange',
                                           readonly=True)
    description_status_dian = fields.Char(string='Descripcion del estado de la factura', copy=False,
                                          track_visibility='onchange', readonly=True)
    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='attachments_rel',
        column1='account_id',
        column2='attachment_id',
        string='Archivo Adjunto',
        copy=False
    )

    '''@api.onchange('invoice_date_due', 'invoice_payment_term_id')
    def onchange_invoice_date_due(self):
        for invoice in self:
            fecha_actual = date.today()
            if invoice.invoice_date_due > fecha_actual:
                invoice.payment_mean_id = 2
            elif invoice.invoice_date_due == fecha_actual:
                invoice.payment_mean_id = 1'''

    def action_invoice_sent(self):
        rslt = super(AccountMove, self).action_invoice_sent()
        template = self.env.ref('facturacion_electronica.email_template_electronic_invoice', raise_if_not_found=False)
        if self.url_pdf and self.invoice_status_dian == "Exitoso":
            rslt['context']['custom_layout'] = "facturacion_electronica.mail_electronic_invoice"
            rslt['context']['default_use_template'] = bool(template)
            rslt['context']['default_template_id'] = template and template.id or False
        return rslt

    def action_post1(self):

        file = 'plantilla.xml'
        full_file = os.path.abspath(os.path.join('', file))
        doc_xml = ET.parse(full_file)

        root = doc_xml.getroot()
        total_descuento = 0
        total_impuestos = 0
        total_retenciones = 0
        total = 0
        subtotal = 0
        FiscalResposability_c = ''
        nit_company = ''

        InvoiceRef = ''
        InvoiceTypeRef = ''
        InvoiceDateRef = ''
        DueDateRef = ''
        CMReasonCode_c = ''
        CMReasonDesc_c = ''
        DMReasonCode_c = ''
        DMReasonDesc_c = ''
        CalculationRate_c = ''
        CustID = ''

        Resolution_str = ''
        ResolutionPrefix = ''
        ResolutionDateInvoice = ''
        ResolutionDateFrom = ''
        ResolutionDateTo = ''
        ResolutionRankFrom = ''
        ResolutionRankTo = ''
        TecnicalKey = ''

        # control de producto regalo
        producto_regalo = []
        impuestosFactura = []
        impuestosFactura.append("IVA")

        for move in self:
            for line in move.invoice_line_ids:
                total_descuento = total_descuento + ((line.discount / 100) * line.price_unit * line.quantity)
                if line.price_unit < 0:
                    total_descuento = total_descuento + (-1 * line.price_unit)
                    # subtotal = subtotal + (-1 * line.price_unit)

                subtotal = subtotal + line.price_subtotal
                for tax in line.tax_ids:
                    if tax.type_tax.name == 'IVA':
                        total_impuestos = total_impuestos + ((tax.amount / 100) * ((line.price_unit * line.quantity) - (
                                (line.discount / 100) * line.price_unit * line.quantity)))
                    elif tax.type_tax.name == 'ReteIVA' or tax.type_tax.name == 'ReteFuente' or tax.type_tax.name == 'ReteICA':
                        total_retenciones = total_retenciones + ((tax.amount / 100) * (
                                (line.price_unit * line.quantity) - (
                                (line.discount / 100) * line.price_unit * line.quantity)))
            total = subtotal + total_impuestos

            FiscalResposability_c = self.GetResponsibilities(move.company_id.fiscal_responsibility_ids)
            nit_company = self.GetNitCompany(move.company_id.vat)
            CustNum = self.GetNitCompany(move.partner_id.vat)
            invoicetype = self.GetInvoiceType(move)
            CustID = self.TypeDocumentCust(move.partner_id.l10n_co_document_type)
            comment = self.narration

            if invoicetype == '91':
                InvoiceRef = move.reversed_entry_id.name
                InvoiceTypeRef = move.reversed_entry_id.document_type
                InvoiceDateRef = move.reversed_entry_id.invoice_date.strftime('%d/%m/%Y %H:%M:%S')
                DueDateRef = move.reversed_entry_id.invoice_date_due.strftime('%d/%m/%Y %H:%M:%S')
                CMReasonCode_c = move.description_code_credit.code
                CMReasonDesc_c = move.description_code_credit.name
                DMReasonCode_c = '0'
                DMReasonDesc_c = '0'
                CalculationRate_c = '0'
                DateCalculationRate_c = '0'

                Resolution_str = move.journal_id.refund_sequence_id.resolution_id.resolution_resolution
                ResolutionPrefix = move.journal_id.refund_sequence_id.prefix
                ResolutionDateInvoice = move.journal_id.refund_sequence_id.resolution_id.resolution_resolution_date.strftime(
                    '%Y-%m-%d')
                ResolutionDateFrom = move.journal_id.refund_sequence_id.resolution_id.resolution_date_from.strftime(
                    '%Y-%m-%d')
                ResolutionDateTo = move.journal_id.refund_sequence_id.resolution_id.resolution_date_to.strftime(
                    '%Y-%m-%d')
                ResolutionRankFrom = str(move.journal_id.refund_sequence_id.resolution_id.resolution_from)
                ResolutionRankTo = str(move.journal_id.refund_sequence_id.resolution_id.resolution_to)
                TecnicalKey = move.journal_id.refund_sequence_id.resolution_id.resolution_technical_key

            elif invoicetype == '92':
                InvoiceRef = move.debit_origin_id.name
                InvoiceTypeRef = move.debit_origin_id.document_type
                InvoiceDateRef = move.debit_origin_id.invoice_date.strftime('%d/%m/%Y')
                DueDateRef = move.debit_origin_id.invoice_date_due.strftime('%d/%m/%Y')
                CMReasonCode_c = '0'
                CMReasonDesc_c = '0'
                DMReasonCode_c = move.description_code_debit.code
                DMReasonDesc_c = move.description_code_debit.name
                CalculationRate_c = '0'
                DateCalculationRate_c = '0'

                Resolution_str = move.journal_id.sequence_id.resolution_id.resolution_resolution
                ResolutionPrefix = move.journal_id.sequence_id.prefix
                ResolutionDateInvoice = move.journal_id.sequence_id.resolution_id.resolution_resolution_date.strftime(
                    '%Y-%m-%d')
                ResolutionDateFrom = move.journal_id.sequence_id.resolution_id.resolution_date_from.strftime('%Y-%m-%d')
                ResolutionDateTo = move.journal_id.sequence_id.resolution_id.resolution_date_to.strftime('%Y-%m-%d')
                ResolutionRankFrom = str(move.journal_id.sequence_id.resolution_id.resolution_from)
                ResolutionRankTo = str(move.journal_id.sequence_id.resolution_id.resolution_to)
                TecnicalKey = move.journal_id.sequence_id.resolution_id.resolution_technical_key
            elif invoicetype == '02':
                InvoiceRef = '0'
                InvoiceTypeRef = '0'
                InvoiceDateRef = '0'
                DueDateRef = '0'
                CMReasonCode_c = '0'
                CMReasonDesc_c = '0'
                DMReasonCode_c = '0'
                DMReasonDesc_c = '0'
                CalculationRate_c = '0'
                DateCalculationRate_c = '0'

                Resolution_str = move.journal_id.sequence_id.resolution_id.resolution_resolution
                ResolutionPrefix = move.journal_id.sequence_id.prefix
                ResolutionDateInvoice = move.journal_id.sequence_id.resolution_id.resolution_resolution_date.strftime(
                    '%Y-%m-%d')
                ResolutionDateFrom = move.journal_id.sequence_id.resolution_id.resolution_date_from.strftime('%Y-%m-%d')
                ResolutionDateTo = move.journal_id.sequence_id.resolution_id.resolution_date_to.strftime('%Y-%m-%d')
                ResolutionRankFrom = str(move.journal_id.sequence_id.resolution_id.resolution_from)
                ResolutionRankTo = str(move.journal_id.sequence_id.resolution_id.resolution_to)
                TecnicalKey = move.journal_id.sequence_id.resolution_id.resolution_technical_key
            else:
                InvoiceRef = '0'
                InvoiceTypeRef = '0'
                InvoiceDateRef = '0'
                DueDateRef = '0'
                CMReasonCode_c = '0'
                CMReasonDesc_c = '0'
                DMReasonCode_c = '0'
                DMReasonDesc_c = '0'
                CalculationRate_c = '0'
                DateCalculationRate_c = '0'
                Resolution_str = move.journal_id.sequence_id.resolution_id.resolution_resolution
                ResolutionPrefix = move.journal_id.sequence_id.prefix
                ResolutionDateInvoice = move.journal_id.sequence_id.resolution_id.resolution_resolution_date.strftime(
                    '%Y-%m-%d')
                ResolutionDateFrom = move.journal_id.sequence_id.resolution_id.resolution_date_from.strftime('%Y-%m-%d')
                ResolutionDateTo = move.journal_id.sequence_id.resolution_id.resolution_date_to.strftime('%Y-%m-%d')
                ResolutionRankFrom = str(move.journal_id.sequence_id.resolution_id.resolution_from)
                ResolutionRankTo = str(move.journal_id.sequence_id.resolution_id.resolution_to)
                TecnicalKey = move.journal_id.sequence_id.resolution_id.resolution_technical_key

        for move in self:
            dato = move
            datos = dict(company=nit_company,
                         StateTaxID=nit_company,
                         IdentificationType=move.company_id.document_type_id.code,
                         Name=move.company_id.name,
                         RegimeType_c=move.company_id.regime_type,
                         FiscalResposability_c=FiscalResposability_c,
                         OperationType_c=move.company_id.operation_type_id.code,
                         CompanyType_c=move.company_id.company_type_id.code,
                         State=move.company_id.state_id.name,
                         StateNum=move.company_id.state_id.dian_state_code,
                         City=move.company_id.city,
                         CityNum=move.company_id.city_id.code,
                         Address1=move.company_id.street,
                         CurrencyCode=move.company_id.currency_id.name,
                         CountryName=move.company_id.country_id.name,
                         CountryCode=move.company_id.country_id.code,
                         OrderNum='1',
                         PostalZone=move.company_id.zip,
                         PhoneNum=move.company_id.phone,
                         Email=move.company_id.email,
                         WebPage=move.company_id.website,
                         CorporateRegistration=move.company_id.commercial_registration)
            move.EditaCompany(datos, root)
        for move in self:
            now = datetime.now()
            datos = dict(Company=nit_company,
                         InvoiceType=invoicetype,
                         InvoiceNum=move.name,
                         LegalNumber=move.name,
                         InvoiceRef=InvoiceRef,
                         InvoiceTypeRef=InvoiceTypeRef,
                         InvoiceDateRef=InvoiceDateRef,
                         DueDateRef=DueDateRef,
                         CMReasonCode_c=CMReasonCode_c,
                         CMReasonDesc_c=CMReasonDesc_c,
                         DMReasonCode_c=DMReasonCode_c,
                         DMReasonDesc_c=DMReasonDesc_c,
                         CustNum=CustNum,
                         ContactName=' ',
                         ContactCountry=' ',
                         ContactCity=' ',
                         ContactAddress=' ',
                         CustomerName=move.partner_id.name,
                         InvoiceDate=move.invoice_date.strftime('%d/%m/%Y'),
                         DueDate=move.invoice_date_due.strftime('%d/%m/%Y'),
                         DocWHTaxAmt=str(round(abs(total_retenciones), 2)),
                         InvoiceComment=comment,
                         CurrencyCode=move.partner_id.currency_id.name,
                         CurrencyCodeCurrencyID=move.partner_id.currency_id.name,
                         ContingencyInvoice='0',
                         NetWeight='0',
                         PorcAdministracion='0',
                         PorcImprevistos='0',
                         PorcUtilidad='0',
                         GrossWeight='0',
                         NumberBoxes='0',
                         PONum='0',
                         Remission='0',
                         Resolution=Resolution_str,
                         ResolutionPrefix=ResolutionPrefix,
                         ResolutionDateInvoice=ResolutionDateInvoice,
                         ResolutionDateFrom=ResolutionDateFrom,
                         ResolutionDateTo=ResolutionDateTo,
                         ResolutionRankFrom=ResolutionRankFrom,
                         ResolutionRankTo=ResolutionRankTo,
                         TecnicalKey=TecnicalKey,
                         IdSoftware=move.company_id.software_id,
                         TestSet=move.company_id.test_set,
                         PinSoftware=move.company_id.software_pin,
                         InvoicePeriod='0',
                         PaymentMeansID_c=move.payment_mean_id.code,
                         PaymentMeansDescription=move.payment_mean_id.name,
                         PaymentMeansCode_c=move.payment_method_id.code,
                         PaymentDurationMeasure=str(abs((move.invoice_date_due - move.invoice_date).days)),
                         PaymentDueDate=move.invoice_date_due.strftime('%Y-%m-%d'),
                         CalculationRate_c=CalculationRate_c,
                         DateCalculationRate_c=DateCalculationRate_c,
                         ConditionPay='0',
                         DspDocSubTotal=str(subtotal),
                         DocTaxAmt=str(total_impuestos),
                         DspDocInvoiceAmt=str(total),
                         Discount=str(total_descuento))
        move.EditaNodos('InvcHead', datos, root)

        for move in self:
            datos = []
            InvoiceNum = move.name
            CurrencyCode = move.partner_id.currency_id.name
            i = 1
            for line in move.invoice_line_ids:
                if line.price_unit > 0:
                    dato = dict(InvoiceNum=InvoiceNum,
                                InvoiceLine=str(i),
                                PartNum=line.product_id.default_code,
                                LineDesc=line.name,
                                PartNumPartDescription=line.name,
                                SellingShipQty=str(line.quantity),
                                SalesUM='UND',
                                UnitPrice=str(line.price_unit),
                                DocUnitPrice=str(line.price_unit),
                                DocExtPrice=str(line.price_unit * line.quantity),
                                DspDocExtPrice=str(line.price_unit * line.quantity),
                                DiscountPercent=str(line.discount),
                                Discount=str(line.price_unit * line.quantity * (line.discount / 100)),
                                DocDiscount='0',
                                DspDocLessDiscount=str(line.price_unit * line.quantity * (line.discount / 100)),
                                DspDocTotalMiscChrg='0',
                                CurrencyCode=CurrencyCode)
                    datos.append(dato)
                    i = i + 1
                else:
                    try:
                        producto_regalo.append(line.name.split("-")[1].lstrip())
                    except:
                        producto_regalo.append(line.name.split(":")[1].lstrip())

            self.GenerarLineasFact(datos, root)

        for move in self:
            datos = []
            InvoiceNum = move.name
            CurrencyCode = move.partner_id.currency_id.name
            i = 1
            for line in move.invoice_line_ids:
                if line.price_subtotal > 0 and not line.name in producto_regalo:
                    if len(line.tax_ids) == 0:
                        dato = dict(Company=nit_company,
                                    InvoiceNum=InvoiceNum,
                                    InvoiceLine=str(i),
                                    CurrencyCode=CurrencyCode,
                                    RateCode="IVA",
                                    DocTaxableAmt=str(line.price_subtotal),
                                    TaxAmt="0",
                                    DocTaxAmt="0",
                                    Percent="0",
                                    WithholdingTax_c="False")
                        datos.append(dato)
                    else:
                        for tax in line.tax_ids:
                            impuestosFactura.append(tax.type_tax.name)
                            dato = dict(Company=nit_company,
                                        InvoiceNum=InvoiceNum,
                                        InvoiceLine=str(i),
                                        CurrencyCode=CurrencyCode,
                                        RateCode=tax.type_tax.name,
                                        DocTaxableAmt=str(line.price_subtotal),
                                        TaxAmt=str(abs(line.price_subtotal * tax.amount / 100)),
                                        DocTaxAmt=str(abs(line.price_subtotal * tax.amount / 100)),
                                        Percent=(str("{0:.2f}".format(abs(tax.amount)))),
                                        WithholdingTax_c=str(tax.type_tax.retention))
                            datos.append(dato)

                i = i + 1
            self.GenerarLineasInvcTaxs(datos, root)

        for move in self:
            datos = []
            InvoiceNum = move.name
            CurrencyCode = move.partner_id.currency_id.name
            i = 1
            for line in move.invoice_line_ids:
                if line.price_unit > 0:
                    dato = dict(Company=nit_company,
                                InvoiceNum=InvoiceNum,
                                InvoiceLine=str(i),
                                MiscCode='0',
                                Description='Descuento',
                                MiscAmt=str(line.quantity * line.price_unit * (line.discount / 100)),
                                DocMiscAmt='0',
                                MiscCodeDescription='Descuento',
                                PercentAmt=str(line.discount),
                                MiscType='1', )

                else:
                    pos = 0
                    totalLinea = 0
                    descuento = line.quantity * line.price_unit
                    for move in self:
                        indice = 1
                        if pos > 0:
                            break
                        for line in move.invoice_line_ids:
                            if line.name in producto_regalo:
                                totalLinea = line.quantity * line.price_unit
                                pos = indice
                                break
                            indice = indice + 1

                    if totalLinea == 0:
                        pos = 0
                        totalLinea = 1

                    dato = dict(Company=nit_company,
                                InvoiceNum=InvoiceNum,
                                InvoiceLine=str(pos),
                                MiscCode='0',
                                Description='Descuento',
                                MiscAmt=str(-1 * descuento),
                                DocMiscAmt='0',
                                MiscCodeDescription='Descuento',
                                PercentAmt=str(((-1 * descuento) * 100) / totalLinea),
                                MiscType='1', )
                    datos.append(dato)
                i = i + 1
            self.GenerarLineasInvcMisc(datos, root)

        for move in self:
            FiscalResposability_partner = self.GetResponsibilities(move.partner_id.fiscal_responsibility_partner_ids)
            datos = dict(Company=nit_company,
                         CustID=CustID,
                         CustNum=CustNum,
                         ResaleID=CustNum,
                         Name=move.partner_id.name,
                         Address1=move.partner_id.street,
                         EMailAddress=move.partner_id.email,
                         PhoneNum=move.partner_id.phone,
                         CurrencyCode=move.partner_id.currency_id.name,
                         Country=move.partner_id.country_id.name,
                         CountryCode=move.partner_id.country_id.code,
                         PostalZone=move.partner_id.zip,
                         RegimeType_c=move.partner_id.organization_type_id.code,
                         FiscalResposability_c=FiscalResposability_partner,
                         State=move.partner_id.state_id.name,
                         StateNum=move.partner_id.state_id.dian_state_code,
                         City=move.partner_id.city_id.name,
                         CityNum=move.partner_id.city_id.code,
                         CorporateRegistration=move.partner_id.commercial_registration_partner)
            move.EditaNodos('Customer', datos, root)
            datos = [dict(Company=nit_company,
                          RateCode='IVA',
                          TaxCode='IVA',
                          Description='Impuesto de Valor Agregado',
                          IdImpDIAN_c='01',
                          ),
                     ]
            if 'ReteFuente' in impuestosFactura:
                datos.append(
                    dict(Company=nit_company,
                         RateCode='ReteFuente',
                         TaxCode='ReteFuente',
                         Description='Retención sobre Renta',
                         IdImpDIAN_c='06',
                         ),
                )

            if 'AIU' in impuestosFactura:
                datos.append(
                    dict(Company=nit_company,
                         RateCode='AIU',
                         TaxCode='AIU',
                         Description='Otros tributos, tasas, contribuciones, y similares',
                         IdImpDIAN_c='ZZ',
                         ),
                )

            move.GenerarLineasSalesTRCs(datos, 'SalesTRC', root)

        for move in self:
            datos = dict(Company=nit_company,
                         IdentificationType=CustID,
                         COOneTimeID=CustNum,
                         CompanyName=move.partner_id.name,
                         CountryName=move.partner_id.country_id.name,
                         CountryCode=move.partner_id.country_id.code, )

            move.EditaNodos('COOneTime', datos, root)

        directorio = "Facturacion/ArchivosXML/" + nit_company + "/"
        directoriozip = "Facturacion/Zip/" + nit_company + "/"

        try:
            os.stat(directorio)
            os.stat(directoriozip)
        except:
            os.makedirs(directorio)
            os.makedirs(directoriozip)

        new_file = directorio + move.name + '.xml'

        # new_file = directorio + 'P126.xml'
        doc_xml.write(new_file)
        for move in self:
            ip_ws = str(move.company_id.ip_webservice)
        url = ''
        if invoicetype == '01':
            url = 'http://' + ip_ws + '/WS_Facturacion_Electronica1.8/api/EnvioFactura'
            # url = 'http://localhost:57780/api/EnvioFactura'
        elif invoicetype == '02':
            url = 'http://' + ip_ws + '/WS_Facturacion_Electronica1.8/api/EnvioFacturaExportacion'
        elif invoicetype == '91':
            url = 'http://' + ip_ws + '/WS_Facturacion_Electronica1.8/api/EnvioNotaCredito'
        else:
            url = 'http://' + ip_ws + '/WS_Facturacion_Electronica1.8/api/EnvioNotaDebito'

        headers = {'content-type': 'text/xml;charset=utf-8'}

        body = open(new_file, "r").read()

        responsews = requests.post(url, data=body.encode('utf-8'), headers=headers)
        respuesta = eval(responsews.content.decode('utf-8'))
        tipodato = type(responsews)
        resultados = ""
        attach = ""
        respuestaws = ""
        if responsews.status_code == 200:
            if 'Respuesta' in respuesta:
                resultados = respuesta['Respuesta']
                attach = self.GetAttach(resultados)
                respuestaws = self.GetResponseWS(resultados)

            estado_factura = ''
            if respuestaws == 'PROCESADO_CORRECTAMENTE':
                estado_factura = 'Exitoso'

                url_xml = 'http://' + ip_ws + '/WS_Facturacion_Electronica1.8/AttachedDocuments/' + str(
                    nit_company) + '/' + attach
                url_pdf = 'http://' + ip_ws + '/WS_Facturacion_Electronica1.8/facturaPDF/' + str(
                    nit_company) + '/' + self.name + '.pdf'

                my_xml = requests.get(url_xml).content
                my_pdf = requests.get(url_pdf).content
                open(directoriozip + attach, 'wb').write(my_xml)
                open(directoriozip + self.name + '.pdf', 'wb').write(my_pdf)
                try:
                    import zlib
                    compression = zipfile.ZIP_DEFLATED
                except:
                    compression = zipfile.ZIP_STORED

                zf = zipfile.ZipFile(directoriozip + attach[0:len(attach) - 4] + '.zip', mode='w')
                try:
                    zf.write(directoriozip + attach, compress_type=compression,
                             arcname=os.path.basename(directoriozip + attach))
                    zf.write(directoriozip + self.name + '.pdf', compress_type=compression,
                             arcname=os.path.basename(directoriozip + self.name + '.pdf'))
                finally:
                    zf.close()
                name_zip = attach[0:len(attach) - 4]
                file_zip = directoriozip + name_zip + '.zip'''
                my_zip = open(file_zip, 'rb').read()
            else:
                estado_factura = 'Fallida'

            '''return (self.write({
                'url_pdf': url_pdf,
                'url_xml': url,
                'invoice_status_dian': dict_resp['Respuesta']
            }))'''

            if estado_factura == 'Exitoso':
                return (self.env['ir.attachment'].create({
                    'name': attach[0:len(attach) - 4] + ".zip",
                    'type': 'binary',
                    'res_id': self.id,
                    'res_model': 'account.move',
                    'datas': base64.b64encode(my_zip),
                    'mimetype': 'application/zip'
                }), self.write({
                    'url_pdf': url_pdf,
                    'url_xml': url_xml,
                    'description_status_dian': respuestaws,
                    'invoice_status_dian': estado_factura
                }))
            else:
                return (self.write({
                    'description_status_dian': respuestaws,
                    'invoice_status_dian': estado_factura
                }))
        elif responsews.status_code == 500:
            raise UserError("Error en la conexión al Web service")

        # raise UserError(respuesta)

    def _get_ipwebservice(self):
        ip_ws = self.env['res.company'].search().filtered('ip_webservice')
        return ip_ws

    def EditaCompany(self, datos, root):
        nodos = root.findall("./Company/")
        for node in nodos:
            tag = node.tag
            if tag in datos:
                node.text = datos[tag]
            else:
                node.text = ''

    def EditaNodos(self, rama, datos, root):
        nodos = root.findall('.//' + rama + '/')
        # print(nodos)
        for node in nodos:
            tag = node.tag
            # print(tag)
            if tag in datos:
                node.text = datos[tag]
            else:
                node.text = ''

    def GenerarLineasFact(self, datos, root):
        node_root = root.find('./InvcDtls')
        if len(datos) > 0:
            if len(datos) > 1:
                i = 2
                longitud = len(datos)
                for x in range(longitud - 1):
                    InvcDtl = ET.Element('InvcDtl')
                    InvcDtl.attrib['id'] = str(i)
                    node_root.append(InvcDtl)
                    InvoiceNum = ET.SubElement(InvcDtl, 'InvoiceNum')
                    InvoiceLine = ET.SubElement(InvcDtl, 'InvoiceLine')
                    PartNum = ET.SubElement(InvcDtl, 'PartNum')
                    LineDesc = ET.SubElement(InvcDtl, 'LineDesc')
                    PartNumPartDescription = ET.SubElement(InvcDtl, 'PartNumPartDescription')
                    SellingShipQty = ET.SubElement(InvcDtl, 'SellingShipQty')
                    SalesUM = ET.SubElement(InvcDtl, 'SalesUM')
                    UnitPrice = ET.SubElement(InvcDtl, 'UnitPrice')
                    DocUnitPrice = ET.SubElement(InvcDtl, 'DocUnitPrice')
                    DocExtPrice = ET.SubElement(InvcDtl, 'DocExtPrice')
                    DspDocExtPrice = ET.SubElement(InvcDtl, 'DspDocExtPrice')
                    DiscountPercent = ET.SubElement(InvcDtl, 'DiscountPercent')
                    Discount = ET.SubElement(InvcDtl, 'Discount')
                    DocDiscount = ET.SubElement(InvcDtl, 'DocDiscount')
                    DspDocLessDiscount = ET.SubElement(InvcDtl, 'DspDocLessDiscount')
                    DspDocTotalMiscChrg = ET.SubElement(InvcDtl, 'DspDocTotalMiscChrg')
                    CurrencyCode = ET.SubElement(InvcDtl, 'CurrencyCode')
                    i += 1

            detalles = root.findall('./InvcDtls/')
            i = 0
            for detalle in detalles:
                for node in detalle:
                    tag = node.tag
                    dic = datos[i]
                    if tag in dic:
                        node.text = dic[tag]
                    else:
                        node.text = ''
                i += 1

    def GenerarLineasInvcTaxs(self, datos, root):
        node_root = root.find('./InvcTaxs')
        if len(datos) > 0:
            if len(datos) > 1:
                i = 2
                longitud = len(datos)
                for x in range(longitud - 1):
                    InvcTax = ET.Element('InvcTax')
                    InvcTax.attrib['id'] = str(i)
                    node_root.append(InvcTax)
                    Company = ET.SubElement(InvcTax, 'Company')
                    InvoiceNum = ET.SubElement(InvcTax, 'InvoiceNum')
                    InvoiceLine = ET.SubElement(InvcTax, 'InvoiceLine')
                    CurrencyCode = ET.SubElement(InvcTax, 'CurrencyCode')
                    RateCode = ET.SubElement(InvcTax, 'RateCode')
                    DocTaxableAmt = ET.SubElement(InvcTax, 'DocTaxableAmt')
                    TaxAmt = ET.SubElement(InvcTax, 'TaxAmt')
                    DocTaxAmt = ET.SubElement(InvcTax, 'DocTaxAmt')
                    Percent = ET.SubElement(InvcTax, 'Percent')
                    WithholdingTax_c = ET.SubElement(InvcTax, 'WithholdingTax_c')
                    i += 1

            detalles = root.findall('./InvcTaxs/')
            i = 0
            for detalle in detalles:
                for node in detalle:
                    tag = node.tag
                    dic = datos[i]
                    if tag in dic:
                        node.text = dic[tag]
                    else:
                        node.text = ''
                i += 1

    def GenerarLineasInvcMisc(self, datos, root):
        node_root = root.find('./InvcMiscs')
        if len(datos) > 0:
            if len(datos) > 1:
                i = 2
                longitud = len(datos)
                for x in range(longitud - 1):
                    InvcMisc = ET.Element('InvcMisc')
                    InvcMisc.attrib['id'] = str(i)
                    node_root.append(InvcMisc)
                    Company = ET.SubElement(InvcMisc, 'Company')
                    InvoiceNum = ET.SubElement(InvcMisc, 'InvoiceNum')
                    InvoiceLine = ET.SubElement(InvcMisc, 'InvoiceLine')
                    MiscCode = ET.SubElement(InvcMisc, 'MiscCode')
                    Description = ET.SubElement(InvcMisc, 'Description')
                    MiscAmt = ET.SubElement(InvcMisc, 'MiscAmt')
                    DocMiscAmt = ET.SubElement(InvcMisc, 'DocMiscAmt')
                    MiscCodeDescription = ET.SubElement(InvcMisc, 'MiscCodeDescription')
                    PercentAmt = ET.SubElement(InvcMisc, 'PercentAmt')
                    MiscType = ET.SubElement(InvcMisc, 'MiscType')
                    i += 1

            detalles = root.findall('./InvcMiscs/')
            i = 0
            for detalle in detalles:
                for node in detalle:
                    tag = node.tag
                    dic = datos[i]
                    if tag in dic:
                        node.text = dic[tag]
                    else:
                        node.text = ''
                i += 1

    def GenerarLineasSalesTRCs(self, datos, rama, root):
        node_root = root.find('./' + rama + 's')
        if len(datos) > 0:
            if len(datos) > 1:
                i = 2
                longitud = len(datos)
                for x in range(longitud - 1):
                    SalesTRC = ET.Element('SalesTRC')
                    SalesTRC.attrib['id'] = str(i)
                    node_root.append(SalesTRC)
                    Company = ET.SubElement(SalesTRC, 'Company')
                    RateCode = ET.SubElement(SalesTRC, 'RateCode')
                    TaxCode = ET.SubElement(SalesTRC, 'TaxCode')
                    Description = ET.SubElement(SalesTRC, 'Description')
                    IdImpDIAN_c = ET.SubElement(SalesTRC, 'IdImpDIAN_c')
                    i += 1

            detalles = root.findall('./' + rama + 's/')
            i = 0
            for detalle in detalles:
                for node in detalle:
                    tag = node.tag
                    dic = datos[i]
                    if tag in dic:
                        node.text = dic[tag]
                    else:
                        node.text = ''
                i += 1

    # Obtener una cadena con las responsabilidades fiscales de la empresa o del cliente
    def GetResponsibilities(self, datos):
        i = 0
        FiscalResposability = ''
        for responsability in datos:
            if i == len(datos) - 1:
                FiscalResposability = FiscalResposability + responsability.name
            else:
                FiscalResposability = FiscalResposability + responsability.name + ';'
            i += 1

        return FiscalResposability

    def GetInvoiceType(self, datos):
        invoicetype = ''
        for dato in datos:
            if dato.type == 'out_refund' and dato.debit_note == False:
                # invoicetype = '91'
                invoicetype = dato.journal_id.refund_sequence_id.resolution_id.document_type
            elif dato.type != 'out_refund' and dato.debit_note == True:
                # invoicetype = '92'
                invoicetype = dato.journal_id.sequence_id.resolution_id.document_type
            elif dato.type != 'out_refund' and dato.debit_note == False:
                # invoicetype = dato.document_type
                invoicetype = dato.journal_id.sequence_id.resolution_id.document_type
            return invoicetype

    def GetType(self, invoice):
        result = ''
        if invoice == '01' or invoice == '02':
            result = 'ad'
        elif invoice == '91':
            result = 'nc'
        elif invoice == '92':
            result = 'nd'
        return

    def GetNitCompany(self, number):
        document = ''
        if '-' in number:
            document = number[0:number.find('-')]
        else:
            document = number
        return document

    def TypeDocumentCust(self, typedocument):
        type = ''
        if typedocument == 'rut':
            type = '31'
        elif typedocument == 'id_document':
            type = '13'
        elif typedocument == 'id_card':
            type = '12'
        elif typedocument == 'passport':
            type = '41'
        elif typedocument == 'foreign_id_card':
            type = '22'
        elif typedocument == 'external_id':
            type = ''
        elif typedocument == 'diplomatic_card':
            type = ''
        elif typedocument == 'residence_document':
            type = ''
        elif typedocument == 'civil_registration':
            type = '11'
        elif typedocument == 'national_citizen_id':
            type = '13'
        return type

    def GetResponseWS(self, response):
        respuesta = ''
        if ';nombreattach:' in response:
            respuesta = response[0:response.find(';nombreattach:')]
        else:
            respuesta = response
        return respuesta

    def GetAttach(self, response):
        respuesta = ''
        if ';nombreattach:' in response:
            respuesta = response[response.find(';nombreattach:') + 14:len(response)]
        return respuesta

    def post(self):
        res = super(AccountMove, self).post()
        send_dian = self._context.get('send_dian', False)
        if send_dian == True:
            if res == True:
                if self._context.get('active_model') == 'account.move':
                    domain = [('id', 'in', self._context.get('active_ids', [])), ('state', '=', 'posted')]

                moves = self.env['account.move'].search(domain).filtered('line_ids')
                for move in moves:
                    if move.state == 'posted':
                        move.action_post1()
        return res


class Company(models.Model):
    _inherit = 'res.company'

    operation_type_id = fields.Many2one("dian.operationtype", string='Tipo de operación', required=True)
    company_type_id = fields.Many2one("dian.companytype", string='Tipo de empresa', required=True)
    document_type_id = fields.Many2one("dian.documenttype", string='Tipo de documento', required=True)
    regime_type = fields.Char(string='Tipo de regimen', required=True)
    fiscal_responsibility_ids = fields.Many2many("dian.fiscalresponsibility", string='Responsabilidades fiscales')
    commercial_registration = fields.Char(string='Matricula mercantil', required=True)

    software_pin = fields.Char(string='PIN del software')
    test_set = fields.Char(string='Test Set')
    software_id = fields.Char(string='ID del software')
    # city_id = fields.Many2one('res.city', string='Ciudad')
    ip_webservice = fields.Char(string='IP WebService')


class ResCity(models.Model):
    _inherit = 'res.country.state.city'

    dian_city_code = fields.Char(string='Código de municipio')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # city_id = fields.Many2one('res.city', string='Ciudad')
    document_type_id = fields.Many2one("dian.documenttype", string='Tipo de documento', required=True)
    organization_type_id = fields.Many2one('dian.companytype', string='Tipo de organizacion')
    fiscal_responsibility_partner_ids = fields.Many2many("dian.fiscalresponsibility",
                                                         string='Responsabilidades fiscales')
    commercial_registration_partner = fields.Char(string='Matricula mercantil')
    # representation_type_id = fields.Many2one('dian.fiscalresponsibility', string='Tipo de representación')
    # establishment_type_id = fields.Many2one('dian.fiscalresponsibility', string='Tipo de establecimiento')
    # customs_type_ids = fields.Many2many('dian.fiscalresponsibility', string='Usuario aduanero')
    # large_taxpayer = fields.Boolean(string="Gran contribuyente", default=False)
    # simplified_regimen = fields.Boolean(string="Regimen simplificado", default=False)
    # fiscal_regimen = fields.Many2one('dian.fiscalregimen', string='Regimen fiscal')


class ResCountry(models.Model):
    _inherit = 'res.country'

    code_dian = fields.Char(string='Codigo DIAN', readonly=True)


class FiscalRegimen(models.Model):
    _name = 'dian.fiscalregimen'

    name = fields.Char(String='Nombre')
    code = fields.Char(String='Codigo')


class AccountTax(models.Model):
    _inherit = 'account.tax'

    type_tax = fields.Many2one('dian.typetax', string='Tipo de impuesto')


class TypeTax(models.Model):
    _name = 'dian.typetax'

    name = fields.Char(string='Nombre')
    code = fields.Char(string='Codigo')
    description = fields.Char(string='Descripción')
    retention = fields.Boolean(string="Retención", default=False)


class OperationType(models.Model):
    _name = 'dian.operationtype'
    _description = 'tipos de operaciones DIAN'

    code = fields.Char(string='Codido', required=True)
    name = fields.Char(string='Nombre', required=True)


class CompanyType(models.Model):
    _name = 'dian.companytype'
    _description = 'tipo de compañia'

    code = fields.Char(string='Codido', required=True)
    name = fields.Char(string='Nombre', required=True)


class DocumentType(models.Model):
    _name = 'dian.documenttype'
    _description = 'tipo de compañia'

    code = fields.Char(string='Codido', required=True)
    name = fields.Char(string='Nombre', required=True)


class FiscalResponsibility(models.Model):
    _name = 'dian.fiscalresponsibility'
    _description = 'responsabilidades fiscales'

    name = fields.Char(string='Codido', required=True)
    description = fields.Char(string='Descripción', required=True)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    # resolution_id = fields.Many2one('dian.resolution', string='Resolución')
    debit_note = fields.Boolean(string="Nota de débito", default=False)
    '''resolution = fields.Char(string='Resolución de facturación', required=True)
    start_range = fields.Char(string='Rango Inicial', required=True)
    end_range = fields.Char(string='Rango Final', required=True)
    start_date = fields.Datetime(string='Fecha de resolución', required=True)
    end_date = fields.Datetime(string='Fecha de finalización de resolución', required=True)
    technical_key = fields.Char(string='Clave tecnica', required=True)'''


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    # @api.model
    def _create_invoice(self, order, so_line, amount, send_dian=False):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        send_dian = self._context.get('send_dian', False)
        if send_dian == True:
            if res.state == 'draft':
                move = res.action_post()
                if res.state == 'posted':
                    res.action_post1()
        return res

    '''def create_invoices(self):
        send_dian  = self._context.get('send_dian', False)
        if send_dian == True:
            return ""'''

    '''def create_invoices(self):
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        return res'''


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # @api.model
    def _create_invoices(self, grouped=False, final=False):
        res = super(SaleOrder, self)._create_invoices(grouped, final)
        send_dian = self._context.get('send_dian', False)
        if send_dian == True:
            for move in res:
                if move.state == 'draft':
                    move.action_post()
                    if move.state == 'posted':
                        move.action_post1()
        return res

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        payment_term = self.env['account.payment.term'].search([('name', '=', 'Pago inmediato')], limit=1)
        if payment_term.name == 'Pago inmediato':
            res['payment_mean_id'] = 1
        else:
            res['payment_mean_id'] = 2
        return res


'''class ValidateAccountMove(models.Model):
    _inherit = 'validate.account.move'

    def validate_move(self):'''
