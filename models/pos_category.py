# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class PosCategory(models.Model):
    _inherit = "pos.category"
    _order = "parent_id, name"


    def _compute(self):
        for obj in self:
            products   = self.env['product.template'].search([('pos_categ_id','=',obj.id)])
            categories = self.env['pos.category'].search([('parent_id','=',obj.id)])
            obj.is_nb_articles   = len(products)
            obj.is_nb_categories = len(categories)


    active = fields.Boolean('Active', default=True)
    is_nb_articles   = fields.Char(string=u'Nb articles'       , compute='_compute', readonly=True, store=False)
    is_nb_categories = fields.Char(string=u'Nb sous-catégories', compute='_compute', readonly=True, store=False)


    @api.multi
    def liste_articles_action(self):
        for obj in self:
            return {
                'name': u'Articles de la catégorie '+obj.name,
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'product.template',
                'domain': [
                    ('pos_categ_id', '=', obj.id),
                ],
                'type': 'ir.actions.act_window',
            }


    @api.multi
    def liste_categories_action(self):
        for obj in self:
            return {
                'name': u'Sous-catégories de '+obj.name,
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'pos.category',
                'domain': [
                    ('parent_id', '=', obj.id),
                ],
                'type': 'ir.actions.act_window',
            }

