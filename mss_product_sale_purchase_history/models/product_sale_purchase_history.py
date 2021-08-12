# -*- coding: utf-8 -*-

from openerp import api, fields, models ,_

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    purchase_line_ids = fields.One2many('purchase.order.line', 'product_tmpl_id', 'Purchase Lines')
    sale_line_ids = fields.One2many('sale.order.line', 'product_tmpl_id', 'Sale Lines')

class ProductProduct(models.Model):
    _inherit = 'product.product'

    purchase_line_ids = fields.One2many('purchase.order.line', 'product_id', 'Purchase Lines')
    sale_line_ids = fields.One2many('sale.order.line', 'product_id', 'Sale Lines')

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_tmpl_id = fields.Many2one('product.template', related='product_id.product_tmpl_id', string="Product Template")

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_tmpl_id = fields.Many2one('product.template', related='product_id.product_tmpl_id', string="Product Template")

