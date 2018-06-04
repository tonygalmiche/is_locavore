# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_prenom    = fields.Char('Prénom contact')
    is_nom       = fields.Char('Nom contact')
    is_code      = fields.Char('Code du fournisseur')
    is_frequence = fields.Integer('Fréquence de livraison en jours')

