from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class Document(models.Model):
    _inherit = 'documents.document'

    first_creation = fields.Boolean('First Creation', default=True)

    def write(self,vals):

        if vals.get('attachment_name') and self.first_creation is True:
            vals['name'] = str(fields.Datetime.now() - relativedelta(hours=8)) + "." + vals.get('attachment_name').split(".")[-1]
            self.first_creation = False
        res = super().write(vals)
        
        return res

class WorkflowActionRulePayment(models.Model):
    _inherit = ['documents.workflow.rule']

    create_model = fields.Selection(selection_add=[('account.payment', "Create a Payment"),
                                                    ('account.move.in_receipt', "Vendor Receipt"),
                                                    ('account.move.out_receipt', "Customer Receipt")])

    def create_record(self, documents=None):
        rv = super(WorkflowActionRulePayment, self).create_record(documents=documents)
        if self.create_model == 'account.payment':
            document_msg = _('Payment created from document')
            new_obj = self.env[self.create_model].create({
                # 'name': " / ".join(documents.mapped('name')) or _("New payment from Documents"),
                #This causes the sequence validation error for some reason. Commenting out the name and letting Odoo set it
                'payment_type': 'inbound',
                'partner_id': documents.partner_id.id if len(documents.partner_id) == 1 else False,
                'journal_id': self.env['account.journal'].search([('name', '=', 'Cash')], limit=1).id
                # 'date': fields.Date.today(),

            })
            task_action = {
                'type': 'ir.actions.act_window',
                'res_model': self.create_model,
                'res_id': new_obj.id,
                'name': "new %s from %s" % (self.create_model, new_obj.name),
                'view_mode': 'form',
                'views': [(False, "form")],
                'context': self._context,
            }
            if len(documents) == 1:
                document_msg += f' {documents._get_html_link()}'
            else:
                document_msg += f's <ul>{"".join(f"<li>{document._get_html_link()}</li>" for document in documents)}</ul>'

            for document in documents:
                this_document = document
                if (document.res_model or document.res_id) and document.res_model != 'documents.document':
                    this_document = document.copy()
                    attachment_id_copy = document.attachment_id.with_context(no_document=True).copy()
                    this_document.write({'attachment_id': attachment_id_copy.id})

                # the 'no_document' key in the context indicates that this ir_attachment has already a
                # documents.document and a new document shouldn't be automatically generated.
                this_document.attachment_id.with_context(no_document=True).write({
                    'res_model': self.create_model,
                    'res_id': new_obj.id
                })
            new_obj.message_post(body=document_msg)
            return task_action
        return rv
