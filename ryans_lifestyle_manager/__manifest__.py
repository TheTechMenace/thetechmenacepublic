# -*- coding: utf-8 -*-
{
    'name': "Lifestyle Manager",

    'summary': 
        """
        Main module for Lifestyle Manager
        """,

    'description': 
        """
        Main module for Lifestyle Manager
        """,

    'author': "Ryan",

    'category': 'Extra Tools',
    'version': '16.0.1.0.3',
    'license': 'AGPL-3', 

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail','account', 'account_budget', 'mrp', 'sale', 'stock', 'product', 'documents'],

    # always loaded
    'data': [
        # 'data/preset_data.xml',
        'data/record_rules.xml',
        'data/server_actions.xml',
        'security/ir.model.access.csv',

        # 'report/report.xml',
        
        'views/views.xml',
        
    ],

    'application': True

}

