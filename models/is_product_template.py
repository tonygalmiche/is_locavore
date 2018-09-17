# -*- coding: utf-8 -*-

from openerp import tools
from openerp import models,fields,api
from openerp.tools.translate import _


class is_product_template(models.Model):
    _name='is.product.template'
    _order='id desc'
    _auto = False


    product_id        = fields.Many2one('product.template', 'Article')
    account_income_id = fields.Many2one('account.account', 'Compte de revenus')
    taxe_id           = fields.Many2one('account.tax', 'Taxe à la vente')


    def init(self):
        cr , uid, context = self.env.args
        tools.drop_view_if_exists(cr, 'is_product_template')
        cr.execute("""

            CREATE OR REPLACE FUNCTION get_property_account_income_id(product_id integer) RETURNS integer AS $$
            BEGIN
                RETURN (
                    select substring(value_reference, 17)::int account_income_id
                    from ir_property ip 
                    where ip.name='property_account_income_id' and res_id=concat('product.template,',product_id)
                    limit 1
                );
            END;
            $$ LANGUAGE plpgsql;

            CREATE OR REPLACE view is_product_template AS (
                select
                    pt.id,
                    pt.id product_id,
                    get_property_account_income_id(pt.id) account_income_id,
                    (
                        select rel.tax_id from product_taxes_rel rel where rel.prod_id=pt.id limit 1
                    ) taxe_id
                from product_template pt
            )
        """)

