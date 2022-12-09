import logging
from odoo import fields, models, Command, api

_logger = logging.getLogger(__name__)


class Product(models.Model):
    _inherit = 'product.template'

    ext_overseas = fields.Char()
    ext_routes_type = fields.Char()
    ext_template_name = fields.Char()
    ext_qty_per_carton = fields.Float()
    ext_reorder_point = fields.Float()
    ext_all_customers = fields.Boolean()
    ext_customers = fields.One2many('res.partner', compute='_compute_ext_customers', inverse="_set_ext_customers")

    def after_import_update(self):
        self.search([]).create_packagings()

    def create_packagings(self):
        for rec in self.filtered(lambda x: x.ext_qty_per_carton > 0):
            rec.write({'packaging_ids': [Command.create({'name': 'Carton', 'qty': rec.ext_qty_per_carton})]})

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
                rec.detailed_type = 'service'

    def _compute_ext_customers(self):
        for rec in self:
            rec.ext_customers = rec.allowed_partner_ids.ids

    def _set_ext_customers(self):
        for rec in self:
            rec.allowed_partner_ids = [Command.link(x.id) for x in rec.ext_customers]

    @api.model_create_multi
    def create(self, val_list):
        recs = super().create(val_list)
        recs.set_routes_from_import_data()
        return recs

    def clear_imported(self):
        sql = """select pp.product_tmpl_id from ir_model_data
        left join product_product pp on pp.id = res_id
         where model = 'product.product' and module = '__import__'
        """
        self.env.cr.execute(sql)
        results = self.env.cr.fetchall()
        product_ids = [res[0] for res in results]
        products = self.env['product.template'].browse(product_ids)
        products.unlink()
