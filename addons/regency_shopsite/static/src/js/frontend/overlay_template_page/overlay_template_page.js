/** @odoo-module **/

import './store';
import { mountComponentAsWidget, useStore } from '@fe_owl_base/js/main';
import { ProductOverlayEditorComponent } from './product_overlay_editor/product_overlay_editor';
import { AttributeSelector, ColorAttributeSelector } from './attribute_selector';
import { PriceSelector } from './price_selector';
import env from 'web.public_env';

const { Component, useState, useRef } = owl;

export class OverlayTemplatePageComponent extends Component {
    setup() {
        this.store = useStore();
        this.state = useState({
            nameInputIsFilled: !!this.store.otPage.overlayProductName,
        });

        this.inputNameRef = useRef('name_input');

        env.bus.on('active-hotel-changed', null, this.onChangedActiveHotel.bind(this));
    }

    get sortedAttributeList() {
        let initAttributeList = Object.values(this.store.otPage.attributeList);
        let sizeAttributeId = this.store.otPage.sizeAttributeId;
        let attributeList = initAttributeList.filter(e => this.store.otPage.colorAttributeId !== e.id);
        if (this.store.otPage.attributeList[sizeAttributeId]) {
            attributeList = attributeList.filter(e => this.store.otPage.sizeAttributeId !== e.id);
            attributeList = [
                this.store.otPage.attributeList[sizeAttributeId],
                ...attributeList,
            ];
        }
        return attributeList;
    }

    get OverlayEditor() {
        return Object.values(this.__owl__.children)
            .find(e => e.component.constructor.name === 'ProductOverlayEditorComponent')
            .component;
    }

    onInputNameFocusin() {
        this.state.nameInputIsFilled = true;
    }

    onInputNameFocusout() {
        this.state.nameInputIsFilled = !!this.inputNameRef.el.value;
    }

    async getDataForSaveCustomization() {
        let name = this.inputNameRef.el.value.trim();
        if (!name) {
            alert('Listing name is empty!')
            return false;
        }
        let overlayAreaList = this.OverlayEditor.getOverlayAreaList();
        if (!overlayAreaList) {
            return false;
        }
        let previewImagesData = await this.OverlayEditor.getPreviewImagesData();
        return { name, overlayAreaList, previewImagesData }
    }

    async onClickSaveCustomization() {
        const customData = await this.getDataForSaveCustomization();
        if (!customData) {
            return false;
        }
        this.store.otPage.saveOverlayProduct({
            overlayProductName: customData.name,
            overlayAreaList: customData.overlayAreaList,
            previewImagesData: customData.previewImagesData,
        }).catch();
    }

    async onClickAddToCart() {
        if (!this.store.otPage.overlayTemplateIsAvailableForActiveHotel || !this.store.otPage.hasPriceList) {
            return;
        }
        let data = this.store.otPage.getCustomizedData();
        let overlayProductId = this.store.otPage.overlayProductId;
        if (!!overlayProductId) {
            data = {
                quantity: data.quantity,
                overlayProductId,
            };
        } else {
            const customData = await this.getDataForSaveCustomization();
            if (!customData) {
                return false;
            }
            data = {
                ...data,
                overlayProductName: customData.name,
                overlayAreaList: customData.overlayAreaList,
                previewImagesData: customData.previewImagesData,
            }
        }
        let res = await this.store.cart.addOverlayToCart(data);
        if (res) {
            this.store.otPage.updateOverlayProductData(res);
        }
    }

    onChangedActiveHotel() {
        let activeHotelId = this.store.hotelSelector?.activeHotel;
        this.store.otPage.updatePriceList(activeHotelId).catch();
    }
}

OverlayTemplatePageComponent.components = {
    ProductOverlayEditorComponent,
    AttributeSelector,
    ColorAttributeSelector,
    PriceSelector,
};

OverlayTemplatePageComponent.template = 'overlay_template_page';

mountComponentAsWidget('OverlayTemplatePageComponent', OverlayTemplatePageComponent).catch();
