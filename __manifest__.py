# -*- coding: utf-8 -*-
{
    'name'     : 'InfoSaône - Epicerie Locavore des Bourroches',
    'version'  : '0.1',
    'author'   : 'InfoSaône',
    'category' : 'InfoSaône/iCom',


    'description': """
InfoSaône - Epicerie Locavore des Bourroches
===================================================
""",
    'maintainer' : 'InfoSaône',
    'website'    : 'http://www.infosaone.com',
    'depends'    : [
        'base',
        'stock',
        'sale',
        'point_of_sale',
        'pos_restaurant',
        'pos_reprint',
        'pos_discount',
        #'website_sale',
        'mail',
        'account',
        'account_accountant',
        'purchase',
        'board',
        'calendar',
        'pos_product_available',
    ],
    'data' : [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/pos_order_view.xml',
        'views/pos_session_view.xml',
        'views/partner_view.xml',
        'views/product_view.xml',
        'views/purchase_views.xml',
        'views/is_preparation_commande_view.xml',
        'views/is_imprime_etiquette_view.xml',
        'views/account_view.xml',
        'views/menu.xml',
        'report/layouts.xml',
        'report/purchase_order_templates.xml',
        'report/is_preparation_commande_report.xml',
        'report/is_imprime_etiquette_report.xml',
        'report/report_paperformat.xml',
        'report/report.xml',
    ],
    'installable': True,
    'application': True,
    'qweb': ['static/src/xml/pos.xml'],
}
