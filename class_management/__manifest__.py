# -*- coding: utf-8 -*-
{
    'name': "Classroom Management",

    'summary': 
        """
        Main module for Classroom Management
        """,

    'description': 
        """
        Main module for Classroom Management
        """,

    'author': "Ryan",

    'category': 'Extra Tools',
    'version': '16.0.1.0.0',
    'license': 'AGPL-3', 

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],



    # always loaded
    'data': [
        # 'data/preset_data.xml',
        # 'data/record_rules.xml',
        # 'data/server_actions.xml',
        'security/ir.model.access.csv',

        # 'report/report.xml',
        'views/views.xml',
        'views/menu_items.xml',
    ],


        
    'application': True

}

