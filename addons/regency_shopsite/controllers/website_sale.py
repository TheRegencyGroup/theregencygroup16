import base64
import io
import json

import PIL.Image as Image
from odoo.tools.image import image_data_uri
from markupsafe import Markup
from odoo import _, http, Command, api
from odoo.http import request
from odoo.addons.website_sale.controllers.main import TableCompute, WebsiteSale


class WebsiteSaleRegency(WebsiteSale):

    @http.route(['/shopsite_test'], type='http', auth="user", website=True)
    def shopsite_test(self, **kwargs):
        return request.render('regency_shopsite.shopsite_page_test', {})

    @http.route(['/shopsite/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def shopsite_cart_update_json(self, overlay_template_id, attribute_list, qty, **kwargs):
        product_id = 1
        self.cart_update_json(product_id=product_id, display=False)

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True,
                         images_with_overlay=None, **kw):
        res = super().cart_update_json(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty,
                                       display=display, **kw)
        so_line_id = res.get('line_id', False)
        if so_line_id and images_with_overlay:
            so_line = request.env['sale.order.line'].browse(so_line_id)
            for image_with_overlay in images_with_overlay:
                if image_with_overlay['background_image_model'] == 'product.template':
                    back_image_id = so_line.product_template_id.image_1920
                else:
                    back_image_id = request.env['product.image'].browse(
                        image_with_overlay['background_image_id']).image_1920
                back_image = Image.open(io.BytesIO(base64.b64decode(back_image_id)))
                width = image_with_overlay['background_image_size']['width']
                height = image_with_overlay['background_image_size']['height']
                delta_x = 0
                delta_y = 0
                if back_image.width >= back_image.height:
                    height = int(width * (back_image.height / back_image.width))
                    delta_y = int((image_with_overlay['background_image_size']['height'] - height) / 2)
                else:
                    width = int(height * (back_image.width / back_image.height))
                    delta_x = int((image_with_overlay['background_image_size']['width'] - width) / 2)
                back_image = back_image.resize((width, height))
                for image_data in image_with_overlay['images']:
                    image = Image.open(io.BytesIO(base64.b64decode(image_data['data'].encode())))
                    x = image_data['size']['x'] - delta_x
                    y = image_data['size']['y'] - delta_y
                    back_image.paste(image, (int(x), int(y)), image)

                result_image = io.BytesIO()
                back_image.save(result_image, format='PNG')
                request.env['product.image'].sudo().create({
                    'name': image_with_overlay['position_name'],
                    'image_1920': base64.b64encode(result_image.getvalue()),
                    'sale_order_line_id': so_line.id,
                })
        return res

    @http.route([
        '/shop',
    ], type='http', auth="user", website=True, sitemap=WebsiteSale.sitemap_shop)
    def shop(self, **kwargs):
        values = {
            'shopsite_catalog_data': Markup(json.dumps(self._get_overlay_templates_data()))
        }
        return request.render('regency_shopsite.shopsite_catalog', values)

    @http.route("/order_history", type='http', auth="user", website=True)
    def order_history(self, **kwargs):
        values = {}
        return request.render('regency_shopsite.order_history', values)

    @api.model
    def _get_overlay_templates_data(self) -> list:
        data = []
        for ot in self._get_overlay_templates():
            ot_val = {'name': ot.name,
                      'main_image_url': ot.get_main_image_url()
                      }
            data.append(ot_val)
        return data

    @api.model
    def _get_overlay_templates(self):
        return request.env['overlay.template'].search([])

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
