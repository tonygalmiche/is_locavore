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
    is_jour_panier = fields.Selection([
        ('2', 'Mardi'),
        ('3', 'Mercredi'),
        ('4', 'Jeudi'),
        ('5', 'Vendredi'),
        ('6', 'Samedi'),
    ], 'Jour panier client')
    is_semaine_panier = fields.Selection([
        ('P', 'Semaines paires'),
        ('I', 'Semaines impaires'),
        ('T', 'Toutes les semaines'),
    ], 'Semaine panier client')
    is_consigne_panier = fields.Text('Consignes du client pour le panier')
