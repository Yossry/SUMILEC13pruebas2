# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """Partner extension."""

    _inherit = 'res.partner'



    """Document type: Lista de selección con los tipos de documento aceptados
       por la autoridad de impuestos (DIAN).
        11 - Registro civil
        12 - Tarjeta de identidad
        13 - Cédula de ciudadanía
        21 - Tarjeta de extranjería
        22 - Cédula de extranjería
        31 - NIT (Número de identificación tributaria)
        41 - Pasaporte
        42 - Tipo de documento extranjero
        43 - Para uso definido por la DIAN

        http://www.dian.gov.co/descargas/normatividad/Factura_Electronica/Anexo_001_R14465.pdf"""

    vat_type = fields.Selection([
        ('11', u'11 - Registro Civil'),
        ('12', u'12 - Tarjeta de identidad'),
        ('13', u'13 - Cédula de ciudadanía'),
        ('21', u'21 - Tarjeta de extranjería'),
        ('22', u'22 - Cédula de extranjería'),
        ('31', u'31 - NIT (Número de identificación tributaria)'),
        ('41', u'41 - Pasaporte'),
        ('42', u'42 - Documento de identificación extranjero'),
        ('43', u'43 - Sin identificación del exterior o para uso definido por la DIAN')
    ], string='VAT type',
        help='''Customer identifier, according to types given by the DIAN.
                If it is a natural person and has RUT use NIT''',
        required=False
    )
    vat_vd = fields.Char('vd', size=1, help='Digito de verificación', store=True)
    '''stock_holder = fields.Selection([
        ('sh', 'Stock holder'),
        ('nsh', 'No Stock holder')
    ], 'Stock holder', default='nsh', required=True)'''
    firstname = fields.Char()
    other_name = fields.Char()
    lastname = fields.Char()
    other_lastname = fields.Char()
    name = fields.Char(index=True)
    vat_num = fields.Char(string='NIF')

    @api.onchange('firstname', 'other_name', 'lastname', 'other_lastname')
    def _name_compute(self):
        for rec in self:
            if rec.company_type == 'person':
                rec.name = (str(rec.firstname) if rec.firstname else '') \
                           + ' ' + (str(rec.other_name) if rec.other_name else '') \
                           + ' ' + (str(rec.lastname) if rec.lastname else '') \
                           + ' ' + (str(rec.other_lastname) if rec.other_lastname else '')



    '''@api.onchange('vat')
    def onchange_vat(self):
        if self.vat:
            if '-' in self.vat and self.l10n_co_document_type == 'rut':
                dig = self.vat[self.vat.find('-')+1: self.vat.len()-1]
                self.vat_num = self.vat[0:self.vat.find('-')]
                self.vat_vd = dig
            else:
                self.vat_num = self.vat'''


    @api.onchange('vat_num')
    def _on_chage_vat(self):
        if self.l10n_co_document_type == 'rut':
            self.vat = str(self.vat_num) + '-' + str(self.vat_vd)
            self.vat_vd = self._check_vat_co()
        else:
            self.vat = self.vat_num

    @api.onchange('vat_vd')
    def _on_chage_vat_dv(self):
        if self.l10n_co_document_type == 'rut':
            self.vat = str(self.vat_num) + '-' + str(self.vat_vd)
        else:
            self.vat = self.vat_num

    @api.model
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        for record in self:
            if record.child_ids:
                for child in record.child_ids:
                    vals_ch= {
                        'vat_num' : record.vat_num,
                        'vat_vd' : record.vat_vd,
                        'vat' : record.vat,
                        'l10n_co_document_type' : record.l10n_co_document_type,
                        'vat_type' : record.vat_type,
                    }
                    child.write(vals_ch)
        return res

    @api.depends('vat_type', 'vat_num')
    def _check_vat_co(self):
        if self.vat_type != '31':
            return ''


        factor = [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3]
        factor = factor[-len(self.vat_num):]
        csum = sum([int(self.vat_num[i]) * factor[i] for i in range(len(self.vat_num))])
        check = csum % 11
        if check > 1:
            check = 11 - check
        return check

    def _onerror_msg(self, msg):
        return {'warning': {'title': _('Error!'), 'message': _(msg)}}

    @api.onchange('vat_type')
    def onchange_vat_type(self):

        return {'value': {'is_company': self.vat_type == '31'}}

    '''@api.onchange('vat_num')
    def onchange_vat(self):
        # Validaciones
        if not self.vat_type:
            return {'value': {'vat_vd': ''}}

        if self.vat_num:
            if len(self.vat_num) < 6:
                return self._onerror_msg(
                    u'VAT must have at least six digits.'
                )

            if not self.vat_num.isdigit() and self.vat_type != '41':
                return self._onerror_msg(u'VAT must have only numbers')

            if self.vat_type != '31':
                return {'value': {'vat_vd': ''}}

        return {'value': {'vat_vd': ''}}'''

    '''@api.onchange('company_type')
    def on_change_company_type(self):
        """
        This function changes the person type once the company type changes.
        If it is a company, document type 31 will be selected automatically as
        in Colombia it's more likely that it will be chosen by the user.
        @return: void
        """
        if self.company_type == 'company':
            self.l10n_co_document_type = "rut"
        else:
            self.l10n_co_document_type = False'''


    '''@api.onchange('vat_vd')
    def onchange_vat_vd(self):

        if self.vat_type == '31':
            

        return False'''

    def _commercial_fields(self):
        """
        Return the list of fields that are managed by the commercial entity
        to which a partner belongs.

        These fields are meant to be hidden on partners that aren't
        `commercial entities` themselves, and will be delegated to
        the parent `commercial entity`. The list is meant to be
        extended by inheriting classes.
        """
        return ['website']

    def copy(self):
        [partner_dic] = self.read(['name', 'vat', 'vat_num', 'vat_vd'])
        default = {}
        default.update({
            'name': '(copy) ' + partner_dic.get('name'),
        })
        return super(ResPartner, self).copy(default)

    def _check_vat(self):
        if self.company_id and self.vat and self.search(
                [('company_id', '=', self.company_id.id), ('vat', '=ilike', self.vat),
                 ('parent_id', '=', None)]).id != self.id:
            return False
        return True

    '''def _check_vat_vd(self):
        if self.vat_type == '31' and not self._check_vat_co(self.vat_type, self.vat_num, self.vat_vd):
            return False
        return True'''


    @api.onchange("l10n_co_document_type")
    def onchange_document_type(self):
        if self.l10n_co_document_type == 'rut':
            self.vat_type = '31'
        elif self.l10n_co_document_type == 'id_document':
            self.vat_type = '13'
        elif self.l10n_co_document_type == 'id_card':
            self.vat_type = '12'
        elif self.l10n_co_document_type == 'passport':
            self.vat_type = '41'
        elif self.l10n_co_document_type == 'foreign_id_card':
            self.vat_type = '22'
        elif self.l10n_co_document_type == 'external_id':
            self.vat_type = ''
        elif self.l10n_co_document_type == 'diplomatic_card':
            self.vat_type = ''
        elif self.l10n_co_document_type == 'residence_document':
            self.vat_type = ''
        elif self.l10n_co_document_type == 'civil_registration':
            self.vat_type = '11'
        elif self.l10n_co_document_type == 'national_citizen_id':
            self.vat_type = '13'

