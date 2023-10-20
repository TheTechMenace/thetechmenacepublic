# -*- coding: utf-8 -*-
{
    'name': "Ryan's Workout Tracker",

    'summary': 
        """
        Tracker for Ryan's Workouts
        """,

    'description': 
        """
        Tracker for Ryan's Workouts
        """,

    'author': "Ryan",

    'category': 'Extra Tools',
    'version': '16.0.1.0.0',
    'license': 'AGPL-3', 

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/menu_items.xml',
        'views/views.xml',
        'wizard/wizard_views.xml',
        
    ],

}
