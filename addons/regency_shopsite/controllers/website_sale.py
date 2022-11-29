from odoo import _, http, Command
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

from odoo.addons.regency_shopsite.controllers.overlay_template_page import OverlayTemplatePage

DEFAULT_PRODUCT_QTY_PEAR_PAGE = 6


class WebsiteSaleRegency(WebsiteSale):

    @http.route(['/shop/cart/update_json/overlay'], type='json', auth='user', methods=['POST'], website=True,
                csrf=False)
    def shopsite_cart_update_json(self, qty, overlay_template_id=None, attribute_list=None, overlay_product_id=None,
                                  overlay_product_name=None, overlay_area_list=None, preview_images_data=None,
                                  overlay_product_was_changed=None, **kwargs):
        if not overlay_product_id or overlay_product_was_changed:
            overlay_product, product_template_attribute_value_ids = OverlayTemplatePage.save_overlay_product(
                overlay_template_id, overlay_product_name,
                attribute_list=attribute_list,
                overlay_area_list=overlay_area_list,
                preview_images_data=preview_images_data,
                overlay_product_id=overlay_product_id,
                overlay_product_was_changed=overlay_product_was_changed)
        else:
            overlay_product = request.env['overlay.product'].sudo().browse(overlay_product_id).exists()
            if not overlay_product:
                raise ValidationError(f'Overlay product does not exists!"')
            product_template_attribute_value_ids = overlay_product.product_template_attribute_value_ids.ids
        product_template_id = overlay_product.product_tmpl_id

        if not overlay_product.product_id:
            customize_attribute_id = request.env.ref('regency_shopsite.customization_attribute')
            product_template_customize_attribute_value_id = product_template_id.attribute_line_ids \
                .filtered(lambda x: x.attribute_id.id == customize_attribute_id.id) \
                .product_template_value_ids \
                .filtered(lambda x: x.product_attribute_value_id.overlay_product_id.id == overlay_product.id)
            if not product_template_customize_attribute_value_id:
                raise ValidationError(f'Product {product_template_id.name} does not have customize attribute!')
            product_template_attribute_value_ids.append(product_template_customize_attribute_value_id.id)

            product_id = product_template_id.create_product_variant(product_template_attribute_value_ids)
            if not product_id:
                raise ValidationError('Error when created product variant!')
        else:
            product_id = overlay_product.product_id.id

        hotel_id = request.env.user._active_hotel_id()
        price_list_id = hotel_id.property_product_pricelist.id
        self.cart_update_json(product_id=product_id, add_qty=qty, display=False,
                              delivery_partner_id=hotel_id.id if hotel_id else False, price_list_id=price_list_id)
        return {
            'cartData': request.website._get_cart_data(),
            'overlayProductData': OverlayTemplatePage.get_overlay_product_data(overlay_product),
        }

    @http.route([
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',
    ], type='http', auth='user')
    def shop(self, **post):
        return request.render('website.page_404')

    @http.route(['/shop/cart/reorder'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def reorder_so(self, sale_order_line_id, **kw):
        sale_order_line = request.env['sale.order.line'].browse(sale_order_line_id)
        data = {
            'quantity': sale_order_line.product_uom_qty,
            'variant_values': sale_order_line.product_template_attribute_value_ids.ids,
            'force_create': True
        }
        return self.cart_update_json(product_id=sale_order_line.product_id.id, add_qty=sale_order_line.product_uom_qty,
                                     kw=data)

    @http.route(['/shop/cart/save_delivery_address'],
                type='json', auth="user", methods=['POST'], website=True, csrf=False)
    def update_sale_order_line_delivery_address(self, sale_order_line_id, delivery_address_id, **kw):
        sol = self._get_sol_id_from_current_cart(sale_order_line_id)
        sol.write({'delivery_address_id': delivery_address_id})

    @http.route(['/shop/cart/add_new_address'],
                type='json', auth="user", methods=['POST'], website=True, csrf=False)
    def create_and_link_delivery_address(self, sale_order_line_id, address_name: str, **kw):
        sol = self._get_sol_id_from_current_cart(sale_order_line_id)
        if sol:
            new_address_vals = {'name': address_name,
                                'type': 'delivery',
                                'parent_id': sol.delivery_partner_id.id,
                                **kw
                                }
            new_address = sol.env['res.partner'].create(new_address_vals)
            sol.write({'delivery_address_id': new_address.id})

    @http.route(['/shop/cart/get_delivery_addresses_data'], type='json', methods=['POST'], auth='user', website=True)
    def get_delivery_address_data(self, sale_order_line_id):
        sol = self._get_sol_id_from_current_cart(sale_order_line_id)
        return sol._get_delivery_data()

    @http.route(['/shop/submit_cart'], type='json', auth='user', methods=['POST'], website=True, csrf=False)
    def submit_cart(self):
        order = request.website.sale_get_order()
        if not order or order.state != 'draft':
            return False
        order.submit_so_and_send_notify()
        return True

    @http.route(['/shop/cart/submit_customer_comment'], type='json', auth='user', methods=['POST'], website=True, csrf=False)
    def submit_cart_customer_comment(self, customer_comment):
        order = request.website.sale_get_order()
        if not order or order.state != 'draft':
            return False
        return order.write({'customer_comment': customer_comment or ''})

    @staticmethod
    def _get_sol_id_from_current_cart(sale_order_line_id):
        order = request.website.sale_get_order(force_create=False)
        order = order.with_company(order.company_id)  # from core, don't know why it is used in such way
        if not order or order.state != 'draft':
            raise UserError('No draft sale order was found.')
        sol = order.order_line.filtered_domain([('id', '=', sale_order_line_id)])
        if not sol:
            raise ValueError(f"There is no sale order line 'id: {sale_order_line_id}' in the order 'id: {order.id}'.")
        return sol
