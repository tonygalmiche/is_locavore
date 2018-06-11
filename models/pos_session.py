# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = "pos.session"


    @api.multi
    def action_ecriture_comptables(self):
        for obj in self:
            orders=self.env['pos.order'].search([('session_id','=',obj.id)])
            moves=[]
            statements=[]
            for order in orders:
                if order.account_move.id not in moves:
                    moves.append(order.account_move.id)
                    for statement in order.session_id.statement_ids:
                        if statement.id not in statements:
                            statements.append(statement.id)
            return {
                'name': u'Sessions',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move.line',
                'type': 'ir.actions.act_window',
                'domain': [
                    '|',('move_id','in',moves),('statement_id','in',statements),
                ],
                'context': {'search_default_group_by_account':1},
            }

