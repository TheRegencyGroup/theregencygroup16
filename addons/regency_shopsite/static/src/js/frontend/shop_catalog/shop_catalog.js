/** @odoo-module **/

import './store';
import { mountComponentAsWidget, useStore } from '@fe_owl_base/js/main';
import { ShopCatalogOverlayTemplateItem } from './shop_catalog_overlay_template_item';
import { ShopCatalogOverlayProductItem } from './shop_catalog_overlay_product_item';
import { ListPagination } from '../list_pagination/list_pagination';
import env from 'web.public_env';

const { Component } = owl;

export class ShopCatalog extends Component {
    setup() {
        this.store = useStore();

        env.bus.on('active-hotel-changed', null, this.onChangedActiveHotel.bind(this));
    }

    get isOverlayTemplateTab() {
        return this.store.shopCatalog.currentTab === this.store.shopCatalog.options.overlayTemplateTabKey;
    }

    get isOverlayProductTab() {
        return this.store.shopCatalog.currentTab === this.store.shopCatalog.options.overlayProductTabKey;
    }

    onClicKOverlayTemplateTab() {
        if (this.isOverlayProductTab) {
            this.store.shopCatalog.updateList({
                page: 1,
                tab: this.store.shopCatalog.options.overlayTemplateTabKey,
            }).catch();
        }
    }

    onClickOverlayProductTab() {
        if (this.isOverlayTemplateTab) {
            this.store.shopCatalog.updateList({
                page: 1,
                tab: this.store.shopCatalog.options.overlayProductTabKey,
            }).catch();
        }
    }

    onChangeListPaginationPage(page) {
        this.store.shopCatalog.updateList({ page }).catch();
    }

    onChangedActiveHotel() {
        let activeHotelId = this.store.hotelSelector?.activeHotel;
        this.store.shopCatalog.updateList({ page: 1 }).catch();
    }
}

ShopCatalog.components = {
    ShopCatalogOverlayTemplateItem,
    ShopCatalogOverlayProductItem,
    ListPagination,
}

ShopCatalog.template = 'shop_catalog';

mountComponentAsWidget('ShopCatalog', ShopCatalog).catch();
