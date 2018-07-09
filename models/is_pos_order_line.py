# -*- coding: utf-8 -*-

from openerp import tools
from openerp import models,fields,api
from openerp.tools.translate import _


class is_pos_order_line(models.Model):
    _name='is.pos.order.line'
    _order='id desc'
    _auto = False

    date_order   = fields.Date('Date du ticket')
    is_annee     = fields.Char('Année')
    is_mois      = fields.Char('Mois')
    order_id     = fields.Many2one('pos.order', 'Ticket')
    session_id   = fields.Many2one('pos.session', 'Session')
    product_id   = fields.Many2one('product.template', 'Article')
    pos_categ_id = fields.Many2one('pos.category', 'Catégorie')
    is_parent_pos_categ_id = fields.Many2one('pos.category', 'Catégorie mère')
    qty          = fields.Float('Quantité')
    price_unit   = fields.Float('Quantité')
    montant      = fields.Float('Montant')
    tax_id       = fields.Many2one('account.tax', 'TVA')


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
                    pol.order_id,
                    po.session_id,
                    pt.id product_id,
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

