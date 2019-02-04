# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import datetime
import odoo.addons.decimal_precision as dp


def _date_creation():
    return datetime.date.today() # Date du jour


class IsAnalyseTauxMarge(models.Model):
    _name='is.analyse.taux.marge'
    _order='name desc'

    name            = fields.Date(u"Date analyse", required=True, default=lambda *a: _date_creation())
    date_debut      = fields.Date(u"Date de début des ventes", required=True)
    date_fin        = fields.Date(u"Date de fin des ventes"  , required=True)
    pos_categ_id    = fields.Many2one('pos.category', u"Catégorie")
    line_ids        = fields.One2many('is.analyse.taux.marge.line', 'analyse_id', u'Lignes')


    @api.multi
    def lancer_analyse_action(self):
        cr = self._cr
        for obj in self:
            obj.line_ids.unlink()
            #d1=datetime.datetime.strptime(obj.date_debut, '%Y-%m-%d')
            #d2=datetime.datetime.strptime(obj.date_fin, '%Y-%m-%d')
            sql="""
                select 
                    pp.id,
                    pt.uom_po_id,
                    pt.pos_categ_id,
                    pt.is_parent_pos_categ_id,
                    pt.is_coef_multi_calcule,
                    (   select
                            sum(pol.price_total)
                        from purchase_order po inner join purchase_order_line pol on po.id=pol.order_id
                        where 
                            po.state not in ('draft','cancel') and
                            po.date_order>='"""+obj.date_debut+""" 00:00:00' and 
                            po.date_order<='"""+obj.date_fin+""" 23:59:59' and 
                            pol.product_id=pp.id
                    ),
                    (   select
                            sum(posl.price_unit*posl.qty)
                        from pos_order_line posl
                        where 
                            posl.product_id=pp.id and
                            posl.create_date>='"""+obj.date_debut+""" 00:00:00' and 
                            posl.create_date<='"""+obj.date_fin+""" 23:59:59'
                    )
                from product_template pt inner join product_product pp on pp.product_tmpl_id=pt.id
                where pt.pos_categ_id is not null
                limit 5000;
            """
            cr.execute(sql)
            result = cr.fetchall()
            for row in result:
                ca_achat = row[5]
                ca_vente = row[6]
                if ca_achat>0 and ca_vente>0:
                    taux_marge=ca_vente/ca_achat
                    vals={
                        'analyse_id'         : obj.id,
                        'product_id'         : row[0],
                        'uom_po_id'          : row[1],
                        'pos_categ_id'       : row[2],
                        'parent_pos_categ_id': row[3],
                        'ca_achat'           : ca_achat,
                        'ca_vente'           : ca_vente,
                        'taux_marge_article' : row[4],
                        'taux_marge'         : taux_marge,
                    }
                    res=self.env['is.analyse.taux.marge.line'].create(vals)


    @api.multi
    def voir_lignes_action(self):
        for obj in self:
            return {
                'name': u'Analyse du '+str(obj.name),
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'is.analyse.taux.marge.line',
                'domain': [
                    ('analyse_id','=',obj.id),
                ],
                'type' : 'ir.actions.act_window',
            }


class IsAnalyseTauxMargeLine(models.Model):
    _name='is.analyse.taux.marge.line'
    _order='product_id'


    analyse_id          = fields.Many2one('is.analyse.taux.marge', u'Analyse', required=True, ondelete='cascade')
    product_id          = fields.Many2one('product.product'        , u"Article"  , readonly=True, index=True)
    uom_po_id           = fields.Many2one('product.uom'            , u"Unité d'achat", readonly=True)
    pos_categ_id        = fields.Many2one('pos.category'           , u"Catégorie", readonly=True, index=True)
    parent_pos_categ_id = fields.Many2one('pos.category', u"Catégorie mère", index=True)
    ca_achat            = fields.Float(u"CA Achats TTC", digits=(12,2), readonly=True)
    ca_vente            = fields.Float(u"CA Ventes TTC", digits=(12,2), readonly=True)
    taux_marge_article  = fields.Float(u"Taux marge prévu article", digits=(12,2), readonly=True)
    taux_marge          = fields.Float(u"Taux marge calculé", digits=(12,2), readonly=True)


