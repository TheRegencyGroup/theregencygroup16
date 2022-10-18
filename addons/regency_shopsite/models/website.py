from odoo import api, fields, models
from odoo.osv import expression


class Website(models.Model):
    _inherit = 'website'

    def sale_product_domain(self):
        domain = super(Website, self).sale_product_domain()
        only_item_domain = expression.AND([domain, [('is_fit_for_overlay', '=', 'True')]])
        return only_item_domain
