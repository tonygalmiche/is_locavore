# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import datetime


def _date_creation():
    return datetime.date.today() # Date du jour


class IsImprimeEtiquette(models.Model):
    _name='is.imprime.etiquette'
    _order='name desc'

    name        = fields.Date(u"Date", required=True, default=lambda *a: _date_creation())
    designation = fields.Char(u"Filtre désignation article", required=True)
    line_ids    = fields.One2many('is.imprime.etiquette.line', 'imprime_id', u'Lignes')


    @api.model
    def create(self, vals):
        obj = super(IsImprimeEtiquette, self).create(vals)
        products = self.env['product.product'].search([('name','like',vals['designation'])])
        for product in products:
            line_obj=self.env['is.imprime.etiquette.line']
            res=line_obj.onchange_product_id(product.id)
            vals=res['value']
            vals.update({
                'imprime_id'       : obj.id,
                'product_id'       : product.id,
            })
            new_id=line_obj.create(vals)
        return obj


class IsImprimeEtiquetteLine(models.Model):
    _name='is.imprime.etiquette.line'
    _order='product_id'

    imprime_id         = fields.Many2one('is.imprime.etiquette', u'Imprime étiquette', required=True, ondelete='cascade')
    product_id         = fields.Many2one('product.product' , u"Article", required=True)
    designation        = fields.Char(u"Désignation", required=True)
    prix_vente         = fields.Float(u"Prix de vente", digits=(12,2), required=True)
    contenance         = fields.Float(u"Contenance", digits=(12,0))
    contenance_uom_id  = fields.Many2one('product.uom', u"Unité de contenance")
    prix_kg            = fields.Float(u"Prix Kg/L", digits=(12,2))
    uom_id             = fields.Many2one('product.uom', "Kg/L")
    largeur            = fields.Integer(u"Largeur désignation étiquette", default=35)
    nb_etiquettes      = fields.Integer(u"Nb étiquettes", default=1)
    imprime            = fields.Boolean(u"Imprime",default=True)


    @api.multi
    def onchange_product_id(self, product_id):
        res={}
        if product_id:
            res['value']={}
            product = self.env['product.product'].browse(product_id)
            prix_kg=0

            category_id=product.is_contenance_uom_id.category_id.id
            uoms = self.env['product.uom'].search([('uom_type','=','reference'),('category_id','=',category_id)])
            uom=False
            for uom in uoms:
                unite=uom.name
                try:
                    x=uom._compute_quantity(1,product.is_contenance_uom_id)
                except:
                    x=False
                if x:
                    div=product.is_contenance
                    if div==0:
                        div=1
                    prix_kg=product.lst_price*x/div

            designation=product.name.upper()
            if product.is_designation:
                designation=product.is_designation.upper()
            res['value'].update({
                'designation'      : designation,
                'prix_vente'       : product.lst_price,
                'contenance'       : product.is_contenance,
                'contenance_uom_id': product.is_contenance_uom_id.id,
                'prix_kg'          : prix_kg,
                'uom_id'           : uom and uom.id or False,
            })
        return res

