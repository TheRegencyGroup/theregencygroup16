import json

from markupsafe import Markup
from odoo import _, http, Command
from odoo.http import request


class OverlayTemplatePage(http.Controller):

    @http.route(['/shopsite/<model("overlay.template"):overlay_template_id>'], type='http', auth='user', website=True)
    def overlay_template_page(self, overlay_template_id, **kwargs):
        if not overlay_template_id or not overlay_template_id.exists():
            return request.render('website.page_404')

        product_template_id = overlay_template_id.product_template_id
        if not product_template_id or not product_template_id.exists():
            return request.render('website.page_404')

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

        overlay_template_price_item_ids = overlay_template_id.price_item_ids
        overlay_template_price_item_ids = overlay_template_price_item_ids.sorted(key='min_quantity')
        price_list = {
            x['id']: {
                'id': x['id'],
                'price': x['fixed_price'],
                'quantity': x['min_quantity'],
            } for x in overlay_template_price_item_ids.read(['id', 'fixed_price', 'min_quantity'])
        }

        overlay_template_page_data = {
            'overlayTemplateName': overlay_template_id.name,
            'productName': product_template_id.name,
            'productDescription': product_template_id.description_sale,
            'attributeList': attribute_list,
            'overlayTemplateAreasData': json.loads(overlay_template_id.areas_json),
            'colorAttributeId': color_attribute_id.id,
            'sizeAttributeId': size_attribute_id.id,
            'priceList': price_list,
        }

        return request.render('regency_shopsite.overlay_template_page', {
            'overlay_template_page_data': Markup(json.dumps(overlay_template_page_data)),
        })
