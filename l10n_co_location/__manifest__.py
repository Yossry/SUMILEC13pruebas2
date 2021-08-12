# -*- coding: utf-8 -*-
{
    'name': "l10n_co_location",

    'summary': "Colombian info",

    'description': """
Este módulo carga:
- información geográfica de colombia (estados y ciudades).
Además, carga el código para cada ciudad y estado generado por el DANE.
- Bancos colombianos

""",
    'author': 'José Luis Vizcaya López',
    'company': 'José Luis Vizcaya López',
    'maintainer': 'José Luis Vizcaya López',
    'website': 'https://vizcaya.mi-erp.app',
    'category': 'res_partner',
    'version': '13.0.0.1.0',
    'depends': ['base', 'contacts'],
    'data': [
        'data/res.bank.csv',
        'data/res.country.state.csv',
        #'data/res.country.state.city.csv',
        'data/res_country_state_city_data.xml',
        'security/ir.model.access.csv',
        'views/partner_city_view.xml',
        'views/bank_city_view.xml',
        'views/res_country_state_city_view.xml',
        'views/company_city_view.xml',
        'views/res_country_state.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
