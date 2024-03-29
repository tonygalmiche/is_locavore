# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _order='name'


    @api.multi
    def actualiser_is_parent_pos_categ_id_action(self):
        for obj in self:
            obj.is_parent_pos_categ_id=obj.pos_categ_id.parent_id


    @api.depends('pos_categ_id')
    def _compute_parent_pos_categ_id(self):
        for obj in self:
            obj.is_parent_pos_categ_id=obj.pos_categ_id.parent_id


    @api.depends('is_prix_achat','is_coef_multi_propose','list_price','lst_price','taxes_id','supplier_taxes_id','is_volume')
    def _compute(self):
        for obj in self:
            coef=1
            if obj.uom_id and obj.uom_po_id:
                if obj.uom_id.factor_inv>0:
                    coef=obj.uom_po_id.factor_inv/obj.uom_id.factor_inv
            
            is_taux_tva_vente=0
            for taxe in obj.taxes_id:
                is_taux_tva_vente=taxe.amount
            is_taux_tva_achat=0
            for taxe in obj.supplier_taxes_id:
                is_taux_tva_achat=taxe.amount
            is_prix_vente_propose=obj.is_prix_achat*obj.is_coef_multi_propose*(1+is_taux_tva_vente/100)
            if coef>0:
                is_prix_vente_propose = is_prix_vente_propose / coef
            is_coef_multi_calcule=0
            if obj.is_prix_achat!=0:
                prix_vente_ht=obj.lst_price/(1+is_taux_tva_vente/100)
                is_coef_multi_calcule=coef * prix_vente_ht/obj.is_prix_achat

            obj.is_taux_tva_achat     = is_taux_tva_achat
            obj.is_taux_tva_vente     = is_taux_tva_vente
            obj.is_prix_vente_propose = is_prix_vente_propose
            obj.is_coef_multi_calcule = is_coef_multi_calcule

            marge = obj.is_prix_achat * (is_coef_multi_calcule - 1.0)
            if coef>0:
                marge=marge/coef
            obj.is_marge = marge

            marge_cm3 = 0
            if obj.is_volume>0:
                marge_cm3 = 1000 * marge / obj.is_volume
            obj.is_marge_cm3 = marge_cm3


    def _is_prix_fournisseur(self):
        for obj in self:
            x=0
            for line in obj.seller_ids:
                x=line.price
            obj.is_prix_fournisseur=x
            obj.is_stock_valorise=x*obj.qty_available


    pos_categ_id           = fields.Many2one('pos.category', string=u'Point of Sale Category', index=True)
    is_prix_fournisseur    = fields.Float(u"Prix fournisseur HT", compute='_is_prix_fournisseur', store=False, readonly=True, digits=dp.get_precision('Product Price'))
    is_stock_valorise      = fields.Float(u"Stock valorisé"     , compute='_is_prix_fournisseur', store=False, readonly=True)
    is_prix_achat          = fields.Float(u"Prix d'achat HT", digits=dp.get_precision('Product Price'))
    is_coef_multi_propose  = fields.Float(u"Coeficient")
    is_taux_tva_achat      = fields.Float(u"Taux de TVA Achat"                , compute='_compute', store=True, readonly=True)
    is_taux_tva_vente      = fields.Float(u"Taux de TVA Vente"                , compute='_compute', store=True, readonly=True)
    is_prix_vente_propose  = fields.Float(u"Prix de vente TTC calculé"        , compute='_compute', store=True, readonly=True, digits=dp.get_precision('Product Price'))
    is_coef_multi_calcule  = fields.Float(u"Coef. calculé"                    , compute='_compute', store=True, readonly=True)
    is_marge               = fields.Float(u"Marge", help = u"Prix d'achat HT x (Coef. calculé - 1)", compute='_compute', store=True, readonly=True, digits=dp.get_precision('Product Price'))
    is_designation         = fields.Char(u"Désignation étiquette")
    is_contenance          = fields.Integer(u"Contenance")
    is_volume              = fields.Integer(u"Volume (cm3)")
    is_marge_cm3           = fields.Float(u"Marge / Litre" , compute='_compute', store=True, readonly=True, digits=dp.get_precision('Product Price'), help="1000 * Marge / Volume")
    is_contenance_uom_id   = fields.Many2one('product.uom', u"Unité de contenance")
    is_id_clyo             = fields.Char(u"Id Clyo")
    is_parent_pos_categ_id = fields.Many2one('pos.category', u"Catégorie mère", compute='_compute_parent_pos_categ_id', store=True, readonly=True, index=True)
    is_dlc                 = fields.Date(u"DLC")


    @api.multi
    def name_get(self):
        res = []
        for product in self.sudo():
            res.append((product.id,product.name))
        return res


class ProductProduct(models.Model):
    _inherit = "product.product"
    _order='name'


    @api.multi
    def name_get(self):
        res = []
        for product in self.sudo():
            res.append((product.id,product.name))
        return res
        





