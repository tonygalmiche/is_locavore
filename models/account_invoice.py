# -*- coding: utf-8 -*-
from openerp import models, fields

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_export_id = fields.Many2one('is.export.compta', string='Export Compta')
