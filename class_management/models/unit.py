# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command
from odoo.tools import float_compare
from odoo.exceptions import UserError
from pprint import pprint

import logging
_logger = logging.getLogger(__name__)

class Unit(models.Model):
    _name = 'classroom.unit'
    _description = "Units"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer("Unit #", tracking=True)
    # total = fields.Float(string="Total", tracking=True)
    # average = fields.Float(string="Unit Average", compute='_compute_unit_average')
    # stored_average = fields.Float(string="Unit Average", store=True)
    date_unit_start = fields.Date(string="Unit Start Date")
    date_unit_end = fields.Date(string="Unit End Date")


    grade_ids = fields.One2many(
        comodel_name="classroom.grade",
        inverse_name="assignment_id",
        string="Grades",
    )


    # def _compute_unit_average(self):
    #     for record in self:
    #         percentages = []
    #         for line in record.grade_ids:
    #             if line.grade_status not in ['not_submitted'] and not line.is_excused:
    #                 percentages.append(line.percent)

    #         if percentages:
    #             record.average = sum(percentages)/len(percentages)
    #             record.stored_average = record.average
    #         else:
    #             record.average = 0
    #             record.stored_average = record.average

    # @api.model
    # def create(self,vals):
    #     res = super(Assignment, self).create(vals)

    #     res.create_grades_from_assignment()
    #     return res


    # def update_average(self):
    #     records = self.env['classroom.assignment'].search([])
    #     for record in records:
    #         record.stored_average = record.average