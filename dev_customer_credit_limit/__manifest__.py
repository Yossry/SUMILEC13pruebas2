# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Customer Credit Limit',
    'version': '13.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Accounting',
    'description':
        """
odoo Apps will check the Customer Credit Limit on Sale order and notify to the sales manager,
        
        Customer Credit Limit, Partner Credit Limit, Credit Limit, Sale limit, Customer Credit balance, Customer credit management, Sale credit approval , Sale customer credit approval, Sale Customer Credit Informatation, Credit approval, sale approval, credit workflow , customer credit workflow,
    Customer credit limit
    Customer credit limit warning
    Check customer credit limit
    Configure customer credit limit
    How can set the customer credit limit
    How can set the customer credit limit on odoo
    How can set the customer credit limit in odoo
    Use of customer credit limit on sale order
    Change customer credit limit
    Use of customer credit limit on customer invoice
    Customer credit limit usages
    Use of customer credit limit
    Set the customer credit limit in odoo
    Set the customer credit limit with odoo
    Set the customer credit limit
    Customer credit limit odoo module
    Customer credit limit odoo app
    Customer credit limit email
    Set credit limit for customers
    Warning message to customer on crossing credit Limit
    Auto-generated email to Administrator on cutomer crossing credit limit.
    Credit limit on customer
    Credit limit for customer
    Customer credit limit setup        
Odoo Customer Credit Limit 
Manage Customer credit 
Odoo Manage Customer Credit 
Customer credit limit
Customer credit limit warning
Check customer credit limit
Configure customer credit limit
How can set the customer credit limit
How can set the customer credit limit on odoo
How can set the customer credit limit in odoo
Use of customer credit limit on sale order
Change customer credit limit
Use of customer credit limit on customer invoice
Customer credit limit usages
Use of customer credit limit
Set the customer credit limit in odoo
Set the customer credit limit with odoo
Set the customer credit limit
Customer credit limit odoo module
Customer credit limit odoo app
Customer credit limit email
Set credit limit for customers
Warning message to customer on crossing credit Limit
Auto-generated email to Administrator on cutomer crossing credit limit.
Credit limit on customer
Credit limit for customer
Customer credit limit setup
Odoo admin cans set customer limit to any customer from odoo customer screen
Alert Sales Person when customer credit limit will be exceeded
Odoo Alert Sales Person when customer credit limit will be exceeded
Exceeded credit limit window will show the sum of total outstanding Invoices from previous orders and total bill amount of the current sale quotation being placed for the customer
Odoo Exceeded credit limit window will show the sum of total outstanding Invoices from previous orders and total bill amount of the current sale quotation being placed for the customer
Quick allow to set customer on credit limit on hold
Odoo Quick allow to set customer on credit limit on hold 
Sales Manager/ Credit manager will notify by mail when customer sale order goes into credit limit
Odoo Sales Manager/ Credit manager will notify by mail when customer sale order goes into credit limit
Separate Menu to see all credit sale orders
Odoo Separate Menu to see all credit sale orders
Alert when selecting customer already on credit limit on hold
Odoo Alert when selecting customer already on credit limit on hold
Customer Credit Limit 
Odoo Customer Credit Limit 
Customer Credit limit manage 
Odoo customer credit limit Manage 
Credit sale Order 
Odoo Credit sale Order



    """,
    'summary': 'odoo Apps will check the Customer Credit Limit on Sale order and notify to the sales manager',
    'author': 'Devintelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',
    'images': ['images/main_screenshot.png'],
    'depends': ['sale_management', 'account'],
    'data': [
        'security/security.xml',
        'wizard/customer_limit_wizard_view.xml',
        'views/partner_view.xml',
        'views/sale_order_view.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price':35,
    'currency':'EUR',
    'live_test_url':'https://youtu.be/CC-a6QQcxMc',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
