# -*- coding: utf-8 -*-

from openerp import tools
from openerp import models,fields,api
from openerp.tools.translate import _


class is_pos_order_line(models.Model):
    _name='is.pos.order.line'
    _order='id desc'
    _auto = False

    date_order   = fields.Date(u'Date du ticket')
    is_annee     = fields.Char(u'Année')
    is_mois      = fields.Char(u'Mois')
    jour_an      = fields.Char(u"Jour dans l'année")
    jour_mois    = fields.Char(u'Jour du mois')
    jour_semaine = fields.Char(u'Jour dans semaine')
    semaine      = fields.Char(u'Semaine')
    heure        = fields.Char(u"Heure")
    order_id     = fields.Many2one('pos.order', u'Ticket')
    session_id   = fields.Many2one('pos.session', u'Session')
    product_id   = fields.Many2one('product.template', u'Article')
    fournisseur  = fields.Char(u'Fournisseur')
    pos_categ_id = fields.Many2one('pos.category', u'Catégorie')
    is_parent_pos_categ_id = fields.Many2one('pos.category', u'Catégorie mère')
    qty          = fields.Float(u'Quantité')
    price_unit   = fields.Float(u'Quantité')
    montant      = fields.Float(u'Montant')
    tax_id       = fields.Many2one('account.tax', u'TVA')


#SELECT ((stored_timestamp AT TIME ZONE 'UTC') AT TIME ZONE 'EST') AS local_timestamp

    def init(self):
        cr , uid, context = self.env.args
        tools.drop_view_if_exists(cr, 'is_pos_order_line')
        cr.execute("""
            CREATE OR REPLACE view is_pos_order_line AS (
                select
                    pol.id,
                    po.date_order::date date_order,
                    po.is_annee,
                    po.is_mois,
                    to_char(po.date_order,'DDD') jour_an,
                    to_char(po.date_order,'DD') jour_mois,
                    to_char(po.date_order,'ID') jour_semaine,
                    to_char(po.date_order,'IW') semaine,
                    to_char((po.date_order AT TIME ZONE 'CET'),'HH24') heure,
                    pol.order_id,
                    po.session_id,
                    pt.id product_id,
                    substring(pt.name,0,4) fournisseur,
                    pt.pos_categ_id,
                    pt.is_parent_pos_categ_id,
                    pol.qty,
                    pol.price_unit,
                    pol.qty*pol.price_unit montant,
                    (select account_tax_id from account_tax_pos_order_line_rel where pos_order_line_id=pol.id limit 1) tax_id
                from pos_order po inner join pos_order_line  pol on pol.order_id=po.id
                                  inner join product_product  pp on pol.product_id=pp.id 
                                  inner join product_template pt on pp.product_tmpl_id=pt.id 
            )
        """)

