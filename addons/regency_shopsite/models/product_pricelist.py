from itertools import chain

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import formatLang


class Pricelist(models.Model):
    _inherit = 'product.pricelist'

    def _get_applicable_rules_domain(self, products, date, **kwargs):
        """
        overridden to get rules set on overlay templates
        """
        if products._name == 'product.template':
            templates_domain = ('product_tmpl_id', 'in', products.ids)
            products_domain = ('product_id.product_tmpl_id', 'in', products.ids)
            # start custom logic
            overlay_domain = ('overlay_tmpl_id', 'in', products.overlay_template_ids.ids)
            # end custom logic
        else:
            templates_domain = ('product_tmpl_id', 'in', products.product_tmpl_id.ids)
            products_domain = ('product_id', 'in', products.ids)
            # start custom logic
            attribute_id = self.env.ref('regency_shopsite.overlay_attribute')
            value_id = products.product_template_variant_value_ids.filtered(lambda f: f.attribute_id == attribute_id)
            overlay_tmpl_id = value_id.product_attribute_value_id.overlay_template_id
            overlay_domain = ('overlay_tmpl_id', '=', overlay_tmpl_id.id)
            # end custom logic

        return [
            ('pricelist_id', '=', self.id),
            '|', ('categ_id', '=', False), ('categ_id', 'child_of', products.categ_id.ids),
            '|', ('product_tmpl_id', '=', False), templates_domain,
            # start custom logic
            '|', ('overlay_tmpl_id', '=', False), overlay_domain,
            # end custom logic
            '|', ('product_id', '=', False), products_domain,
            '|', ('date_start', '=', False), ('date_start', '<=', date),
            '|', ('date_end', '=', False), ('date_end', '>=', date),
        ]
