# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import datetime
import odoo.addons.decimal_precision as dp


def _date_creation():
    return datetime.date.today() # Date du jour


class IsPreparationCommande(models.Model):
    _name='is.preparation.commande'
    _order='name desc'

    name            = fields.Date("Date préparation"        , required=True, default=lambda *a: _date_creation())
    date_debut      = fields.Date("Date de début des ventes", required=True)
    date_fin        = fields.Date("Date de fin des ventes"  , required=True)
    line_ids        = fields.One2many('is.preparation.commande.line'       , 'preparation_id', u'Lignes')
    fournisseur_ids = fields.One2many('is.preparation.commande.fournisseur', 'preparation_id', u'Fournisseurs')
    designation     = fields.Char("Désignation article")
    besoins         = fields.Boolean("Uniquement les fournisseurs ayant des besoins", default=False)


    @api.multi
    def lancer_analyse_action(self):
        cr = self._cr
        for obj in self:
            obj.line_ids.unlink()
            obj.fournisseur_ids.unlink()
            sql="""
                select pol.product_id,sum(pol.qty)
                from pos_order_line pol inner join pos_order po on pol.order_id=po.id
                where 
                    po.date_order>='"""+str(obj.date_debut)+""" 00:00:00' and
                    po.date_order<='"""+str(obj.date_fin)+""" 23:59:59' 
                group by pol.product_id;
            """
            cr.execute(sql)
            result = cr.fetchall()
            orders={}
            for row in result:
                orders[row[0]]=row[1]
            sql="""
                select 
                    pp.id,
                    pt.pos_categ_id,
                    0 ventes_totales,
                    (
                        select rp.id
                        from product_supplierinfo ps inner join res_partner rp on ps.name=rp.id
                        where ps.product_tmpl_id=pt.id
                        limit 1
                    ) partner_id,
                    (
                        select rp.is_frequence
                        from product_supplierinfo ps inner join res_partner rp on ps.name=rp.id
                        where ps.product_tmpl_id=pt.id
                        limit 1
                    ) frequence,
                    (
                        select sum(pol.product_qty)
                        from purchase_order_line pol inner join purchase_order po on pol.order_id=po.id
                        where 
                            po.state in ('draft','sent') and 
                            pol.product_id=pp.id
                    ) qt_cde,
                    (
                        select ps.price
                        from product_supplierinfo ps 
                        where ps.product_tmpl_id=pt.id
                        limit 1
                    ) prix_achat,
                    (
                        select sum(sq.qty)
                        from stock_quant sq inner join stock_location sl on sq.location_id=sl.id 
                        where sq.product_id=pp.id and sl.usage='internal' and sl.active='t'
                    ) stock,
                    pt.uom_po_id,
                    is_unit_coef(pt.uom_id,pt.uom_po_id)
                from product_product pp inner join product_template pt on pp.product_tmpl_id=pt.id 
                where pt.pos_categ_id is not null
            """


            if obj.designation:
                sql=sql+" and pt.name ilike '"+obj.designation+"%' "
            sql=sql+" order by pt.name limit 50000"
            cr.execute(sql)
            result = cr.fetchall()
            d1=datetime.datetime.strptime(obj.date_debut, '%Y-%m-%d')
            d2=datetime.datetime.strptime(obj.date_fin, '%Y-%m-%d')
            delta = d2 - d1
            nb_jours=delta.days
            if nb_jours==0:
                nb_jours=1
            fournisseurs={}
            for row in result:

                product_id   = row[0]
                pos_categ_id = row[1]
                fournisseur  = row[3]
                frq          = row[4] or 0
                qt_cde       = row[5] or 0
                prix_achat   = row[6] or 0
                stock        = row[7] or 0
                uom_po_id    = row[8]
                coef         = row[9]
                qt_vendue=0
                if product_id in orders:
                    qt_vendue=orders[product_id]
                #stock=0
                if stock:
                    stock = stock/coef
                vente_total=0
                vente_jour=0
                if qt_vendue:
                    vente_total=qt_vendue/coef
                    vente_jour=vente_total/nb_jours
                vente_frq=0
                if frq and vente_jour:
                    vente_frq=vente_jour*frq*1.1
                nb_jours_stock=999
                if vente_jour!=0:
                    nb_jours_stock=stock/vente_jour
                if stock==0:
                    nb_jours_stock=0
                qt_suggeree=round(vente_frq-stock-qt_cde)
                if qt_suggeree<0:
                    qt_suggeree=0

                montant_stock=stock*prix_achat
                montant_cde=qt_suggeree*prix_achat
                if fournisseur not in fournisseurs:
                    fournisseurs[fournisseur]=[0.0,0.0]
                fournisseurs[fournisseur][0]=fournisseurs[fournisseur][0]+montant_stock
                fournisseurs[fournisseur][1]=fournisseurs[fournisseur][1]+montant_cde
                vals={
                    'preparation_id' : obj.id,
                    'product_id'     : product_id,
                    'uom_po_id'      : uom_po_id,
                    'pos_categ_id'   : pos_categ_id,
                    'vente_total'    : vente_total,
                    'vente_jour'     : vente_jour,
                    'vente_frq'      : vente_frq,
                    'stock'          : stock,
                    'qt_cde'         : qt_cde,
                    'qt_suggeree'    : qt_suggeree,
                    'nb_jours_stock' : nb_jours_stock,
                    'prix_achat'     : prix_achat,
                    'montant_cde'    : montant_cde,
                    'montant_stock'  : montant_stock,
                    'partner_id'     : fournisseur,
                    'frq'            : frq,
                }
                res=self.env['is.preparation.commande.line'].create(vals)
            for k in fournisseurs.keys():
                montant_stock = fournisseurs[k][0]
                montant_cde   = fournisseurs[k][1]
                if (obj.besoins==True and montant_cde>0) or obj.besoins==False:
                    vals={
                        'preparation_id': obj.id,
                        'partner_id'    : k,
                        'montant_stock' : montant_stock,
                        'montant_cde'   : montant_cde,
                    }
                    res=self.env['is.preparation.commande.fournisseur'].create(vals)


    @api.multi
    def voir_lignes_action(self):
        for obj in self:
            return {
                'name': u'Préparation du '+str(obj.name),
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'is.preparation.commande.line',
                'domain': [
                    ('preparation_id','=',obj.id),
                ],
                'type'          : 'ir.actions.act_window',
            }


class IsPreparationCommandeLine(models.Model):
    _name='is.preparation.commande.line'
    _order='product_id'


    @api.depends('prix_achat', 'qt_suggeree')
    def _compute(self):
        for obj in self:
            obj.montant_cde=obj.prix_achat*obj.qt_suggeree

    preparation_id  = fields.Many2one('is.preparation.commande', 'Préparation', required=True, ondelete='cascade')
    product_id      = fields.Many2one('product.product' , "Article"  , readonly=True)
    uom_po_id       = fields.Many2one('product.uom' , "Unité d'achat", readonly=True)
    pos_categ_id    = fields.Many2one('pos.category'  , "Catégorie"  , readonly=True)
    vente_total     = fields.Float("Ventes totales", digits=(12,2)   , readonly=True)
    vente_jour      = fields.Float("Ventes par jour", digits=(12,2)  , readonly=True)
    vente_frq       = fields.Float("Ventes x Frq x 1.1", digits=(12,2), readonly=True)
    stock           = fields.Float("Stock", digits=(12,2), readonly=True)
    qt_cde          = fields.Float("Qt en Cde", digits=(12,2), readonly=True)
    qt_suggeree     = fields.Float("Qt suggérée", digits=(12,2))
    nb_jours_stock  = fields.Float("Nb jours stock", digits=(12,2), readonly=True)
    prix_achat      = fields.Float("Prix achat", digits=dp.get_precision('Product Price'))
    montant_cde     = fields.Float("Montant Cde suggérée", digits=(12,2), readonly=True, compute='_compute', store=True)
    montant_stock   = fields.Float("Montant stock actuel", digits=(12,0), readonly=True)
    partner_id      = fields.Many2one('res.partner', "Fournisseur", readonly=True)
    frq             = fields.Float("Frq", readonly=True)


class IsPreparationCommandeFournisseur(models.Model):
    _name='is.preparation.commande.fournisseur'
    _order='partner_id'

    preparation_id  = fields.Many2one('is.preparation.commande', 'Préparation', required=True, ondelete='cascade')
    partner_id      = fields.Many2one('res.partner', "Fournisseur"      , readonly=True)
    montant_stock   = fields.Float("Montant stock"       , digits=(12,0), readonly=True)
    montant_cde     = fields.Float("Montant Cde suggérée", digits=(12,0), readonly=True)
    order_id        = fields.Many2one('purchase.order', "Commande"      , readonly=True)

    @api.multi
    def liste_articles_action(self):
        for obj in self:
            return {
                'name': u'Articles '+obj.partner_id.name,
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'is.preparation.commande.line',
                'domain': [
                    ('preparation_id', '=', obj.preparation_id.id),
                    ('partner_id'    , '=', obj.partner_id.id),
                ],
                'type': 'ir.actions.act_window',
            }


    @api.multi
    def creation_commande_action(self):
        for obj in self:
            partner=obj.partner_id
            vals={
                'partner_id'      : partner.id,
                'fiscal_position_id' : partner.property_account_position_id.id,
            }
            order=self.env['purchase.order'].create(vals)
            if order:
                order_line_obj = self.env['purchase.order.line']

                filtre=[
                    ('preparation_id', '=', obj.preparation_id.id),
                    ('partner_id'    , '=', obj.partner_id.id),
                    ('qt_suggeree'   , '>', 0),
                ]
                lines=self.env['is.preparation.commande.line'].search(filtre)
                for line in lines:
                    taxe_ids  = []
                    for tax in line.product_id.supplier_taxes_id:
                        taxe_ids.append(tax.id)
                    name = line.product_id.name
                    if line.product_id.description_purchase:
                        name = line.product_id.description_purchase
                    vals={
                        'order_id'    : order.id,
                        'product_id'  : line.product_id.id,
                        'name'        : name,
                        'product_uom' : line.uom_po_id.id ,
                        'price_unit'  : line.prix_achat,
                        'product_qty' : line.qt_suggeree,
                        'date_planned': '2018-01-01',
                        'taxes_id'    : [(6,0,taxe_ids)],
                    }
                    line=order_line_obj.create(vals)
                obj.order_id=order.id


