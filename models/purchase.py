# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    @api.multi
    def facture_recue_action(self):
        for obj in self:
            obj.invoice_status='invoiced'


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context({
            'lang': self.partner_id.lang,
            'partner_id': self.partner_id.id,
        })
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            #self.name += '\n' + product_lang.description_purchase
            self.name = product_lang.description_purchase

        fpos = self.order_id.fiscal_position_id
        if self.env.uid == SUPERUSER_ID:
            company_id = self.env.user.company_id.id
            self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
        else:
            self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id)

        self._suggest_quantity()
        self._onchange_quantity()

        return result

