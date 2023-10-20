# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command
from odoo.tools import float_compare
from odoo.exceptions import UserError, ValidationError
from pprint import pprint

import logging
_logger = logging.getLogger(__name__)

class IrModelField(models.Model):
    _inherit = 'ir.model.fields'
    
    def _reflect_field_params(self, field, model_id):
        """ Tracking value can be either a boolean enabling tracking mechanism
        on field, either an integer giving the sequence. Default sequence is
        set to 100. """
        vals = super(IrModelField, self)._reflect_field_params(field, model_id)
        tracking = getattr(field, 'tracking', None)
        _logger.info("tracking: (%s)" %(tracking))
        
        if tracking is True:
            tracking = 100
            _logger.info("tracking TRUE: (%s, %s)" %(tracking, field.name))
        elif tracking is False:
            tracking = 0
            _logger.info("tracking FALSE: (%s, %s)" %(tracking, field.name))
        elif tracking is None:
            tracking = 100
            _logger.info("tracking NONE: (%s, %s)" %(tracking, field.name))
        vals['tracking'] = tracking
        return vals