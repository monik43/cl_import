# -*- coding: utf-8 -*-
{
    'name': "Importar XLS",

    'summary': """
        Módulo para importar archivos XLSX.""",

    'description': """
        Localizado dentro del formulario de stock picking, el objetivo de este módulo es agilizar el proceso de entrada de equipos al sistema.
    """,

    'author': "Cloudalia Educacion",
    'website': "https://cloudaliaeducacion.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchases',
    'version': '11.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        'wizard/view_import_file.xml',
        'views/cl_import_views.xml',
    ],
}