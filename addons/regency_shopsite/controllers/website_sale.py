from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

from odoo.addons.regency_shopsite.controllers.overlay_template_page import OverlayTemplatePage

DEFAULT_PRODUCT_QTY_PEAR_PAGE = 6


class WebsiteSaleRegency(WebsiteSale):

    @http.route(['/shop/cart/update_json/overlay'], type='json', auth='user', methods=['POST'], website=True,
                csrf=False)
    def shopsite_cart_update_json(self, qty, overlay_template_id=None, attribute_list=None, overlay_product_id=None,
                                  overlay_product_name=None, overlay_area_list=None, preview_images_data=None,
                                  **kwargs):
        if not overlay_product_id:
            overlay_product_id, product_template_attribute_value_ids = OverlayTemplatePage.create_overlay_product(
                overlay_template_id, attribute_list, overlay_product_name, overlay_area_list, preview_images_data)
        else:
            overlay_product_id = request.env['overlay.product'].sudo().browse(overlay_product_id).exists()
            if not overlay_product_id:
                raise ValidationError(f'Overlay product does not exists!"')
            product_template_attribute_value_ids = overlay_product_id.product_template_attribute_value_ids.ids
        product_template_id = overlay_product_id.product_tmpl_id

        if not overlay_product_id.product_id:
            customize_attribute_id = request.env.ref('regency_shopsite.customization_attribute')
            product_template_customize_attribute_value_id = product_template_id.attribute_line_ids \
                .filtered(lambda x: x.attribute_id.id == customize_attribute_id.id) \
                .product_template_value_ids \
                .filtered(lambda x: x.product_attribute_value_id.overlay_product_id.id == overlay_product_id.id)
            if not product_template_customize_attribute_value_id:
                raise ValidationError(f'Product {product_template_id.name} does not have customize attribute!')
            product_template_attribute_value_ids.append(product_template_customize_attribute_value_id.id)

            product_id = product_template_id.create_product_variant(product_template_attribute_value_ids)
            if not product_id:
                raise ValidationError('Error when created product variant!')
        else:
            product_id = overlay_product_id.product_id.id

        self.cart_update_json(product_id=product_id, add_qty=qty, display=False)
        return {
            'cartData': request.website._get_cart_data(),
            'overlayProductData': OverlayTemplatePage.get_overlay_product_data(overlay_product_id),
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
