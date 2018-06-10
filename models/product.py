# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _order='name'


    @api.depends('is_prix_achat','is_coef_multi_propose','list_price','lst_price','taxes_id','supplier_taxes_id')
    def _compute(self):
        for obj in self:
            is_taux_tva_vente=0
            for taxe in obj.taxes_id:
                is_taux_tva_vente=taxe.amount
            is_taux_tva_achat=0
            for taxe in obj.supplier_taxes_id:
                is_taux_tva_achat=taxe.amount
            is_prix_vente_propose=obj.is_prix_achat*obj.is_coef_multi_propose*(1+is_taux_tva_vente/100)
            is_coef_multi_calcule=0
            if obj.is_prix_achat!=0:
                prix_vente_ht=obj.lst_price/(1+is_taux_tva_vente/100)
                is_coef_multi_calcule=prix_vente_ht/obj.is_prix_achat
            obj.is_taux_tva_achat     = is_taux_tva_achat
            obj.is_taux_tva_vente     = is_taux_tva_vente
            obj.is_prix_vente_propose = is_prix_vente_propose
            obj.is_coef_multi_calcule = is_coef_multi_calcule

    def _is_prix_fournisseur(self):
        for obj in self:
            x=0
            for line in obj.seller_ids:
                x=line.price
            obj.is_prix_fournisseur=x
            obj.is_stock_valorise=x*obj.qty_available

    is_prix_fournisseur   = fields.Float("Prix fournisseur HT", compute='_is_prix_fournisseur', store=False, readonly=True)
    is_stock_valorise     = fields.Float("Stock valorisé"     , compute='_is_prix_fournisseur', store=False, readonly=True)
    is_prix_achat         = fields.Float("Prix d'achat HT")
    is_coef_multi_propose = fields.Float("Coeficient")
    is_taux_tva_achat     = fields.Float("Taux de TVA Achat"                , compute='_compute', store=True, readonly=True)
    is_taux_tva_vente     = fields.Float("Taux de TVA Vente"                , compute='_compute', store=True, readonly=True)
    is_prix_vente_propose = fields.Float("Prix de vente TTC calculé"        , compute='_compute', store=True, readonly=True)
    is_coef_multi_calcule = fields.Float("Coef. calculé"                    , compute='_compute', store=True, readonly=True)
    is_designation        = fields.Char("Désignation étiquette")
    is_contenance         = fields.Integer("Contenance")
    is_contenance_uom_id  = fields.Many2one('product.uom', "Unité de contenance")
    is_id_clyo            = fields.Char("Id Clyo")


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
        





