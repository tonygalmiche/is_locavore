# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PosOrder(models.Model):
    _inherit = "pos.order"


    @api.depends('date_order')
    def _compute(self):
        for obj in self:
            if obj.date_order:
                obj.is_annee = obj.date_order[:4]
                obj.is_mois  = obj.date_order[5:7]

    @api.depends('lines')
    def _compute_total(self):
        for obj in self:
            total=0
            for l in obj.lines:
                total=total+l.qty*l.price_unit
            obj.is_total=total


    is_annee     = fields.Char(string='Année de la commande', compute='_compute', readonly=True, store=True)
    is_mois      = fields.Char(string='Mois de la commande' , compute='_compute', readonly=True, store=True)
    is_total     = fields.Float(string='Total' , compute='_compute_total', readonly=True, store=True)



class PosOrderLine(models.Model):
    _inherit = "pos.order.line"


    order_id = fields.Many2one('pos.order', string='Les lignes', ondelete='cascade', index=True)
