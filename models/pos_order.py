# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PosOrder(models.Model):
    _inherit = "pos.order"


    @api.depends('date_order')
    def _compute(self):
        for obj in self:
            paiements={}
            for row in obj.statement_ids:
                x=row.journal_id.name
                paiements[x]=x
            obj.is_paiement=', '.join(paiements)
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


    @api.depends('statement_ids')
    def _compute_paiement(self):
        for obj in self:
            paiements={}
            for row in obj.statement_ids:
                x=row.journal_id.name
                paiements[x]=x
            obj.is_paiement=', '.join(paiements)


    is_annee     = fields.Char(string=u'Année de la commande', compute='_compute', readonly=True, store=True)
    is_mois      = fields.Char(string=u'Mois de la commande' , compute='_compute', readonly=True, store=True)
    is_total     = fields.Float(string=u'Total TTC' , compute='_compute_total', readonly=True, store=True)
    is_paiement  = fields.Char(string=u'Paiement', compute='_compute_paiement', readonly=True, store=True)


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"


    order_id = fields.Many2one('pos.order', string=u'Les lignes', ondelete='cascade', index=True)
