from odoo import fields, models, api, Command
from odoo.addons.regency_estimate.models.product_price_sheet import MAX_QUANTITY


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    price_sheet_id = fields.Many2one('product.price.sheet')
    estimate_id = fields.Many2one('sale.estimate')
    legal_accepted = fields.Boolean(default=False)

    def toggle_legal_accepted(self, checked):
        self.ensure_one()
        if self.state == 'draft':
            self.legal_accepted = checked
        return self.legal_accepted


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pricesheet_line_id = fields.Many2one('product.price.sheet.line')

    def _compute_tax_id(self):
        """
            Temporary disable taxes calculation
        :return:
        """
        #TODO: uncomment when taxes will be handled in a correct way
        pass

    def get_purchase_order_lines(self):
        return self.purchase_line_ids |\
               self.order_id.procurement_group_id.stock_move_ids.filtered(lambda x: x.product_id == self.product_id).created_purchase_line_id |\
               self.order_id.procurement_group_id.stock_move_ids.filtered(lambda x: x.product_id == self.product_id).move_orig_ids.purchase_line_id
