# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command
from odoo.tools import float_compare
from odoo.exceptions import UserError
from pprint import pprint

import logging
_logger = logging.getLogger(__name__)

class Assignment(models.Model):
    _name = 'classroom.assignment'
    _inherit = 'mail.thread'
    _description = "Assignments"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer("Assignment #", tracking=True)
    weighting = fields.Float(string="Assignment Weighting", tracking=True)
    total = fields.Float(string="Total", tracking=True)
    average = fields.Float(string="Assignment Average", compute='_compute_assignment_average')
    stored_average = fields.Float(string="Assignment Average", store=True)
    due_date = fields.Date(string="Due Date")
    grades_generated = fields.Boolean(copy=False)
    
    class_id = fields.Many2one(
        comodel_name="classroom.class",
        string="Class",
        copy=False
    )

    unit_id = fields.Many2one(
        comodel_name="classroom.unit",
        string="Unit"
    )
    

    grade_ids = fields.One2many(
        comodel_name="classroom.grade",
        inverse_name="assignment_id",
        string="Grades",
    )


    def _compute_assignment_average(self):
        for record in self:
            percentages = []
            for line in record.grade_ids:
                if line.grade_status not in ['not_submitted'] and not line.is_excused:
                    percentages.append(line.percent)

            if percentages:
                record.average = sum(percentages)/len(percentages)
                record.stored_average = record.average
            else:
                record.average = 0
                record.stored_average = record.average

    # @api.model
    # def create(self,vals):
    #     res = super(Assignment, self).create(vals)

    #     res.create_grades_from_assignment()
    #     return res

    def create_grades_from_assignment(self):
        for record in self:
            if not record.class_id:
                raise UserError("Class must be set to generate grades!")
            for student in record.class_id.student_ids:
                self.env['classroom.grade'].create({
                    'assignment_id': record.id,
                    'name': "%s - %s" %(record.class_id.name, record.name),
                    'student_id': student.id,
                    'total': record.total
                })
            record.grades_generated = True

    def update_average(self):
        records = self.env['classroom.assignment'].search([])
        for record in records:
            record.stored_average = record.average