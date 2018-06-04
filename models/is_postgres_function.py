# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class is_postgres_function(models.Model):
    _name='is.postgres.function'

    name = fields.Char('Name')

    def init(self):
        cr, uid, context = self.env.args
        tools.drop_view_if_exists(cr, 'is_comparatif_tarif_reception')
        cr.execute("""
            CREATE OR REPLACE FUNCTION is_unit_coef(uom1 integer, uom2 integer) RETURNS float AS $$
            DECLARE
                factor1 float := 1;
                factor2 float := 1;
            BEGIN

                factor1 := (
                    select factor 
                    from product_uom
                    where id=uom1
                );
                factor2 := (
                    select factor 
                    from product_uom
                    where id=uom2
                );
                RETURN factor1/factor2;
            END;
            $$ LANGUAGE plpgsql;
        """)


