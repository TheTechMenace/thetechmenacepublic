
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def action_onhand_qty(self):

        #company_ids = self.env['res.company'].search([]).ids

        action = self.env['stock.quant'].with_context(
            search_default_internal_loc=1,
            #search_default_productgroup=1,
            #search_default_locationgroup=1,
            #allowed_company_ids = company_ids,
        ).action_view_quants()
        # action['domain'] = [('product_id', '=', self.product_id.id)]

        # pprint(action)
        return action
