from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_order_line_values(self, product_id, quantity, linked_line_id=False, no_variant_attribute_values=None,
                                   product_custom_attribute_values=None, **kwargs):
        result = super()._prepare_order_line_values(product_id, quantity, linked_line_id, no_variant_attribute_values,
                                                    product_custom_attribute_values, **kwargs)
        if 'delivery_partner_id' in kwargs:
            result['delivery_partner_id'] = kwargs['delivery_partner_id']
        if 'price_list_id' in kwargs:
            result['price_list_id'] = kwargs['price_list_id']
        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    image_with_overlay_ids = fields.One2many('product.image', 'sale_order_line_id', string='Images with overlay')
    overlay_template_id = fields.Many2one('overlay.template', compute='_compute_overlay_template_id')
    price_list_id = fields.Many2one('product.pricelist', default=lambda self: self.order_id.pricelist_id)

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        res._link_overlay_to_product()
        return res

    def _link_overlay_to_product(self):
        for line in self:
            attribute_ids = line.product_template_attribute_value_ids.mapped('attribute_id')
            if self.env.ref('regency_shopsite.overlay_attribute') in attribute_ids and self.env.ref(
                    'regency_shopsite.customization_attribute') in attribute_ids:
                for overlay_product in line.product_template_id.overlay_template_ids.mapped('overlay_product_ids'):
                    overlay_product.product_id = line.product_id.id

    @api.depends('product_id', 'product_id.product_template_attribute_value_ids')
    def _compute_overlay_template_id(self):
        overlay_attribute_id = self.env.ref('regency_shopsite.overlay_attribute')
        for line in self:
            product_template_attribute_value_ids = line.product_id.product_template_attribute_value_ids
            if overlay_attribute_id.id in product_template_attribute_value_ids.mapped('attribute_id').ids:
                line.overlay_template_id = product_template_attribute_value_ids \
                    .filtered(lambda x: x.attribute_id.id == overlay_attribute_id.id) \
                    .product_attribute_value_id.overlay_template_id.id
            else:
                line.overlay_template_id = False

    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'price_list_id')
    def _compute_pricelist_item_id(self):
        for line in self:
            if not line.product_id or line.display_type or not line.order_id.pricelist_id:
                line.pricelist_item_id = False
            else:
                line.pricelist_item_id = line.price_list_id._get_product_rule(
                    line.product_id,
                    line.product_uom_qty or 1.0,
                    uom=line.product_uom,
                    date=line.order_id.date_order,
                ) if line.price_list_id else line.order_id.pricelist_id._get_product_rule(
                    line.product_id,
                    line.product_uom_qty or 1.0,
                    uom=line.product_uom,
                    date=line.order_id.date_order,
                )

    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'price_list_id')
    def _compute_price_unit(self):
        for line in self:
            # check if there is already invoiced amount. if so, the price shouldn't change as it might have been
            # manually edited
            if line.qty_invoiced > 0:
                continue
            if not line.product_uom or not line.product_id or not line.order_id.pricelist_id:
                line.price_unit = 0.0
            else:
                price = line.with_company(line.company_id)._get_display_price()
                line.price_unit = line.product_id._get_tax_included_unit_price(
                    line.company_id,
                    line.order_id.currency_id,
                    line.order_id.date_order,
                    'sale',
                    fiscal_position=line.order_id.fiscal_position_id,
                    product_price_unit=price,
                    product_currency=line.currency_id
                )

    def action_open_sale_order_line_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line',
            'res_id': self.id,
            'view_mode': 'form',
            'views': [(False, "form")],
        }
