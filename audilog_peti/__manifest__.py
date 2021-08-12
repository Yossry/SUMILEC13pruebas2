# -*- coding: utf-8 -*-
{
    'name': "audilog_peti",

    'summary': """
        Agregar campos de creacion y actualizacion en el cliente""",

    'description': """
        Se visualizan campos de creacion, actualizacion en el clientes y tambien desde el POS
    """,

    'author': "PETI Soluciones Prodcutivas",
    'website': "http://www.peti.com.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [],

    # always loaded
    'data': [
        'views/assets.xml',
        'views/views.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml'
    ],

}
