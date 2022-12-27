from odoo import models, _
from odoo.addons.delivery.models.delivery_request_objects import DeliveryPackage
from odoo.exceptions import UserError


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    def _get_packages_from_order(self, order, default_package_type):
        """
        Overriden.
        """
        packages = []

        total_cost = 0
        for line in order.order_line.filtered(lambda line: not line.is_delivery and not line.display_type):
            total_cost += self._product_price_to_company_currency(line.product_qty, line.product_id, order.company_id)

        total_weight = self._get_estimated_weight(order) + default_package_type.base_weight  # Overridden
        if total_weight == 0.0:
            weight_uom_name = self.env['product.template']._get_weight_uom_name_from_ir_config_parameter()
            raise UserError(
                _("The package cannot be created because the total weight of the products in the picking is 0.0 %s") % (
                    weight_uom_name))
        # If max weight == 0 => division by 0. If this happens, we want to have
        # more in the max weight than in the total weight, so that it only
        # creates ONE package with everything.
        max_weight = default_package_type.max_weight or total_weight + 1
        total_full_packages = int(total_weight / max_weight)
        last_package_weight = total_weight % max_weight

        package_weights = [max_weight] * total_full_packages + [last_package_weight] if last_package_weight else []
        partial_cost = total_cost / len(package_weights)  # separate the cost uniformly
        for weight in package_weights:
            packages.append(DeliveryPackage(None, weight, default_package_type, total_cost=partial_cost, currency=order.company_id.currency_id, order=order))
        return packages

    def _get_estimated_weight(self, order):
        self.ensure_one()
        weight = 0.0
        for order_line in order.order_line.filtered(
                lambda l: l.product_id.type in ['product', 'consu'] and not l.is_delivery and not l.display_type):
            stock_picking = order_line.move_ids.mapped('picking_id').filtered(lambda f: f.state in ['assigned', 'done'])
            if stock_picking:
                package_id = stock_picking.move_line_ids.mapped('package_id')
                product_stock_quant = package_id.quant_ids.filtered(lambda f: f.product_id == order_line.product_id)
                weight = package_id.shipping_weight / product_stock_quant.quantity * sum(
                    stock_picking.move_line_ids.mapped('reserved_qty'))
            else:
                weight += order_line.product_qty * order_line.product_id.weight
        return weight
