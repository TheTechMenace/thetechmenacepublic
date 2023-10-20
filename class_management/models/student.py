# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command
from odoo.tools import float_compare
from odoo.exceptions import UserError, ValidationError
from pprint import pprint

import logging
_logger = logging.getLogger(__name__)

class Student(models.Model):
    _name = 'classroom.student'
    _inherit = 'mail.thread'
    _order = "name"
    _description = "Students"

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    average = fields.Float(string="Student Average", compute='_compute_student_average') 
    stored_average = fields.Float(string="Student Average", store=True)



    grade_ids = fields.One2many(
        comodel_name="classroom.grade",
        inverse_name="student_id",
        string="Grades",
    )

    class_id = fields.Many2one(
        comodel_name="classroom.class",
        string="Class",
    )

    def _compute_student_average(self):
        for record in self:
            percentages = []
            weighting = []
            for grade in record.grade_ids:
                if grade.grade_status not in ['not_submitted'] and not grade.is_excused:
                    percentages.append(grade.percent)
                    weighting.append(grade.weighting)

            if percentages and weighting:
                if len(percentages) == len(weighting):
                    record.average = sum(x*y for x, y in list(zip(percentages, weighting))) / sum(weighting)
                    record.stored_average = record.average
                else:
                    record.average = 0 
                    record.stored_average = record.average

            else:
                record.average = 0
                record.stored_average = record.average