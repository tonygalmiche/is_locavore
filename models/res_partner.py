# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_prenom      = fields.Char('Prénom contact')
    is_nom         = fields.Char('Nom contact')
    is_code        = fields.Char('Code du fournisseur')
    is_frequence   = fields.Integer('Fréquence de livraison en jours')
    is_distance    = fields.Integer('Distance du producteur (km)')
    is_sens_fleche = fields.Selection([
        ('gauche', 'Gauche'),
        ('droite', 'Droite'),
    ], 'Sens flèche étiquette producteur', default='droite')


