# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command
from odoo.tools import float_compare
from odoo.exceptions import UserError
from pprint import pprint

import logging
_logger = logging.getLogger(__name__)

class Class(models.Model):
    _name = 'classroom.class'
    _inherit = 'mail.thread'
    _description = "Classes"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    teacher_id = fields.Many2one('res.partner', string='Teacher')
    average = fields.Float(string="Class Average", compute='_compute_class_average') 
    stored_average = fields.Float(string="Class Average", store=True)

    
    colour = fields.Integer(string="Colour")

    student_ids = fields.One2many(string='Students', comodel_name='classroom.student', inverse_name='class_id')

    def _compute_class_average(self):
        for record in self:
            percentages = []
            for grade in record.student_ids:
                if grade.average != 0:
                    percentages.append(grade.average) 

            if percentages:
                record.average = sum(percentages)/len(percentages)
                record.stored_average = record.average
            else:
                record.average = 0
                record.stored_average = record.average