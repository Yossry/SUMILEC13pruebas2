# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import datetime
from odoo import http
from odoo.http import request
import json
class OdooWebsiteProductQuote(http.Controller):

	@http.route(['/quote'], type='http', auth="public", website=True)
	def quote(self, **post):
		cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
		return request.render("odoo_website_product_quote.quote")


	@http.route(['/quote/cart'], type='http', auth="public", website=True)
	def quote_cart(self, access_token=None, revive='', **post):
		cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
		
		return request.render("odoo_website_product_quote.quote_cart")
	
	@http.route(['/quote/product/selected/<model("product.template"):product_id>'], type='http', auth="public", website=True)
	def quote_multiple(self, product_id, **post):
		cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
		
		quote_obj = request.env['quote.order']
		quote_line_obj = request.env['quote.order.line']
		partner = request.env.user.partner_id
		quote_order_id = request.session.get('quote_order_id')
		if not quote_order_id:
			last_quote_order = partner.last_website_quote_id
			quote_order_id = last_quote_order.id

		quote_order = request.env['quote.order'].sudo().browse(quote_order_id).exists() if quote_order_id else None
		
		product_product_obj = request.env['product.product'].sudo().search([('product_tmpl_id','=', product_id.id)], limit=1)
		# quote_filter_id = quote_obj.sudo().search([('partner_id','=', partner.id)])
		# if not quote_filter_id:
		request.session['quote_order_id'] = None
		if not quote_order:
			quote = quote_obj.sudo().create({'partner_id': partner.id})
			quote_line_ids = quote_line_obj.sudo().search([('product_id.product_tmpl_id','=', product_id.id),('quote_id','=',quote.id)])
			
			if quote_line_ids:
				quote_line_ids.update({'qty': quote_line_ids.qty})
			else:
				quote_line = quote_line_obj.sudo().create({
					'product_id': product_product_obj.id,
					'qty': 1,
					'price': product_product_obj.lst_price,
					'quote_id': quote.id,	
				})
			request.session['quote_order_id'] = quote.id
		if quote_order:
			if not request.session.get('quote_order_id'):
				request.session['quote_order_id'] = quote_order.id
			# quote_final_id = quote_obj.sudo().search([('partner_id','=', partner.id)])
			
			quote_line_ids = quote_line_obj.sudo().search([('product_id.product_tmpl_id','=', product_id.id),('quote_id','=',quote_order.id)])
			
			if quote_line_ids:
				quote_line_ids.update({'qty': quote_line_ids.qty})
			else:
				quote_line = quote_line_obj.sudo().create({
					'product_id': product_product_obj.id,
					'qty': 1,
					'price': product_product_obj.lst_price,
					'quote_id': quote_order.id,	
				})
		# else:
		# 	request.session['quote_order_id'] = None
			
		return request.render("odoo_website_product_quote.quote_cart")	

	@http.route(['/quote/product/selected/nonlogin'], type='http', auth="public", website=True)
	def quote_multiple_nonlogin(self, **post):
		cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
		countries = request.env['res.country'].sudo().search([])
		states = request.env['res.country.state'].sudo().search([])
		render_values ={}
		render_values={
					'countries': countries,
					'states': states,
			}
		return request.render("odoo_website_product_quote.get_quotation_request",render_values)

	@http.route(['/quote/cart/update_json'], type='json', auth="public", website=True)
	def get_cart_qty(self,jsdata, **post):
		
		# quote_cart_ids = request.env['quote.order'].sudo().search([('partner_id','=', request.env.user.partner_id.id)])
		quote_cart_ids =request.env['quote.order'].sudo().browse(request.session['quote_order_id'])

		for i in quote_cart_ids.quote_lines:
			for j in jsdata:
				for x, y in j.items():
					
					if i.id == int(x):
						
						i.update({'qty': y})
		return True	
		
	@http.route(['/process/quote'], type='http', auth="public", website=True)
	def get_quote(self, **post):
		cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
		# order = request.env['quote.order'].sudo().search([('partner_id','=', request.env.user.partner_id.id)])
		order =request.env['quote.order'].sudo().browse(request.session['quote_order_id'])

		val={'order':order}
		return request.render("odoo_website_product_quote.get_billing",val)

	@http.route(['/process/quote/nonlogin'], type='http', auth="public", website=True)
	def get_quote_nonlogin(self, **post):
		cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
		
		partner_obj = request.env['res.partner']
		partner = partner_obj.sudo().create({ 
		  'name' : post['name'],
		  'email' : post['email'],
		  'phone' : post['phone'],
		  'street': post['street'],
		  'city':post['city'],
		  'zip':post['zip'],
		  'country_id':int(post['country_id']),
		  'state_id':int(post['state_id']),

		})
		
		# order = request.env['quote.order'].sudo().search([('partner_id','=', request.env.user.partner_id.id)])

		product_obj = request.env['product.template']        
		#sale_order_obj = request.env['sale.order']
		sale_order_line_obj = request.env['sale.order.line']
		line_vals ={}
		pricelist_id = request.website.get_current_pricelist().id
		vals = {
				'partner_id': partner.id,
				'pricelist_id': pricelist_id,
				'user_id': request.website.salesperson_id and request.website.salesperson_id.id,
				'team_id': request.website.salesteam_id and request.website.salesteam_id.id
			}    	
		sale_order_create = request.env['sale.order'].sudo().create(vals)
		order = request.env['quote.order'].sudo().browse(request.session['quote_order_id'])
		order.update({'partner_id': partner.id})
		for i in order.quote_lines:
			line_vals = {    
						'product_id': i.product_id.id, 
						'name': i.product_id.name,
						'product_uom_qty': i.qty, 
						'customer_lead':7, 
						'product_uom':i.product_id.uom_id.id,
						'order_id': sale_order_create.id  }
			sale_order_line_create = sale_order_line_obj.sudo().create(line_vals)
			#i.sudo().unlink()
		
		order.sudo().unlink()
		request.session['quote_order_id'] = False
		return request.render("odoo_website_product_quote.quote_thankyou")

	@http.route(['/shop/product/quote/confirm'], type='http', auth="public", website=True)
	def quote_confirm(self, **post):
		# order = request.env['quote.order'].sudo().search([('partner_id','=', request.env.user.partner_id.id)])
		order = request.env['quote.order'].sudo().browse(request.session['quote_order_id'])
		
		product_obj = request.env['product.template']        
		partner_obj = request.env['res.partner']
		sale_order_obj = request.env['sale.order']
		sale_order_line_obj = request.env['sale.order.line']
		line_vals ={}
		pricelist_id = request.website.get_current_pricelist().id
		vals = {
				'partner_id': order.partner_id.id, 
				'pricelist_id': pricelist_id,
				'user_id': request.website.salesperson_id and request.website.salesperson_id.id,
				'team_id': request.website.salesteam_id and request.website.salesteam_id.id
			}    	
		sale_order_create = sale_order_obj.sudo().create(vals)
		for i in order.quote_lines:
			line_vals = {    
						'product_id': i.product_id.id, 
						'name': i.product_id.name,
						'product_uom_qty': i.qty, 
						'customer_lead':7, 
						'product_uom':i.product_id.uom_id.id,
						'order_id': sale_order_create.id  }
			sale_order_line_create = sale_order_line_obj.sudo().create(line_vals)
		
		order.sudo().unlink()
		request.session['quote_order_id'] = False
		return request.render("odoo_website_product_quote.quote_thankyou")

	@http.route(['/quote/delete/<model("quote.order.line"):line>'], type='http', auth="public", website=True)
	def qoute_delete(self, **post):
		cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
		order = post['line']
		
		order.sudo().unlink()
		return request.render("odoo_website_product_quote.quote_cart")	

	@http.route(['/thank_you'], type='http', auth="public", website=True)
	def thank_you(self, **post):
		cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
		return request.render("odoo_website_product_quote.quote_thankyou")	
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
