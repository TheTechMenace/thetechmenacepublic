from odoo import models, fields, api
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    company_ids = fields.Many2many(string='Companies', comodel_name='res.company')
