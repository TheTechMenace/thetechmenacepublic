# -*- coding: utf-8 -*-

from odoo import models, fields, api

from pprint import pprint
from datetime import datetime

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_exerciser = fields.Boolean("Exerciser?")

class Sessions(models.Model):
    _name = 'workout.session'
    _description = 'Session'
    _inherit = 'mail.thread'
    _rec_name = 'date'

    date = fields.Date(string="Date", required=True, default=lambda self: fields.Date.context_today(self))
    start_time = fields.Datetime(string="Start Time", required=True, default=lambda self: fields.Datetime.now().replace(second=0))
    end_time = fields.Datetime(string="End Time")
    event_ids = fields.One2many('workout.event', 'session_id', "Exercises")

    def generate_workout(self):
        return self.env.ref('workout_module.launch_workout_session_template_wizard').read()[0]

class Event(models.Model):
    _name = 'workout.event'
    _description = 'Event'
    _rec_name = 'display_name'
    _inherit = 'mail.thread'

    display_name = fields.Char(compute='_compute_display_name')

    sequence = fields.Integer()
    exerciser_id = fields.Many2one("res.partner", "Exerciser", required=True, domain="[('is_exerciser', '=', True)]")
    equipment_id = fields.Many2one('workout.equipment', "Equipment Name", required=True)
    exercise_type_id = fields.Many2one('workout.exercise.type', "Exercise Type", required=True)
    
    #TODO: logic for when a new event is created on the fly not from a template will need
    #to find a way to autoset the session
    session_id = fields.Many2one('workout.session', "Session", ondelete='cascade')
    set_ids = fields.One2many('workout.set', 'event_id', "Sets")

    def _compute_display_name(self):
        for record in self:
            record.display_name = "%s - %s" %(record.equipment_id.name, record.exercise_type_id.name)

class ExerciseType(models.Model):
    _name = 'workout.exercise.type'
    _description = 'Exercise Type'
    _inherit = 'mail.thread'

    sequence = fields.Integer()
    name = fields.Char("Exercise Type")

class Set(models.Model):
    _name = 'workout.set'
    _description = 'Equipment'
    _rec_name = 'event_id'
    _inherit = 'mail.thread'

    event_id = fields.Many2one('workout.event', "Event", ondelete='cascade')
    session_id = fields.Many2one('workout.session', related='event_id.session_id', store=True)
    session_date = fields.Date(related='session_id.date', store=True)

    set_count = fields.Integer("Set #", required=True)
    reps_count = fields.Integer("Reps", required=True)
    weight = fields.Float("Weight(lbs)")
    is_done = fields.Boolean("Done?")


class MuscleGroup(models.Model):
    _name = 'workout.musclegroup'
    _description = 'Muscle Group'

    sequence = fields.Integer()
    name = fields.Char("Muscle Group")
    # body_part = fields.Selection([
	# 	('arms', 'Arms'),
	# 	('chest', 'Chest'),
	# 	('shoulders', 'Shoulders'),
	# 	('back', 'Back'),
	# 	('legs', 'Legs'),
	# 	('abs', 'Abs'),
	# 	('cardio', 'Cardio'),
    #     ('other', 'Other'),
    #     ('na', 'N/A')
	# ], string="Muscle Focus", tracking=True, required=True)

class Equipment(models.Model):
    _name = 'workout.equipment'
    _description = 'Equipment'
    _inherit = 'mail.thread'

    name = fields.Char("Equipment Name", required=True)
    sequence = fields.Integer()

    # body_part = fields.Selection([
    #     ('arms', 'Arms'),
    #     ('chest', 'Chest'),
    #     ('shoulders', 'Shoulders'),
    #     ('back', 'Back'),
    #     ('legs', 'Legs'),
    #     ('abs', 'Abs'),
    #     ('cardio', 'Cardio'),
    #     ('na', 'N/A')
    # ], string="Body Part", tracking=True, required=True)

    muscle_group_target_ids = fields.Many2many('workout.musclegroup', string="Muscle Group Target")

    equipment_adjustment_ids = fields.One2many('workout.equipment.adjustment', 'equipment_id', "Adjustments")


class EquipmentAdjustment(models.Model):
    _name = 'workout.equipment.adjustment'
    _description = 'Equipment Adjustment'
    _rec_name = 'exerciser_id'
    _inherit = 'mail.thread'

    exerciser_id = fields.Many2one("res.partner", "Exerciser", required=True, domain="[('is_exerciser', '=', True)]")
    equipment_id = fields.Many2one('workout.equipment', "Equipment Name")


    adjustment_1 = fields.Char("Adjustment 1")
    adjustment_2 = fields.Char("Adjustment 2")
    adjustment_3 = fields.Char("Adjustment 3")

class EventTemplate(models.Model):
    _name = 'workout.event.template'
    _description = 'Event Template'
    _rec_name = 'equipment_id'
    _inherit = 'mail.thread'

    sequence = fields.Integer()
    exerciser_id = fields.Many2one("res.partner", "Exerciser", required=True, domain="[('is_exerciser', '=', True)]")
    equipment_id = fields.Many2one('workout.equipment', "Equipment Name")
    exercise_type_id = fields.Many2one('workout.exercise.type', "Exercise Type")
        
    set_ids = fields.One2many('workout.set.template', 'template_id', "Sets")


class SetTemplate(models.Model):
    _name = 'workout.set.template'
    _description = 'Set Template'
    
    template_id = fields.Many2one('workout.event.template', "Template", ondelete='cascade')

    set_count = fields.Integer("Set #", required=True)
    reps_count = fields.Integer("Reps", required=True)
    weight = fields.Float("Weight(lbs)")
    is_done = fields.Boolean("Done?")