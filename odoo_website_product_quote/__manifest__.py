# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Website Get Quote Odoo Shop',
    'version': '12.0.1.4',
    'license':'OPL-1',
    'category': 'eCommerce',
    'summary': 'This apps helps to request a quote from Website by Customer/Visitor',
    "description": """
    Purpose :- 
    Odoo Website Product Quote.
    website request quote
    website product request
    website Request for quotation
    website ask for quote
    website request a quote
    Odoo website Quote, Website product quote request, Website quote request
    Website quotation request, website product quotation request, website get quote

    Odoo shop Product Quote.
    Odoo shop Quote, shop product quote request, shop quote request
    shop quotation request, shop product quotation request, shop get quote
    Ecommerce quote request, Ecommerce product quote request, Ecommerce quotation request, Ecommerce product quotation request, Ecommerce get quote
    """,
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    "price": 19,
    "currency": 'EUR',
    'images': [],
    'depends': ['website','website_sale','sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/product_view.xml',
        'views/templates.xml',
    ],
   'qweb': [
                
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/BPhYVkMcdJY',
    "images":["static/description/Banner.png"],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
