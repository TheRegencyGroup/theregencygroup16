from odoo import fields, models, api, Command
from odoo.addons.regency_estimate.models.product_price_sheet import MAX_QUANTITY


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    price_sheet_id = fields.Many2one('product.price.sheet')
    estimate_id = fields.Many2one('sale.estimate')

    def _has_to_be_signed(self, include_draft=False):
        return super(SaleOrder, self)._has_to_be_signed(include_draft=True)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _compute_tax_id(self):
        """
            Temporary disable taxes calculation
        :return:
        """
        #TODO: uncomment when taxes will be handled in a correct way
        pass