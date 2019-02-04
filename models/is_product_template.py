# -*- coding: utf-8 -*-

from openerp import tools
from openerp import models,fields,api
from openerp.tools.translate import _


class is_product_template(models.Model):
    _name='is.product.template'
    _order='product_id'
    _auto = False


    product_id         = fields.Many2one('product.template', u'Article')
    account_income_id  = fields.Many2one('account.account', u'Compte de revenus')
    taxe_id            = fields.Many2one('account.tax', u'Taxe à la vente')
    account_expense_id = fields.Many2one('account.account', u'Compte de dépenses')
    supplier_taxe_id   = fields.Many2one('account.tax', u'Taxe fournisseur')
    nb_taxes           = fields.Integer(u'Nb taxes à la vente')
    nb_supplier_taxes  = fields.Integer(u'Nb taxes fournisseur')
    available_in_pos   = fields.Boolean(u'Disponible dans le point de vente')


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

            CREATE OR REPLACE FUNCTION get_property_account_expense_id(product_id integer) RETURNS integer AS $$
            BEGIN
                RETURN (
                    select substring(value_reference, 17)::int account_expense_id
                    from ir_property ip 
                    where ip.name='property_account_expense_id' and res_id=concat('product.template,',product_id)
                    limit 1
                );
            END;
            $$ LANGUAGE plpgsql;



            CREATE OR REPLACE view is_product_template AS (
                select
                    pt.id,
                    pt.id product_id,
                    pt.available_in_pos,
                    get_property_account_income_id(pt.id) account_income_id,
                    get_property_account_expense_id(pt.id) account_expense_id,
                    (
                        select rel.tax_id from product_taxes_rel rel where rel.prod_id=pt.id limit 1
                    ) taxe_id,

                    (
                        select rel.tax_id from product_supplier_taxes_rel rel where rel.prod_id=pt.id limit 1
                    ) supplier_taxe_id,

                    (
                        select count(*) from product_taxes_rel rel where rel.prod_id=pt.id 
                    ) nb_taxes,

                    (
                        select count(*) from product_supplier_taxes_rel rel where rel.prod_id=pt.id 
                    ) nb_supplier_taxes


                from product_template pt where pt.active='t'
            )
        """)

