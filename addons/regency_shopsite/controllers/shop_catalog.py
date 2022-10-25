import json

from odoo.addons.http_routing.models.ir_http import slug
from markupsafe import Markup
from odoo import http
from odoo.fields import Datetime
from odoo.http import request

from odoo.addons.regency_shopsite.const import SHOP_CATALOG_ITEM_LIMIT, OVERLAY_PRODUCT_CATALOG_TAB_KEY, \
    OVERLAY_TEMPLATE_CATALOG_TAB_KEY, SHOP_CATALOG_TAB_MODELS, DEFAULT_SHOP_CATALOG_TAB_SORT, PAGE_URL_PARAMETER, \
    SHOP_CATALOG_TAB_URL_PARAMETER, OVERLAY_PRODUCT_ID_URL_PARAMETER


class ShopCatalog(http.Controller):

    @classmethod
    def _prepare_overlay_template_data(cls, overlay_template_ids):
        res = []
        for rec in overlay_template_ids:
            res.append({
                'overlayTemplateId': rec.id,
                'overlayTemplateName': rec.name,
                'productName': rec.product_template_id.name,
                'imageUrl': rec._preview_image_url(),
                'url': f'/shop/{slug(rec)}',
            })
        return res

    @classmethod
    def _prepare_overlay_product_data(cls, overlay_product_ids):
        res = []
        for rec in overlay_product_ids:
            res.append({
                'overlayProductId': rec.id,
                'overlayProductName': rec.name,
                'overlayTemplateId': rec.overlay_template_id.id,
                'overlayTemplateName': rec.overlay_template_id.name,
                'productName': rec.product_tmpl_id.name,
                'imageUrl': rec._preview_image_url(),
                'url': f'/shop/{slug(rec.overlay_template_id)}?{OVERLAY_PRODUCT_ID_URL_PARAMETER}={rec.id}',
                'updatedByName': rec.updated_by_id.partner_id.name or '',
                'lastUpdatedDate': Datetime.to_string(rec.last_updated_date),
            })
        return res

    @classmethod
    def _get_shop_catalog_data(cls, catalog_tab, page=1, limit=SHOP_CATALOG_ITEM_LIMIT):
        catalog_item_list = []
        catalog_items_total = 0
        catalog_model = 'overlay.template'
        if catalog_tab in [OVERLAY_TEMPLATE_CATALOG_TAB_KEY, OVERLAY_PRODUCT_CATALOG_TAB_KEY]:
            catalog_model = SHOP_CATALOG_TAB_MODELS[catalog_tab]

        active_hotel_id = request.env.user._active_hotel_id()
        if active_hotel_id:
            domain = [('hotel_ids', 'in', active_hotel_id.id), ('website_published', '=', True)]
            catalog_items_total = request.env[catalog_model].sudo().search_count(domain)
            order = DEFAULT_SHOP_CATALOG_TAB_SORT[catalog_tab]
            offset = (page - 1) * limit
            if offset >= catalog_items_total:
                page = 1
                offset = 0
            catalog_item_ids = request.env[catalog_model].sudo().search(domain, offset=offset, limit=limit, order=order)
            if catalog_tab == OVERLAY_PRODUCT_CATALOG_TAB_KEY:
                catalog_item_list = cls._prepare_overlay_product_data(catalog_item_ids)
            else:
                catalog_item_list = cls._prepare_overlay_template_data(catalog_item_ids)
            
        return {
            'itemList': catalog_item_list,
            'totalItemsNumber': catalog_items_total,
            'itemsLimit': SHOP_CATALOG_ITEM_LIMIT,
            'currentPage': page,
            'currentTab': catalog_tab,
        }
        
    @http.route(['/shop'], type='http', auth='user', website=True)
    def shop_catalog_page(self, **kwargs):
        page = 1
        url_page = kwargs.get(PAGE_URL_PARAMETER, False)
        if url_page:
            try:
                url_page = int(url_page)
                page = url_page
            except (ValueError, TypeError):
                pass

        catalog_tab = OVERLAY_TEMPLATE_CATALOG_TAB_KEY
        url_catalog_tab = kwargs.get(SHOP_CATALOG_TAB_URL_PARAMETER, False)
        if url_catalog_tab:
            catalog_tab = url_catalog_tab

        catalog_list_data = self._get_shop_catalog_data(catalog_tab, page=page)
        catalog_list_data.update({
            'options': {
                'overlayTemplateTabKey': OVERLAY_TEMPLATE_CATALOG_TAB_KEY,
                'overlayProductTabKey': OVERLAY_PRODUCT_CATALOG_TAB_KEY,
            },
            'urlParameterList': {
                'currentPage': PAGE_URL_PARAMETER,
                'currentTab': SHOP_CATALOG_TAB_URL_PARAMETER,
            },
        })
        
        return request.render('regency_shopsite.shop_catalog_page', {
            'shop_catalog_data': Markup(json.dumps(catalog_list_data)),
        })

    @http.route(['/shop/data'], type='json', methods=['POST'], auth='user', website=True)
    def shop_catalog_data(self, page, limit, catalog_tab):
        return self._get_shop_catalog_data(catalog_tab, page=page, limit=limit)
