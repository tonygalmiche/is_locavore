# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_prenom      = fields.Char(u'Prénom contact')
    is_nom         = fields.Char(u'Nom contact')
    is_code        = fields.Char(u'Code du fournisseur')
    is_frequence   = fields.Integer(u'Fréquence de livraison en jours')
    is_distance    = fields.Integer(u'Distance du producteur (km)')
    is_sens_fleche = fields.Selection([
        ('gauche', 'Gauche'),
        ('droite', 'Droite'),
    ], u'Sens flèche étiquette producteur', default='droite')
    is_semaine_panier = fields.Selection([
        ('P', 'Semaines paires'),
        ('I', 'Semaines impaires'),
        ('T', 'Toutes les semaines'),
    ], u'Semaine panier client')
    is_jour_panier = fields.Selection([
        ('2', 'Mardi'),
        ('3', 'Mercredi'),
        ('4', 'Jeudi'),
        ('5', 'Vendredi'),
        ('6', 'Samedi'),
    ], u'Jour du panier')
    is_horaire_panier = fields.Selection([
        ('matin', 'Matin'),
        ('midi' , 'Midi'),
        ('soir' , 'Soir'),
    ], u'Horaire du panier')
    is_montant_panier = fields.Integer(u'Montant du panier')
    is_consigne_panier = fields.Text(u'Consignes du client pour le panier')
