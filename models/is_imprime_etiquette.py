# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import datetime


def _date_creation():
    return datetime.date.today() # Date du jour


class IsImprimeEtiquette(models.Model):
    _name='is.imprime.etiquette'
    _order='name desc'

    name        = fields.Date("Date", required=True, default=lambda *a: _date_creation())
    designation = fields.Char("Filtre désignation article", required=True)
    line_ids    = fields.One2many('is.imprime.etiquette.line', 'imprime_id', u'Lignes')


class IsImprimeEtiquetteLine(models.Model):
    _name='is.imprime.etiquette.line'
    _order='product_id'

    imprime_id         = fields.Many2one('is.preparation.commande', 'Préparation', required=True, ondelete='cascade')
    product_id         = fields.Many2one('product.product' , "Article", required=True)
    designation        = fields.Char("Désignation", required=True)
    prix_vente         = fields.Float("Prix de vente", digits=(12,2), required=True)
    contenance         = fields.Float("Contenance", digits=(12,0))
    contenance_uom_id  = fields.Many2one('product.uom', "Unité de contenance")
    prix_kg            = fields.Float("Prix Kg/L", digits=(12,2))
    uom_id             = fields.Many2one('product.uom', "Unité")
    nb_etiquettes      = fields.Integer("Nb étiquettes", default=1)
    imprime            = fields.Boolean("Imprime")

    @api.multi
    def onchange_product_id(self, product_id):
        print product_id
        res={}

        if product_id:
            res['value']={}
            product = self.env['product.product'].browse(product_id)
            res['value'].update({
                'designation'      : product.name,
                'prix_vente'       : product.lst_price,
                'contenance'       : product.is_contenance,
                'contenance_uom_id': product.is_contenance_uom_id,
                'prix_kg'          : product.lst_price,
                'uom_id': product.is_contenance_uom_id,
            })
        print res
        return res

