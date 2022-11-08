import logging
from odoo import fields, models, Command, api

_logger = logging.getLogger(__name__)


class Product(models.Model):
    _inherit = 'product.product'

    ext_overseas = fields.Char()
    ext_routes_type = fields.Char()
    ext_template_name = fields.Char()
    ext_qty_per_carton = fields.Integer()
    ext_reorder_point = fields.Integer()
    ext_all_customers = fields.Boolean()

    def after_import_update(self):
        all = self.search([])
        all.set_routes_from_import_data()

    def set_routes_from_import_data(self):
        mto_mts = self.env.ref('stock_mts_mto_rule.route_mto_mts')
        buy = self.env.ref('purchase_stock.route_warehouse0_buy')
        mto = self.env.ref('stock.route_warehouse0_mto')
        cross_docks = self.env['stock.warehouse'].search([]).mapped('crossdock_route_id')
        for rec in self.filtered('ext_routes_type'):
            if rec.ext_routes_type[:9] == 'Inventory':
                # Inventory: MTO+MTS, Buy
                rec.route_ids = [Command.link(mto_mts.id), Command.link(buy.id)]
            elif rec.ext_routes_type[:8] == 'Standard':
                # Standard: CROSS-DOCK, MTO, BUY
                rec.route_ids = [Command.link(mto.id), Command.link(buy.id)] + [Command.link(r.id) for r in cross_docks]
            elif rec.ext_routes_type[:7] == 'Service':
                rec.detailed_type == 'service'

    @api.model_create_multi
    def create(self, val_list):
        recs = super().create(val_list)
        recs.set_routes_from_import_data()
        return recs

