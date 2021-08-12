# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.addons.website.models import ir_http
from odoo.http import request


class ProductTemplate(models.Model):
	_inherit = "product.template"    
	
	quote_products = fields.Boolean('Quote Products')
	
	_defaults = {
		'quote_products' : False
	}

class Website(models.Model):
	_inherit = 'website'


	def get_quote_products(self):   
		quote_ids=self.env['product.template'].sudo().search([('quote_products','=','True')])
		
		return quote_ids  

	def get_qty(self):
		res = 0
		if request.session['uid']:
			quote_cart_ids = self.env['quote.order'].sudo().search([('partner_id','=',self.env.user.partner_id.id)])
			request.session['quote_order_id'] = quote_cart_ids.id
		else:
			if 'quote_order_id' in request.session.keys():
				quote_cart_ids = self.env['quote.order'].sudo().browse(request.session['quote_order_id'])
			else:
				quote_cart_ids = self.env['quote.order'].sudo().browse(None)
		
		for i in quote_cart_ids.quote_lines:
			res = res +i.qty
		return int(res)

	
	def get_quote_cart_products(self):
		order =  self.env['quote.order'].sudo().search([])
		# quote_cart_ids = self.env['quote.order'].sudo().search([('partner_id','=', self.env.user.partner_id.id)])
		quote_cart_ids = self.env['quote.order'].sudo().browse(request.session['quote_order_id'])

		return quote_cart_ids.quote_lines

class QuoteOrderLine(models.Model):

	_name = 'quote.order.line'
	
	product_id = fields.Many2one('product.product')
	qty = fields.Float('Quantity')
	price = fields.Float('Price')
	quote_id = fields.Many2one('quote.order', 'Quote Order')
	
	def unlink(self):
		return super(QuoteOrderLine, self).unlink()
	
	
class QuoteOrder(models.Model):
	
	_name = 'quote.order'
	
	partner_id = fields.Many2one('res.partner')
	quote_lines = fields.One2many('quote.order.line', 'quote_id', string='Quote Lines')

	def unlink(self):
		for qt in self:
			for line in qt.quote_lines:
				line.sudo().unlink()
		return super(QuoteOrder, self).unlink()


class ResPartnerInherit(models.Model):
	_inherit = 'res.partner'

	last_website_quote_id = fields.Many2one('quote.order', compute='_compute_last_website_quote_id', string='Last Online Sales Order')

	def _compute_last_website_quote_id(self):
		QuoteOrder = self.env['quote.order']
		for partner in self:
			is_public = any([u._is_public()
							 for u in partner.with_context(active_test=False).user_ids])
			website = ir_http.get_request_website()
			if website and not is_public:
				partner.last_website_quote_id = QuoteOrder.search([
					('partner_id', '=', partner.id),
				],order='id desc',  limit=1)
			else:
				partner.last_website_quote_id = QuoteOrder
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
