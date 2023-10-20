from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    default_recurrence_stage_id = fields.Many2one('project.task.type',
                                                string='Default Recurrence Stage')
    default_shame_stage_id = fields.Many2one('project.task.type',
                                                string='Default Shame Stage')
    default_completed_stage_id = fields.Many2one('project.task.type',
                                                string='Default Completed Stage')
    is_automatic_cleanup_enabled = fields.Boolean("Automatic Task Cleanup?", default=False, copy=False)

    def end_of_day_cleanup(self):
        # raise UserError(self.ids)
        auto_cleanup_ids = self.search([('is_automatic_cleanup_enabled', '=', True)])
        # raise UserError(auto_cleanup_ids.ids)
        for record in auto_cleanup_ids:
            default_recurrence_stage_id = record.default_recurrence_stage_id.id
            default_shame_stage_id = record.default_shame_stage_id.id
            default_completed_stage_id = record.default_completed_stage_id.id

            tasks_in_to_do_ids = self.env['project.task'].search([('stage_id', '=', default_recurrence_stage_id), ('project_id', '=', record.id)])
            tasks_in_complete_ids = self.env['project.task'].search([('stage_id', '=', default_completed_stage_id), ('project_id', '=', record.id)])
            tasks_in_shame_ids = self.env['project.task'].search([('stage_id', '=', default_shame_stage_id), ('project_id', '=', record.id)])
            
            shame_tasks_ids = tasks_in_to_do_ids|tasks_in_shame_ids 
            for task in shame_tasks_ids:
                task.stage_id = default_shame_stage_id
                task.active = False

            for task in tasks_in_complete_ids:
                task.active = False

class ProjectTask(models.Model):
    _inherit = 'project.task'

    recurrence_time = fields.Selection(string="Recurrence Time", 
                                selection = [("morning", "Morning"),
                                                ("afternoon", "Afternoon"),
                                                ("evening", "Evening"), 
                                                ],store=True)
    
    is_recurrent_task_template = fields.Boolean(string="Recurrent Task Template", default=False,copy=False)

    @api.model
    def create(self, vals):
        res = super(ProjectTask, self).create(vals)

        if 'recurrence_time' in vals:
            res.recurrence_id.recurrence_time = vals['recurrence_time']
        return res

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)

        if 'recurrence_time' in vals:
            self.recurrence_id.recurrence_time = vals['recurrence_time']
        return res

class ProjectTaskRecurrence(models.Model):
    _inherit = 'project.task.recurrence'

    recurrence_time = fields.Selection(string="Recurrence Time", 
                                selection = [("morning", "Morning"),
                                                ("afternoon", "Afternoon"),
                                                ("evening", "Evening"), 
                                                ],store=True)

    def _compute_recurrence_time(self):
        for record in self:
            record.recurrence_time = record.task_ids[0].recurrence_time


#TODO ADD WITH CONTEXT FUNCTION CALL TO CREATE NEXT TASK TO ALLOW FOR PASSING THE LOOP COUNT TO
#DETERMINE THE OFFSET OF PLANNED DATE

    @api.model
    def _cron_create_recurring_tasks_morning(self):
        _logger.info("RUNNING MORNING TASK CREATION")
        if not self.env.user.has_group('project.group_project_recurring_tasks'):
            return
        today = fields.Date.today()
        recurring_today = self.search([('next_recurrence_date', '<=', today), ('recurrence_time', '=', 'morning')])
        recurring_today._create_next_task()
        for recurrence in recurring_today.filtered(lambda r: r.repeat_type == 'after'):
            recurrence.recurrence_left -= 1
        recurring_today._set_next_recurrence_date()

    @api.model
    def _cron_create_recurring_tasks_afternoon(self):
        _logger.info("RUNNING AFTERNOON TASK CREATION")
        if not self.env.user.has_group('project.group_project_recurring_tasks'):
            return
        today = fields.Date.today()
        recurring_today = self.search([('next_recurrence_date', '<=', today), ('recurrence_time', '=', 'afternoon')])
        recurring_today._create_next_task()
        for recurrence in recurring_today.filtered(lambda r: r.repeat_type == 'after'):
            recurrence.recurrence_left -= 1
        recurring_today._set_next_recurrence_date()

    @api.model
    def _cron_create_recurring_tasks_night(self):
        _logger.info("RUNNING EVENING TASK CREATION")
        if not self.env.user.has_group('project.group_project_recurring_tasks'):
            return
        today = fields.Date.today()
        recurring_today = self.search([('next_recurrence_date', '<=', today), ('recurrence_time', '=', 'evening')])

        recurring_today._create_next_task()
        for recurrence in recurring_today.filtered(lambda r: r.repeat_type == 'after'):
            recurrence.recurrence_left -= 1
        recurring_today._set_next_recurrence_date()


    def _create_next_task(self):
        for recurrence in self:
            #task_ids = []
            #TODO:
            #issue is happening where it looks like the template task is not changing, therefore the name is wrong
            # Need to do some debugging right here.
            task_ids = recurrence.sudo().task_ids
            template_task = task_ids.search([('is_recurrent_task_template','=',True)],limit=1)
            if not template_task:
                template_task = task_ids.sorted('create_date')[0]
            create_values = recurrence._new_task_values(template_task)
            new_task = self.env['project.task'].sudo().create(create_values)
            recurrence._create_subtasks(template_task, new_task, depth=3)


    def _new_task_values(self, task):
        res = super(ProjectTaskRecurrence, self)._new_task_values(task)
        name = res['name']
        res['name'] = "%s - %s" % (name, fields.Date.context_today(self.with_user(2)).strftime('%a, %b %d'))
        # raise UserError(res['name'])
        res['stage_id'] = task.project_id.default_recurrence_stage_id.id
        res['date_deadline'] = fields.Date.context_today(self.with_user(2))
        res['color'] = task.color

        return res

