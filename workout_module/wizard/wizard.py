from odoo import api, fields, models, Command
import logging

_logger = logging.getLogger(__name__)

class WorkoutSessionWizard(models.TransientModel):
    _name = 'workout.session.wizard'
    _description = 'Wizard: Setup Workout Template'

    #Returning active_id
    def _default_session(self):
        return self.env['workout.session'].browse(self._context.get('active_id'))
    
    workout_template_ids = fields.Many2many('workout.event.template')
    
    def generate_workout(self):
        for record in self:
            for template in record.workout_template_ids:

                event_vals = \
                { 
                    'exerciser_id': template.exerciser_id.id,
                    'equipment_id': template.equipment_id.id,
                    'exercise_type_id': template.exercise_type_id.id, 
                    'session_id': self._default_session().id,
                }

                event_id = self.env['workout.event'].create(event_vals)

                computed_command_set_ids = [Command.create({
                        'event_id': event_id.id,
                        'set_count': set.set_count,
                        'reps_count': set.reps_count,
                        'weight': set.weight,
                        'is_done': set.is_done,
                    }) for set in template.set_ids
                    ]

                event_id.write({'set_ids':computed_command_set_ids})


            action = self.env["ir.actions.actions"]._for_xml_id("workout_module.action_workout_sets")

            return action
