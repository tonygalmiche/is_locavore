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

    is_prix_achat         = fields.Float("Prix d'achat HT")
    is_coef_multi_propose = fields.Float("Coeficient")
    is_taux_tva_achat     = fields.Float("Taux de TVA Achat"                , compute='_compute', store=True, readonly=True)
    is_taux_tva_vente     = fields.Float("Taux de TVA Vente"                , compute='_compute', store=True, readonly=True)
    is_prix_vente_propose = fields.Float("Prix de vente TTC calculé"        , compute='_compute', store=True, readonly=True)
    is_coef_multi_calcule = fields.Float("Coef. calculé"                    , compute='_compute', store=True, readonly=True)
    is_contenance         = fields.Integer("Contenance")
    is_contenance_uom_id  = fields.Many2one('product.uom', "Unité de contenance")
    is_id_clyo            = fields.Char("Id Clyo")


#    def name_get(self, cr, uid, ids, context=None):
#        res = []
#        for product in self.browse(cr, uid, ids, context=context):
#            name=product.name
#            res.append((product.id,name))
#        return res


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
        





