import base64
import io
import json
import time
from functools import reduce

import PIL.Image as Image
from markupsafe import Markup
from odoo import _, http, api, Command
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

from odoo.addons.regency_shopsite.controllers.overlay_template_page import OverlayTemplatePage

DEFAULT_PRODUCT_QTY_PEAR_PAGE = 6


class WebsiteSaleRegency(WebsiteSale):

    @http.route(['/shop/cart/update_json/overlay'], type='json', auth='user', methods=['POST'], website=True, csrf=False)
    def shopsite_cart_update_json(self, qty, overlay_template_id=None, attribute_list=None, overlay_product_id=None,
                                  overlay_product_name=None, overlay_area_list=None, **kwargs):
        if not overlay_product_id:
            overlay_product_id, product_template_attribute_value_ids = OverlayTemplatePage.create_overlay_product(
                overlay_template_id, attribute_list, overlay_product_name, overlay_area_list)
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

    # @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    # def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True,
    #                      images_with_overlay=None, **kw):
    #     res = super().cart_update_json(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty,
    #                                    display=display, **kw)
    #     so_line_id = res.get('line_id', False)
    #     if so_line_id and images_with_overlay:
    #         so_line = request.env['sale.order.line'].browse(so_line_id)
    #         for image_with_overlay in images_with_overlay:
    #             if image_with_overlay['background_image_model'] == 'product.template':
    #                 back_image_id = so_line.product_template_id.image_1920
    #             else:
    #                 back_image_id = request.env['product.image'].browse(
    #                     image_with_overlay['background_image_id']).image_1920
    #             back_image = Image.open(io.BytesIO(base64.b64decode(back_image_id)))
    #             width = image_with_overlay['background_image_size']['width']
    #             height = image_with_overlay['background_image_size']['height']
    #             delta_x = 0
    #             delta_y = 0
    #             if back_image.width >= back_image.height:
    #                 height = int(width * (back_image.height / back_image.width))
    #                 delta_y = int((image_with_overlay['background_image_size']['height'] - height) / 2)
    #             else:
    #                 width = int(height * (back_image.width / back_image.height))
    #                 delta_x = int((image_with_overlay['background_image_size']['width'] - width) / 2)
    #             back_image = back_image.resize((width, height))
    #             for image_data in image_with_overlay['images']:
    #                 image = Image.open(io.BytesIO(base64.b64decode(image_data['data'].encode())))
    #                 x = image_data['size']['x'] - delta_x
    #                 y = image_data['size']['y'] - delta_y
    #                 back_image.paste(image, (int(x), int(y)), image)
    #
    #             result_image = io.BytesIO()
    #             back_image.save(result_image, format='PNG')
    #             request.env['product.image'].sudo().create({
    #                 'name': image_with_overlay['position_name'],
    #                 'image_1920': base64.b64encode(result_image.getvalue()),
    #                 'sale_order_line_id': so_line.id,
    #             })
    #     return res

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
