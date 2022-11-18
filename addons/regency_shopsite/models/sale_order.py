import json

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            order.order_line._write_image_snapshot()
        return res

    def _prepare_order_line_values(self, product_id, quantity, linked_line_id=False, no_variant_attribute_values=None,
                                   product_custom_attribute_values=None, **kwargs):
        result = super()._prepare_order_line_values(product_id, quantity, linked_line_id, no_variant_attribute_values,
                                                    product_custom_attribute_values, **kwargs)
        if 'delivery_partner_id' in kwargs:
            result['delivery_partner_id'] = kwargs['delivery_partner_id']
        if 'price_list_id' in kwargs:
            result['price_list_id'] = kwargs['price_list_id']
        return result

    def submit_so_and_send_notify(self):
        self.state = 'sent'
        email_template = self.env.ref('regency_shopsite.so_submitted')
        for partner in self.team_id.message_follower_ids.mapped('partner_id'):
            email_values = {
                'recipient_ids': [(4, partner.id)]
            }
            action_id = self.env.ref('sale.action_quotations_with_onboarding')
            menu_id = self.env.ref('sale.menu_sale_quotations')
            data = {
                'partner_name': partner.name,
                'so_ref': self.name,
                'so_url': "/web#id=%d&action=%d&model=%s&view_type=form&menu_id=%d" % (
                    self.id, action_id.id, self._name, menu_id.id)
            }
            email_template.with_context(data).send_mail(self.id, email_values=email_values)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    overlay_template_id = fields.Many2one('overlay.template', compute='_compute_overlay_template_id')
    price_list_id = fields.Many2one('product.pricelist', string='Pricelist')
    image_snapshot = fields.Image('Product Image')
    image_snapshot_url = fields.Text(compute='_compute_image_snapshot_url')

    def _get_delivery_data(self):
        self.ensure_one()
        possible_addresses = [{'modelId': address.id,
                               'addressStr': address.name,
                               } for address in self.possible_delivery_address_ids]
        return json.dumps({'solId': self.id,
                           'currentDeliveryAddress': self.delivery_address_id.id,
                           'possibleDeliveryAddresses': possible_addresses,
                           })


    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        res._link_overlay_product_to_product_variant()
        return res

    def _write_image_snapshot(self):
        """should be called manually in right moment of business logic
        (if you really should synchronize image for order lines in existing order)"""
        for sol in self:
            overlay_product_id = sol.product_id.overlay_product_id
            if overlay_product_id:
                sol.image_snapshot = overlay_product_id._preview_image()
            else:
                sol.image_snapshot = False

    def _compute_image_snapshot_url(self):
        for sol in self:
            sol.image_snapshot_url = f'/web/image?model={sol._name}&id={sol.id}&field={"image_snapshot"}'

    def _link_overlay_product_to_product_variant(self):
        customization_attribute_id = self.env.ref('regency_shopsite.customization_attribute')
        for line in self:
            customization_value_id = line.product_id.product_template_attribute_value_ids\
                .filtered(lambda x: x.attribute_id.id == customization_attribute_id.id)\
                .product_attribute_value_id
            if not customization_value_id or not customization_value_id.overlay_product_id:
                continue
            customization_value_id.overlay_product_id.product_id = line.product_id.id

    @api.depends('product_id', 'product_id.product_template_attribute_value_ids')
    def _compute_overlay_template_id(self):
        # TODO not correct result - overlay.template without sales has sale_order_line_ids
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
        """
        overridden to get price rule for each sale order line from line.price_list_id if set,
        if not set, standard behaviour
        added price_list_id to depends list
        """
        for line in self:
            if not line.product_id or line.display_type or not line.order_id.pricelist_id:
                line.pricelist_item_id = False
            # start custom logic
            elif line.price_list_id:
                line.pricelist_item_id = line.price_list_id._get_product_rule(
                    line.product_id,
                    line.product_uom_qty or 1.0,
                    uom=line.product_uom,
                    date=line.order_id.date_order)
            # end custom logic
            else:
                line.pricelist_item_id = line.order_id.pricelist_id._get_product_rule(
                    line.product_id,
                    line.product_uom_qty or 1.0,
                    uom=line.product_uom,
                    date=line.order_id.date_order,
                )

    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'price_list_id')
    def _compute_price_unit(self):
        """
        overridden to add price_list_id to depends list
        """
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
