# -*- coding: utf-8 -*-

from openerp import tools
from openerp import models,fields,api
from openerp.tools.translate import _


class IsTicketHeure(models.Model):
    _name='is.ticket.heure'
    _order='date_order desc, heure desc'
    _auto=False

    date_order   = fields.Date(u'Date du ticket')
    annee        = fields.Char(u'Année')
    mois         = fields.Char(u'Mois')
    semaine      = fields.Char(u'Semaine')
    heure        = fields.Char(u"Heure")
    jour_semaine = fields.Char(u'Jour dans semaine')
    nb_tickets   = fields.Integer(u'Nb tickets')

    def init(self):
        cr , uid, context = self.env.args
        tools.drop_view_if_exists(cr, 'is_ticket_heure')
        cr.execute("""
            CREATE OR REPLACE view is_ticket_heure AS (
                select
                    max(po.id) id,
                    to_char(po.date_order,'YYYY-MM-DD') date_order,
                    to_char(po.date_order,'YYYY') annee,
                    to_char(po.date_order,'MM') mois,
                    to_char(po.date_order,'WW') semaine,
                    to_char(po.date_order,'HH24') heure,
                    to_char(po.date_order,'ID') jour_semaine,
                    count(*) nb_tickets
                from pos_order po 
                where po.date_order>='2014-01-01'
                group by 
                    to_char(po.date_order,'YYYY-MM-DD'),
                    to_char(po.date_order,'YYYY'),
                    to_char(po.date_order,'MM'),
                    to_char(po.date_order,'WW'),
                    to_char(po.date_order,'HH24'),
                    to_char(po.date_order,'ID')
                order by to_char(po.date_order,'YYYY-MM-DD'),to_char(po.date_order,'HH24')
            )
        """)

