# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError, ValidationError
from pprint import pprint

import logging
_logger = logging.getLogger(__name__)


class MrpWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    #this is all still a WIP

    display_name = fields.Char(compute='_compute_display_name')
    name = fields.Selection(required=False, selection = [("both", "Both"),
                                                 ("ryan", "Ryan"),
                                                 ("haley", "Haley")
                                                 ],default='both')
    workcenter_id = fields.Many2one(required=False, group_expand='_read_group_workcenter_id',)
    

    @api.model
    def _read_group_workcenter_id(self, stages, domain, order):
        return self.env['mrp.workcenter'].search([])
    

    def _compute_display_name(self):
        for record in self:
            record.display_name = "%s - %s" % (record.production_id.product_id.name, record.name)
