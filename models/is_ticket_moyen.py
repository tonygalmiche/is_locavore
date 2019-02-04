# -*- coding: utf-8 -*-

from openerp import tools
from openerp import models,fields,api
from openerp.tools.translate import _


class IsTicketMoyen(models.Model):
    _name='is.ticket.moyen'
    _order='date desc'
    _auto=False

    date_order   = fields.Date(u'Date du ticket')
    annee        = fields.Char(u'Année')
    mois         = fields.Char(u'Mois')
    jour_an      = fields.Char(u"Jour dans l'année")
    jour_mois    = fields.Char(u'Jour du mois')
    jour_semaine = fields.Char(u'Jour dans semaine')
    semaine      = fields.Char(u'Semaine')
    session_id   = fields.Many2one(u'pos.session', 'Session')
    total_ttc    = fields.Float(u'Total TTC'   , digits=(14,2))
    nb_tickets   = fields.Integer(u'Nb tickets')
    ticket_moyen = fields.Float(u'Ticket moyen', digits=(14,2))

    def init(self):
        cr , uid, context = self.env.args
        tools.drop_view_if_exists(cr, 'is_ticket_moyen')
        cr.execute("""
            CREATE OR REPLACE view is_ticket_moyen AS (
                select
                    max(po.id) id,
                    to_char(po.date_order,'YYYY-MM-DD') date_order,
                    to_char(po.date_order,'YYYY') annee,
                    to_char(po.date_order,'MM') mois,
                    to_char(po.date_order,'DDD') jour_an,
                    to_char(po.date_order,'DD') jour_mois,
                    to_char(po.date_order,'ID') jour_semaine,
                    to_char(po.date_order,'IW') semaine,
                    max(po.session_id) session_id,
                    sum(po.is_total) total_ttc,
                    count(*) nb_tickets,
                    sum(po.is_total)/count(*) ticket_moyen
                from pos_order po 
                where po.date_order>='2014-01-01'
                group by 
                    to_char(po.date_order,'YYYY-MM-DD'),
                    to_char(po.date_order,'YYYY'),
                    to_char(po.date_order,'MM'),
                    to_char(po.date_order,'DDD'),
                    to_char(po.date_order,'DD'),
                    to_char(po.date_order,'ID'),
                    to_char(po.date_order,'IW')
                order by to_char(po.date_order,'YYYY-MM-DD') desc
            )
        """)


class IsTicketMoyenMois(models.Model):
    _name='is.ticket.moyen.mois'
    _order='annee desc, mois desc'
    _auto=False

    annee        = fields.Char(u'Année')
    mois         = fields.Char(u'Mois')
    total_ttc    = fields.Float(u'Total TTC'   , digits=(14,2))
    nb_tickets   = fields.Integer(u'Nb tickets')
    ticket_moyen = fields.Float(u'Ticket moyen', digits=(14,2))

    def init(self):
        cr , uid, context = self.env.args
        tools.drop_view_if_exists(cr, 'is_ticket_moyen_mois')
        cr.execute("""
            CREATE OR REPLACE view is_ticket_moyen_mois AS (
                select
                    max(po.id) id,
                    to_char(po.date_order,'YYYY') annee,
                    to_char(po.date_order,'MM') mois,
                    sum(po.is_total) total_ttc,
                    count(*) nb_tickets,
                    sum(po.is_total)/count(*) ticket_moyen
                from pos_order po 
                where po.date_order>='2014-01-01'
                group by 
                    to_char(po.date_order,'YYYY'),
                    to_char(po.date_order,'MM')
                order by 
                    to_char(po.date_order,'YYYY') desc,
                    to_char(po.date_order,'MM') desc
            )
        """)




