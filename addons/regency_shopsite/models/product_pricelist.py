from odoo import models
from odoo.osv import expression


class Pricelist(models.Model):
    _inherit = 'product.pricelist'

    def _get_applicable_rules_domain(self, products, date, **kwargs):
        """
        overridden to get rules set on overlay templates
        """
        res = super()._get_applicable_rules_domain(products, date, **kwargs)
        if 'overlay_tmpl_id' in kwargs.keys():
            res = expression.AND([res, [('overlay_tmpl_id', '=', kwargs['overlay_tmpl_id'])]])
        return res
