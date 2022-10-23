import base64
import io
import json

from markupsafe import Markup
from odoo import http, Command
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.regency_shopsite.const import OVERLAY_PRODUCT_ID_URL_PARAMETER


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
            overlay_template_price_item_ids = overlay_template_id.price_item_ids\
                .filtered(lambda x: x.pricelist_id.id == active_hotel_id.property_product_pricelist.id)
            overlay_template_price_item_ids = overlay_template_price_item_ids.sorted(key='min_quantity')
            price_list = {
                x['id']: {
                    'id': x['id'],
                    'price': x['fixed_price'],
                    'quantity': x['min_quantity'],
                } for x in overlay_template_price_item_ids.read(['id', 'fixed_price', 'min_quantity'])
            }
        return price_list

    @classmethod
    def get_overlay_product_data(cls, overlay_product_id):
        return {
            'overlayProductId': overlay_product_id.id if overlay_product_id else False,
            'overlayProductName': overlay_product_id.name if overlay_product_id else False,
        }

    @classmethod
    def create_overlay_product(cls, overlay_template_id, attribute_list, overlay_product_name, overlay_area_list):
        overlay_template_id = request.env['overlay.template'].browse(overlay_template_id).exists()
        if not overlay_template_id:
            raise ValidationError('Overlay template does not exists!')
        product_template_id = overlay_template_id.product_template_id

        product_template_attribute_value_ids = []
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

        overlay_product_id = request.env['overlay.product'].sudo().create({
            'name': overlay_product_name,
            'overlay_template_id': overlay_template_id.id,
            'product_template_attribute_value_ids': [Command.set(product_template_attribute_value_ids)],
        })

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
                for obj in data:
                    image_bytes = obj.get('image', False)
                    if not image_bytes:
                        continue
                    request.env['overlay.product.area.image'].sudo().create({
                        'image': image_bytes.encode(),
                        'overlay_position_id': overlay_position_id.id,
                        'area_index': area.get('index'),
                        'area_object_index': obj.get('index'),
                        'overlay_product_id': overlay_product_id.id,
                    })
                    del obj['image']
        overlay_product_id.area_list_json = json.dumps(overlay_area_list)

        return overlay_product_id, product_template_attribute_value_ids

    @http.route(['/shop/<model("overlay.template"):overlay_template_id>'], type='http', auth='user', website=True)
    def overlay_template_page(self, overlay_template_id, **kwargs):
        if not overlay_template_id or not overlay_template_id.exists():
            return request.render('website.page_404')

        product_template_id = overlay_template_id.product_template_id
        if not product_template_id or not product_template_id.exists():
            return request.render('website.page_404')

        if not self._overlay_template_is_available_for_user(overlay_template_id):
            return request.render('website.page_404')

        active_hotel_id = request.env.user._active_hotel_id()
        overlay_template_is_available_for_hotel = active_hotel_id.id in overlay_template_id.hotel_ids.ids

        overlay_attribute_id = request.env.ref('regency_shopsite.overlay_attribute')
        customization_attribute_id = request.env.ref('regency_shopsite.customization_attribute')
        color_attribute_id = request.env.ref('regency_shopsite.color_attribute')
        size_attribute_id = request.env.ref('regency_shopsite.size_attribute')

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
            'overlayTemplateIsAvailableForActiveHotel': overlay_template_is_available_for_hotel,
            'overlayTemplateId': overlay_template_id.id,
            'overlayTemplateName': overlay_template_id.name,
            'overlayTemplateHotelIds': overlay_template_id.hotel_ids.ids,
            'productTemplateId': product_template_id.id,
            'productName': product_template_id.name,
            'productDescription': product_template_id.description_sale,
            'attributeList': attribute_list,
            'overlayTemplateAreasData': json.loads(overlay_template_id.areas_json),
            'colorAttributeId': color_attribute_id.id,
            'sizeAttributeId': size_attribute_id.id,
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
                overlay_product_id = request.env['overlay.product'].sudo().search(
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
            overlay_template_page_data.update({
                'overlayProductId': overlay_product_id.id,
                'overlayProductName': overlay_product_id.name if overlay_product_id else False,
                'overlayProductAreaList': json.loads(overlay_product_id.area_list_json) or {},
                'overlayProductAreaImageList': overlay_product_area_image_list,
                'overlayProductAreaImageModel': overlay_product_id.overlay_product_area_image_ids._name,
                'productId': product_id.id,
            })


        return request.render('regency_shopsite.overlay_template_page', {
            'overlay_template_page_data': Markup(json.dumps(overlay_template_page_data)),
        })

    @http.route(['/shop/overlay_template/save'], type='json', auth='user', methods=['POST'], website=True,
                csrf=False)
    def overlay_product_save(self, overlay_template_id, attribute_list, overlay_product_name, overlay_area_list,
                             **kwargs):
        overlay_product_id, product_template_attribute_value_ids = self.create_overlay_product(
            overlay_template_id, attribute_list, overlay_product_name, overlay_area_list)
        return self.get_overlay_product_data(overlay_product_id)

    @http.route(['/shop/overlay_template/price_list'], type='json', auth='user', methods=['POST'], website=True)
    def overlay_template_price_list(self, overlay_template_id, **kwargs):
        overlay_template_id = request.env['overlay.template'].sudo().browse(overlay_template_id).exists()
        if not overlay_template_id or not self._overlay_template_is_available_for_user(overlay_template_id):
            return False
        return {
            'priceList':  self._get_overlay_template_price_list(overlay_template_id),
        }
