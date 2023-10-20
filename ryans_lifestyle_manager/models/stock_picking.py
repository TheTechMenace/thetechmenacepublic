from odoo import models, fields, api
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"


    def set_done_with_fee(self):
        DISCOUNT_RATE = 0.998
        for record in self:
            if record.state not in ['done', 'cancel']:
                #if record.picking_type_code
                for line in record.move_ids_without_package:
                    line.quantity_done = line.product_uom_qty * DISCOUNT_RATE
            else:
                raise UserError('State must not be in Done or Cancelled!')
