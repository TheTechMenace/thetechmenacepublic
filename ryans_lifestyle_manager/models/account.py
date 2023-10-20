# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command
from odoo.tools import float_compare
from odoo.exceptions import UserError, ValidationError
from pprint import pprint

from dateutil.relativedelta import relativedelta
from datetime import datetime
import calendar

import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    ref = fields.Char(copy=True)
    extra_info = fields.Char(string="Extra Info")

    #This method will get executed when we click on Create Subscription Bills Server Action and will create 11 vendor bills
    def action_create_subscription_bills(self):
        references = []
        if not self.move_type == 'in_invoice':
            raise ValidationError("This action isn't available for this document.")
        for record in self:
            if record.invoice_line_ids:
                account_move_line_ids = record.invoice_line_ids[0]
            else:
                raise ValidationError("You must have at least one line item in the bill.")
            date = record.date
            label = account_move_line_ids.name + " - " if account_move_line_ids.name else ""
            extra = " - " + record.extra_info if record.extra_info else ""
            record.ref = f'{label}{date.strftime("%B")}{extra}'
            references.append(record.ref)
            for _ in range(11):
                date += relativedelta(months=1)
                reference = f'{label}{date.strftime("%B")}{extra}'     
                references.append(reference)
                record.copy(default = {'ref': reference,
                                       'date': date,
                                       'invoice_date': date,
                                       'auto_post': 'at_date'})

        return {
            'name': 'Bills',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [
                ('ref', 'in', references),
                ('move_type', '=', 'in_invoice')
            ]
        }

    @api.depends('invoice_date', 'company_id')
    def _compute_date(self):
        for record in self:
            record.date = record.invoice_date

    @api.model
    def default_get(self,fields_list):
        res = super(AccountMove, self).default_get(fields_list)
        res.update({'date': fields.Date.context_today(self)})
            
        return res

    
    def action_post(self):
        #deprecated, no longer useful
        # if self.invoice_line_ids:
        #     for line in self.invoice_line_ids.filtered(lambda l: l.display_type == False):
        #         if not line.analytic_distribution:
        #             if not line.account_id.is_excluded_from_tag_check:
        #                 raise UserError(_('You must enter an analytic tag or account on every line item!'))

        if self.move_type in ['in_receipt', 'in_invoice']:
            if not self.invoice_date:
                self.invoice_date = self.date
        return super().action_post()

    def _copy_recurring_entries(self):
        ''' Creates a copy of a recurring (periodic) entry and adjusts its dates for the next period.
        Meant to be called right after posting a periodic entry.
        Copies extra fields as defined by _get_fields_to_copy_recurring_entries().
        '''
        for record in self:
            record.auto_post_origin_id = record.auto_post_origin_id or record  # original entry references itself
            next_date = self._apply_delta_recurring_entries(record.date, record.auto_post_origin_id.date, record.auto_post)

            existing_record = self.search([('date', '=', next_date )], limit=1)

            if existing_record:
                return

            if not record.auto_post_until or next_date <= record.auto_post_until:  # recurrence continues
                record.copy(default=record._get_fields_to_copy_recurring_entries({'date': next_date}))

    def copy_recurring_entries(self):
        ''' Creates a copy of a recurring (periodic) entry and adjusts its dates for the next period.
        Meant to be called right after posting a periodic entry.
        Copies extra fields as defined by _get_fields_to_copy_recurring_entries().
        '''
        for record in self:
            record._copy_recurring_entries()

    def duplicate_last_line(self):
        for record in self:
            if record.invoice_line_ids:
                line = record.invoice_line_ids.sorted('sequence')[-1]
            else:
                return


            record.write({
                'invoice_line_ids':[Command.create({
                'move_id': self.id,
                'quantity': line.quantity,
                'product_id': line.product_id.id,
                'name': line.name,
                'account_id': line.account_id.id,
                'analytic_distribution': line.analytic_distribution if line.analytic_distribution else False,
                'price_unit': line.price_unit,
                'sequence': line.sequence + 1,
                'product_uom_id': line.product_uom_id.id
                })

                ]})

    # def action_register_payment(self):
    #     if len(self) == 1:
    #         if self._context.get('default_move_type') in ['in_invoice', 'in_receipt']:
    #             self._context.pop('default_payment_date')
    #             print("VENDOR BILL")
    #             print(self._context)
    #             #cant do this as this is a frozen dict, cant be changed
    #     return super().action_register_payment()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def default_get(self, fields):
        res = super(AccountMoveLine, self).default_get(fields)
        if self.move_id.move_type in ['out_invoice','out_receipt']:
            # raise UserError(('%s') %(res))
            res.update({'account_id': self.env['account.account'].search([('id', '=', '205')], limit=1).id})
            #raise UserError(('tried to change default account %s %s') %(res.get('account_id', 'NOTHING'), res))
            #raise UserError(('The account %s (%s) is deprecated. line:%s') % (account.name, account.code, line))
        #id 205 is the receivable account. Keeps defaulting to other accounts (deprecated GST for example) despite the fact that it
        # is set everywhere else. Not sure why

        elif self.move_id.move_type in ['in_invoice','in_receipt']:
            res.update({'account_id': self.env['account.account'].search([('id', '=', '234')], limit=1).id })
        #id 234 is the payable account. Keeps defaulting to other accounts (deprecated GST for example) despite the fact that it
        # is set everywhere else. Not sure why
            
        return res

    @api.constrains('account_id', 'journal_id')
    def _check_constrains_account_id_journal_id(self):
        for line in self.filtered(lambda x: x.display_type not in ('line_section', 'line_note')):
            account = line.account_id
            journal = line.move_id.journal_id


            if account.deprecated:
                _logger.error(('The account %s (%s) is deprecated. line:%s') % (account.name, account.code, line))
                #raise UserError(_('The account %s (%s) is deprecated.') % (account.name, account.code))

            account_currency = account.currency_id
            if account_currency and account_currency != line.company_currency_id and account_currency != line.currency_id:
                raise UserError(_('The account selected on your journal entry forces to provide a secondary currency. You should remove the secondary currency on the account.'))

            if account.allowed_journal_ids and journal not in account.allowed_journal_ids:
                raise UserError(_('You cannot use this account (%s) in this journal, check the field \'Allowed Journals\' on the related account.', account.display_name))

            if account in (journal.default_account_id, journal.suspense_account_id):
                continue

            is_account_control_ok = not journal.account_control_ids or account in journal.account_control_ids

            if not is_account_control_ok:
                raise UserError(_("You cannot use this account (%s) in this journal, check the section 'Control-Access' under "
                                  "tab 'Advanced Settings' on the related journal.", account.display_name))


    @api.constrains('account_id', 'display_type')
    def _check_payable_receivable(self):
        for line in self:
            account_type = line.account_id.account_type
            if line.move_id.is_sale_document(include_receipts=True):
                if (line.display_type == 'payment_term') ^ (account_type == 'asset_receivable'):
                    _logger.error("Any journal item on a receivable account must have a due date and vice versa.")
                    #raise UserError(_("Any journal item on a receivable account must have a due date and vice versa."))
            if line.move_id.is_purchase_document(include_receipts=True):
                if (line.display_type == 'payment_term') ^ (account_type == 'liability_payable'):
                    _logger.error("Any journal item on a payable account must have a due date and vice versa.")
                    #raise UserError(_("Any journal item on a payable account must have a due date and vice versa."))
class AccountAccount(models.Model):
    _inherit = 'account.account'
    is_excluded_from_tag_check = fields.Boolean("Excluded From Tag Check?")

class AccountAccount(models.Model):
    _inherit = 'account.analytic.account'

    def name_get(self):
        res = []
        for analytic in self:
            name = analytic.name
            # removed so that the full name doesnt show up on the invoice line

            # if analytic.code:
            #     name = '[' + analytic.code + '] ' + name
            # if analytic.partner_id.commercial_partner_id.name:
            #     name = name + ' - ' + analytic.partner_id.commercial_partner_id.name
            res.append((analytic.id, name))
        return res


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    is_invoiced = fields.Boolean("Is Invoiced?")

    @api.model
    def create(self, vals):
        record = super(AccountAnalyticLine,self).create(vals)

        if record.amount > 0:
            record.is_invoiced = True
        else:
            record.is_invoiced = False
        return record
            
    def create_so_from_analytic_lines(self):
        payment_term_id = self.env['account.payment.term'].search([('name', '=', 'End of This Month')], limit=1)
        repayment_account_id = self.env['account.account'].search([('code', '=', '4998')], limit=1) #get repayment income account
        for record in self:
            partner_id = record.account_id.partner_id.id
            break
        ctx = {'default_move_type': 'out_invoice'}
        invoice_id = self.env['account.move'].with_context(ctx).create({
            'move_type':'out_invoice',
            'invoice_date': fields.Date.today(),
            'partner_id': partner_id,
            'invoice_date_due': fields.Date.today(),
            'invoice_payment_term_id': payment_term_id.id,
            
            })
        already_invoiced_ids = []
        positive_amount_ids = []
        for record in self:
            if record.is_invoiced:
                already_invoiced_ids.append([record.name, record.amount])
                continue
            if record.amount > 0:
                _logger.info(record.amount)
                positive_amount_ids.append([record.name, record.amount])
                
            line_vals = {
            'move_id': invoice_id.id,
            'product_id': record.product_id.id,
            'name': "%s - %s" %(record.partner_id.name, record.name),
            'quantity': record.unit_amount,
            'account_id': repayment_account_id.id or self.env['account.account'].search([('name', 'ilike', 'income')], limit=1).id, #get repayment income account or a default income account
            'analytic_distribution': {record.account_id.id: 100},
            'price_unit': -record.amount / record.unit_amount if record.unit_amount != 0 else 0
            }
        
            invoice_id.write({'invoice_line_ids':[Command.create(line_vals)]})
            record['is_invoiced'] = True
        if already_invoiced_ids:
            raise UserError("Already invoiced on lines: (%s). Please remove and try again." %(already_invoiced_ids))

        # if positive_amount_ids:
            #DOESNT WORK HERE
            # raise UserError('error!!')
            # created_popup = self.env['custom.popup.warning'].create({'title':'WOW DUDE SLOW DOWN!','description':'Life goes on ..'})
            # return {
            #     'name': _('Somethink Went Wrong'),
            #     'type': 'ir.actions.act_window',
            #     'view_mode': 'form',
            #     'res_model': 'custom.popup.warning',
            #     'res_id': created_popup,
            #     'target': 'new'
            # }

class CrossoveredBudget(models.Model):
    _inherit = "crossovered.budget"

    #This method will get executed when we click on Create Monthly Budgets Server Action and will create 11 Monthly Budgets
    def action_create_monthly_budgets(self):
        budget_ids = []
        for record in self:
            from_date = record.date_from
            to_date = record.date_to

            if not from_date or not to_date:
                raise ValidationError("You must enter from date and to date in the period field.")
            
            if not record.crossovered_budget_line:
                raise ValidationError("You must have at least one line item in the budget lines.")
                
            first_day, last_day = calendar.monthrange(from_date.year, from_date.month)
            if from_date.year != to_date.year or from_date.month != to_date.month or from_date.day != first_day or to_date.day != last_day:
                raise ValidationError("You must enter the first and last date of the same month and year. Example - 08/01/2023 to 08/31/2023.")
            
            record.name = f'{from_date.strftime("%B")} Budget'
            budget_ids.append(record.id)
            for _ in range(11):
                from_date += relativedelta(months=1)
                to_date += relativedelta(months=1)
                new_from_date, new_to_date = record.get_first_last_date_of_month(from_date.year, from_date.month)
                name = f'{from_date.strftime("%B")} Budget' 
                
                duplicate_record = record.copy(default = {'name': name})
                duplicate_record.write({'date_from': new_from_date, 'date_to': new_to_date})
                for line in duplicate_record.crossovered_budget_line:
                    line.write({'date_from': new_from_date, 'date_to': new_to_date})
                budget_ids.append(duplicate_record.id)

        return {
            'name': 'Budgets',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'crossovered.budget',
            'domain': [
                ('id', 'in', budget_ids),
            ]
        }

    def get_first_last_date_of_month(self, year, month):
        _, last_day = calendar.monthrange(year, month)
        first_date = datetime(year, month, 1)
        last_date = datetime(year, month, last_day)
        return first_date.date(), last_date.date()