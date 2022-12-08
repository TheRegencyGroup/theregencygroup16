import psycopg2

from odoo import api, fields, models, registry, SUPERUSER_ID, _
from odoo.tools.float_utils import float_round

from odoo.addons.delivery.models.delivery_request_objects import DeliveryCommodity, DeliveryPackage


# from .delivery_request_objects import DeliveryCommodity, DeliveryPackage


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    def _get_packages_from_order(self, order, default_package_type):
        packages = []

        total_cost = 0
        for line in order.order_line.filtered(lambda line: not line.is_delivery and not line.display_type):
            total_cost += self._product_price_to_company_currency(line.product_qty, line.product_id, order.company_id)

        total_weight = self._get_estimated_weight(order) + default_package_type.base_weight  # Overridden
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
        for order_line in order.order_line.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not l.is_delivery and not l.display_type):
            in_stock_picking = order_line.move_ids.mapped('picking_id').filtered(lambda f: f.picking_type_code == 'incoming' and f.state == 'done')
            if in_stock_picking:
                stock_quants = in_stock_picking.mapped('package_ids.quant_ids').filtered(lambda f: f.product_id == order_line.product_id)
                qty = sum(stock_quants.mapped('quantity'))
                package_weight = sum(stock_quants.mapped('package_weight'))
                move_lines = order_line.mapped('move_ids.move_line_ids').filtered(lambda f: f.picking_id == in_stock_picking)
                weight = package_weight / qty * sum(move_lines.mapped('qty_done'))

            else:
                weight += order_line.product_qty * order_line.product_id.weight
        return weight
