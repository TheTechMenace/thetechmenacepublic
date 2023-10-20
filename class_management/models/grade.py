# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command
from odoo.tools import float_compare
from odoo.exceptions import UserError, ValidationError
from pprint import pprint

import logging
_logger = logging.getLogger(__name__)

class Grade(models.Model):
    _name = 'classroom.grade'
    _inherit = 'mail.thread'
    _order = "student_id"
    _description = "Grades"

    name = fields.Char()
    active = fields.Boolean(default=True)
    assignment_id = fields.Many2one('classroom.assignment', string='Assignment', ondelete='cascade')
    unit_id = fields.Many2one(string="Unit", related='assignment_id.unit_id')
    due_date = fields.Date(string="Due Date", related='assignment_id.due_date', store=True )
    student_id = fields.Many2one('classroom.student', string='Student', ondelete='cascade')
    
    score = fields.Float(string="Score", tracking=True)
    total = fields.Float(string="Total", related='assignment_id.total', readonly=True)
    weighting = fields.Float(string="Weighting", related='assignment_id.weighting', readonly=True)
    percent = fields.Float(string="Percent", compute='_compute_percentage')

    grade_status = fields.Selection(string="Grade Status", 
                                    selection = [("not_submitted", "Not Submitted"),
                                                 ("not_graded", "Not Graded"),
                                                 ("graded", "Graded"), 
                                                 ("returned", "Returned"),
                                                 ],default='not_submitted')

    is_excused = fields.Boolean(string="Excused?", copy=False)


    @api.onchange('score','total')
    def _compute_percentage(self):
        for record in self:
            if record.total == 0:
                record.percent = 0
            else:    
                record.percent = record.score / record.total


    @api.constrains('score','total')
    def _check_score_and_total(self):
        for record in self:
            if record.score < 0 or record.total < 0:
                raise ValidationError("You cannot have negative numbers as a score or total!")

    # def _compute_name(self):
    #     for record in self:
    #         if record.assignment_id:
    #             record.name = record.assignment_id.name
    #         else:
    #             record.name = "NA"

    # @api.onchange('score')
    # def _update_grade_status(self):
    #     for record in self:
    #         record.grade_status = 'graded'
    @api.model
    def create(self,vals):
        res = super(Grade, self).create(vals)
        if res.assignment_id and res.student_id:
            res.name = "%s - %s" %(res.student_id.class_id.name, res.assignment_id.name)
        else:
            res.name = "NA"
        if 'score' in vals:
            vals['grade_status'] = 'graded'

        


    def write(self,vals):
        if 'score' in vals:
            vals['grade_status'] = 'graded'

        # if ['class_id', 'assignment_id'] in vals:
        #     self.name = "%s - %s" %(self.class_id.name, self.assignment_id.name)

        return super(Grade, self).write(vals)
