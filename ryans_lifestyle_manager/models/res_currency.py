from odoo import models, fields, api


class Currency(models.Model):
    _inherit = "res.currency"

    rounding = fields.Float(string='Rounding Factor', digits=(12, 12), default=0.01,
        help='Amounts in this currency are rounded off to the nearest multiple of the rounding factor.')
    
    _sql_constraints = [
        ('unique_name', 'unique (name)', 'The currency code must be unique!'),
        ('rounding_gt_zero', 'CHECK (1=1)', 'No Error.')
    ]
