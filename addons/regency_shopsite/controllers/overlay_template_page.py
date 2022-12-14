import io
import json
from base64 import b64encode, b64decode

from PIL import Image

from markupsafe import Markup
from odoo import http, Command
from odoo.exceptions import ValidationError
from odoo.http import request
from werkzeug.exceptions import Forbidden, NotFound

from odoo.addons.regency_shopsite.const import OVERLAY_PRODUCT_ID_URL_PARAMETER, VECTOR_FILE_FORMATS
from odoo.addons.regency_shopsite.image_tools import convert_vector_to_png, compute_image_data


class OverlayTemplatePage(http.Controller):

    @classmethod
    def _overlay_template_is_available_for_user(cls, overlay_template_id):
        overlay_template_hotel_ids = overlay_template_id.hotel_ids
        user_hotel_ids = request.env.user.hotel_ids
        if not user_hotel_ids or not overlay_template_hotel_ids \
                or not set(user_hotel_ids.ids).intersection(set(overlay_template_hotel_ids.ids)):
            return False
        return True

    @classmethod
    def _get_overlay_template_price_list(cls, overlay_template_id):
        active_hotel_id = request.env.user._active_hotel_id()
        overlay_template_is_available_for_hotel = active_hotel_id.id in overlay_template_id.hotel_ids.ids

        price_list = {}
        if overlay_template_is_available_for_hotel:
            overlay_template_price_item_ids = overlay_template_id.price_item_ids \
                .filtered(lambda x: x.pricelist_id.id == active_hotel_id.property_product_pricelist.id)
            overlay_template_price_item_ids = overlay_template_price_item_ids.sorted(key='min_quantity')
            price_list = {
                x['id']: {
                    'id': x['id'],
                    'price': x['fixed_price'],
                    'quantity': x['min_quantity'],
                    'totalPrice': round(x['fixed_price'] * x['min_quantity'], 2)
                } for x in overlay_template_price_item_ids.read(['id', 'fixed_price', 'min_quantity'])
            }
        return price_list

    @classmethod
    def _create_overlay_product_preview_images(cls, overlay_product_id, preview_images_data):
        for image_with_overlay in preview_images_data:
            if not image_with_overlay.get('images', False):
                continue
            overlay_position_id = request.env['overlay.position'].sudo().browse(
                image_with_overlay['overlayPositionId']).exists()
            if not overlay_position_id:
                continue
            back_image_id = request.env['product.image'].browse(image_with_overlay['backgroundImageId'])
            back_image = Image.open(io.BytesIO(b64decode(back_image_id.image_1920)))
            width = image_with_overlay['backgroundImageSize']['width']
            height = image_with_overlay['backgroundImageSize']['height']
            back_image = back_image.resize((width, height))
            for image_data in image_with_overlay['images']:
                image = Image.open(io.BytesIO(b64decode(image_data['data'].encode())))
                scale = image_data['scale']
                image = image.resize((int(image.width * scale), int(image.height * scale)))
                x = image_data['size']['x']
                y = image_data['size']['y']
                back_image.paste(image, (int(x), int(y)), image)

            result_image = io.BytesIO()
            back_image.save(result_image, format='PNG')

            request.env['overlay.product.image'].sudo().create({
                'image': b64encode(result_image.getvalue()),
                'overlay_position_id': overlay_position_id.id,
                'overlay_product_id': overlay_product_id.id,
            })

    @classmethod
    def copy_overlay_product_area_images(cls, area_images):
        new_area_images = request.env['overlay.product.area.image'].sudo()
        for area_image in area_images:
            new_area_image = area_image.copy()
            new_area_image.overlay_product_id = False
            new_area_images += new_area_image
        return new_area_images

    @classmethod
    def save_overlay_product(cls, overlay_template_id, overlay_product_name, attribute_list=None,
                             overlay_area_list=None, preview_images_data=None, overlay_product_id=None,
                             overlay_product_was_changed=None, duplicate_overlay_product_id=None):
        overlay_template_id = request.env['overlay.template'].browse(overlay_template_id).exists()
        if not overlay_template_id:
            raise ValidationError('Overlay template does not exists!')
        product_template_id = overlay_template_id.product_template_id

        sol_with_overlay_product = False
        old_overlay_product = False
        old_overlay_product_area_image_by_backend = False
        overlay_product = False
        if overlay_product_id:
            old_overlay_product = request.env['overlay.product'].sudo().browse(overlay_product_id).exists()
            if not old_overlay_product:
                raise ValidationError(f'Overlay product with ID={overlay_product_id} does not exists!')
            if old_overlay_product.product_id:
                sol_with_overlay_product = request.env['sale.order.line'].sudo().search(
                    [('product_id', '=', old_overlay_product.product_id.id)])
            if sol_with_overlay_product and overlay_product_was_changed:
                old_overlay_product.active = False
                backend_area_images = old_overlay_product.overlay_product_area_image_ids. \
                    filtered(lambda x: not x.added_on_website)
                old_overlay_product_area_image_by_backend = cls.copy_overlay_product_area_images(
                    backend_area_images)
            else:
                overlay_product = old_overlay_product
                overlay_product.name = overlay_product_name
                if overlay_product_was_changed:
                    overlay_product.overlay_product_image_ids.unlink()
                    overlay_product.overlay_product_area_image_ids.filtered(lambda x: x.added_on_website).unlink()
                    overlay_product.product_id = False

        if not overlay_product:
            overlay_product = request.env['overlay.product'].sudo().create({
                'name': overlay_product_name,
                'overlay_template_id': overlay_template_id.id,
            })

        if not old_overlay_product_area_image_by_backend and duplicate_overlay_product_id:
            backend_area_images = request.env['overlay.product.area.image'].sudo().search(
                [('overlay_product_id', '=', duplicate_overlay_product_id), ('added_on_website', '=', False)])
            old_overlay_product_area_image_by_backend = cls.copy_overlay_product_area_images(backend_area_images)

        if overlay_product and old_overlay_product_area_image_by_backend:
            old_overlay_product_area_image_by_backend.overlay_product_id = overlay_product.id

        product_template_attribute_value_ids = []
        if not old_overlay_product or overlay_product_was_changed:
            for attribute in attribute_list:
                attribute_id = attribute['attribute_id']
                product_template_attribute_line_id = product_template_id.attribute_line_ids \
                    .filtered(lambda x: x.attribute_id.id == attribute_id)
                if not product_template_attribute_line_id:
                    raise ValidationError(f'Attribute with id "{attribute_id}" does not exists in the product!')
                value_id = attribute['value_id']
                product_template_attribute_value_id = product_template_attribute_line_id.product_template_value_ids \
                    .filtered(lambda x: x.product_attribute_value_id.id == value_id)
                if not product_template_attribute_line_id:
                    raise ValidationError(f'Attribute value with id "{attribute_id}" does not exists in the product!')
                product_template_attribute_value_ids.append(product_template_attribute_value_id.id)

            overlay_attribute_id = request.env.ref('regency_shopsite.overlay_attribute')
            product_template_overlay_attribute_value_id = product_template_id.attribute_line_ids \
                .filtered(lambda x: x.attribute_id.id == overlay_attribute_id.id) \
                .product_template_value_ids \
                .filtered(lambda x: x.product_attribute_value_id.overlay_template_id.id == overlay_template_id.id)
            if not product_template_overlay_attribute_value_id:
                raise ValidationError(f'Product {product_template_id.name} does not have overlay attribute!')
            product_template_attribute_value_ids.append(product_template_overlay_attribute_value_id.id)
            overlay_product.product_template_attribute_value_ids = [Command.set(product_template_attribute_value_ids)]

            cls._create_overlay_product_preview_images(overlay_product, preview_images_data)

            for item in overlay_area_list.values():
                overlay_position_id = item.get('overlayPositionId', False)
                if overlay_position_id:
                    overlay_position_id = request.env['overlay.position'].sudo().browse(overlay_position_id).exists()
                if not overlay_position_id:
                    continue

                area_list = item.get('areaList', {})
                if not area_list:
                    continue
                for area in area_list.values():
                    data = area.get('data', [])
                    if not data:
                        continue
                    area_index = area.get('index')
                    for obj in data:
                        image_data = obj.get('image', False)
                        if not image_data:
                            continue
                        image_data_split = image_data.split(',')
                        image_type = image_data_split[0].split(':')[1].split(';')[0]
                        image_bytes = image_data_split[1]
                        area_object_index = obj.get('index')
                        area_image_id = request.env['overlay.product.area.image'].sudo().create({
                            'image': image_bytes.encode(),
                            'image_type': image_type,
                            'image_extension': obj.get('imageExtension', ''),
                            'overlay_position_id': overlay_position_id.id,
                            'area_index': area_index,
                            'area_object_index': area_object_index,
                            'overlay_product_id': overlay_product.id,
                            'added_on_website': True,
                        })
                        obj['areaImageId'] = area_image_id.id
                        del obj['image']
            overlay_product.area_list_data = overlay_area_list

        overlay_product._set_update_info()

        return overlay_product, product_template_attribute_value_ids

    @classmethod
    def get_base_overlay_product_data(cls, overlay_product_id):
        return {
            'id': overlay_product_id.id if overlay_product_id else False,
            'active': overlay_product_id.active if overlay_product_id else False,
            'name': overlay_product_id.name if overlay_product_id else False,
            'positionImagesUrls': {
                x.overlay_position_id.id: f'/web/content/{x._name}/{x.id}/image'
                for x in overlay_product_id.overlay_product_image_ids
            }
        }

    @http.route(['/shop/<model("overlay.template"):overlay_template_id>'], type='http', auth='user', website=True)
    def overlay_template_page(self, overlay_template_id, **kwargs):
        if not overlay_template_id or not overlay_template_id.exists():
            return request.render('website.page_404')
        if not self._overlay_template_is_available_for_user(overlay_template_id):
            return request.render('website.page_404')
        if not overlay_template_id.website_published:
            return request.render('website.page_404')

        overlay_template_id = overlay_template_id.sudo()
        product_template_id = overlay_template_id.product_template_id
        if not product_template_id or not product_template_id.exists():
            return request.render('website.page_404')

        active_hotel_id = request.env.user._active_hotel_id()
        overlay_template_is_available_for_hotel = active_hotel_id.id in overlay_template_id.hotel_ids.ids

        overlay_attribute_id = request.env.ref('regency_shopsite.overlay_attribute')
        customization_attribute_id = request.env.ref('regency_shopsite.customization_attribute')
        color_attribute_id = request.env.ref('regency_shopsite.color_attribute')

        overlay_template_attribute_ids = overlay_template_id.overlay_attribute_line_ids.mapped('attribute_id')
        product_template_attribute_ids = product_template_id.attribute_line_ids.mapped('attribute_id')

        attribute_list = {}
        for attribute_id in product_template_attribute_ids:
            if attribute_id.id in [overlay_attribute_id.id, customization_attribute_id.id]:
                continue
            if attribute_id.id not in overlay_template_attribute_ids.ids:
                value_ids = product_template_id.attribute_line_ids.filtered(
                    lambda x: x.attribute_id.id == attribute_id.id).value_ids
            else:
                value_ids = overlay_template_id.overlay_attribute_line_ids.filtered(
                    lambda x: x.attribute_id.id == attribute_id.id).value_ids
            url_attribute_value_id_str = kwargs.get(attribute_id.name.lower(), False)
            selected_value_id = False
            if url_attribute_value_id_str:
                try:
                    url_attribute_value_id = int(url_attribute_value_id_str)
                    if url_attribute_value_id in value_ids.ids:
                        selected_value_id = url_attribute_value_id
                except (ValueError, TypeError):
                    pass
            if not selected_value_id:
                selected_value_id = value_ids[0].id
            values = {
                x['id']: {
                    'id': x['id'],
                    'name': x['name'],
                    'color': x['html_color'],
                } for x in value_ids.read(['id', 'name', 'html_color'])
            }
            attribute_list[attribute_id.id] = {
                'id': attribute_id.id,
                'name': attribute_id.name,
                'valueList': values,
                'selectedValueId': selected_value_id,
            }

        price_list = self._get_overlay_template_price_list(overlay_template_id)

        overlay_template_page_data = {
            'overlayTemplate': {
                'isAvailableForActiveHotel': overlay_template_is_available_for_hotel,
                'id': overlay_template_id.id,
                'name': overlay_template_id.name,
                'hotelIds': overlay_template_id.hotel_ids.ids,
                'positionsData': overlay_template_id.areas_data or {},
                'exampleImageUrl':
                    f'/web/image?model=overlay.template&id={overlay_template_id.id}'
                    f'&field=example_image&width=3840&height=2160'
                    if overlay_template_id.example_image else False,
            },
            'productTemplateId': product_template_id.id,
            'productName': product_template_id.name,
            'productDescription': product_template_id.description_sale,
            'attributeList': attribute_list,
            'areasImageAttributeId': overlay_template_id.areas_image_attribute_id.id,
            'colorAttributeId': color_attribute_id.id,
            'priceList': price_list,
            'options': {
                'overlayProductIdUrlParameter': OVERLAY_PRODUCT_ID_URL_PARAMETER,
            }
        }

        overlay_product_id = False
        url_overlay_product_id = kwargs.get(OVERLAY_PRODUCT_ID_URL_PARAMETER, False)
        if url_overlay_product_id:
            try:
                url_overlay_product_id = int(url_overlay_product_id)
                overlay_product_id = request.env['overlay.product'].sudo().with_context(active_test=False).search(
                    [('id', '=', url_overlay_product_id), ('overlay_template_id', '=', overlay_template_id.id)])
            except (ValueError, TypeError):
                pass
        if overlay_product_id:
            product_id = overlay_product_id.product_id
            overlay_product_area_image_list = {}
            for rec in overlay_product_id.overlay_product_area_image_ids:
                if not rec.overlay_position_id:
                    continue
                if not overlay_product_area_image_list.get(rec.overlay_position_id.id):
                    overlay_product_area_image_list[rec.overlay_position_id.id] = {}
                if not overlay_product_area_image_list[rec.overlay_position_id.id].get(rec.area_index):
                    overlay_product_area_image_list[rec.overlay_position_id.id][rec.area_index] = {}
                overlay_product_area_image_list[rec.overlay_position_id.id][rec.area_index][
                    rec.area_object_index] = rec.id
                for attribute in attribute_list.values():
                    overlay_product_attribute_value_id = overlay_product_id.product_template_attribute_value_ids\
                        .filtered(lambda x: x.attribute_id.id == attribute['id']).product_attribute_value_id
                    if overlay_product_attribute_value_id:
                        attribute['selectedValueId'] = overlay_product_attribute_value_id.id
            overlay_template_page_data.update({
                'overlayProduct': {
                    **self.get_base_overlay_product_data(overlay_product_id),
                    'areaList': overlay_product_id.area_list_data or {},
                    'areaImageList': overlay_product_area_image_list,
                },
                'productId': product_id.id,
                'attributeList': attribute_list,
            })

        return request.render('regency_shopsite.overlay_template_page', {
            'overlay_template_page_data': Markup(json.dumps(overlay_template_page_data)),
        })

    @http.route(['/shop/overlay_template/save'], type='json', auth='user', methods=['POST'], website=True,
                csrf=False)
    def overlay_product_save(self, overlay_template_id, overlay_product_name, attribute_list=None,
                             overlay_area_list=None, preview_images_data=None, overlay_product_id=None,
                             overlay_product_was_changed=None, duplicate_overlay_product_id=None, **kwargs):
        overlay_product, product_template_attribute_value_ids = self.save_overlay_product(
            overlay_template_id, overlay_product_name,
            attribute_list=attribute_list,
            overlay_area_list=overlay_area_list,
            preview_images_data=preview_images_data,
            overlay_product_id=overlay_product_id,
            overlay_product_was_changed=overlay_product_was_changed,
            duplicate_overlay_product_id=duplicate_overlay_product_id,
        )
        return self.get_base_overlay_product_data(overlay_product)

    @http.route(['/shop/overlay_template/delete'], type='json', auth='user', methods=['POST'], website=True,
                csrf=False)
    def overlay_product_delete(self, overlay_product_id):
        overlay_product = request.env['overlay.product'].sudo().browse(overlay_product_id).exists()
        if not overlay_product:
            raise ValidationError(f'Overlay product with ID={overlay_product_id} does not exists!')
        overlay_template_id = overlay_product.overlay_template_id
        if self._overlay_template_is_available_for_user(overlay_template_id):
            sol_with_overlay_product = False
            if overlay_product.product_id:
                sol_with_overlay_product = request.env['sale.order.line'].sudo().search(
                    [('product_id', '=', overlay_product.product_id.id)])
            if sol_with_overlay_product:
                overlay_product.active = False
            else:
                overlay_product.sudo().unlink()
            return True
        return False

    @http.route(['/shop/overlay_template/price_list'], type='json', auth='user', methods=['POST'], website=True)
    def overlay_template_price_list(self, overlay_template_id, **kwargs):
        overlay_template_id = request.env['overlay.template'].sudo().browse(overlay_template_id).exists()
        if not overlay_template_id or not self._overlay_template_is_available_for_user(overlay_template_id):
            return False
        return {
            'priceList': self._get_overlay_template_price_list(overlay_template_id),
        }

    @http.route(['/shop/area_image'], type='json', auth="user", website=True)
    def overlay_product_area_image(self, overlay_product_area_image_id):
        overlay_product_area_image = request.env['overlay.product.area.image'].sudo()\
            .browse(overlay_product_area_image_id)

        if not overlay_product_area_image:
            raise NotFound()

        if not self._overlay_template_is_available_for_user(
                overlay_product_area_image.overlay_product_id.overlay_template_id):
            raise Forbidden()

        image = overlay_product_area_image.image
        image_type = overlay_product_area_image.image_type

        if overlay_product_area_image.image_type in VECTOR_FILE_FORMATS:
            data = {
                'vector': compute_image_data(image.decode(), image_type),
                'bitmap': convert_vector_to_png(image.decode(), image_type),
            }
        else:
            data = {
                'bitmap': compute_image_data(image.decode(), image_type),
            }

        return data

    @http.route(['/shop/convert_area_image'], type='json', auth='user', methods=['POST'], website=True)
    def convert_area_image(self, file_data, file_type, **kwargs):
        return convert_vector_to_png(file_data, file_type)
