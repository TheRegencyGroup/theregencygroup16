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

    get overlayEditor() {
        return Object.values(this.__owl__.children)
            .find(e => e.component.constructor.name === 'ProductOverlayEditorComponent')
            .component;
    }

    get disabledEditName() {
        return this.store.otPage.hasOverlayProductId && !this.store.otPage.editMode;
    }

    get showEditBtn() {
        return this.store.otPage.overlayProductActive &&
            this.store.otPage.hasOverlayProductId &&
            !this.store.otPage.editMode;
    }

    get showDeleteBtn() {
        return this.store.otPage.overlayProductActive && !this.store.otPage.editMode;
    }

    get showCancelBtn() {
        return this.store.otPage.hasOverlayProductId && this.store.otPage.editMode;
    }

    get showSaveBtn() {
        return (this.store.otPage.overlayProductActive &&
                this.store.otPage.hasOverlayProductId &&
                this.store.otPage.editMode) ||
            !this.store.otPage.hasOverlayProductId;
    }

    get showDuplicateBtn() {
        return this.store.otPage.overlayProductActive &&
            this.store.otPage.hasOverlayProductId &&
            !this.store.otPage.editMode;
    }

    get showPriceSelector() {
        return this.store.otPage.hasPriceList && this.showAddToCartBtn;
    }

    get showAddToCartBtn() {
        return !this.store.otPage.hasOverlayProductId ||
            (this.store.otPage.hasOverlayProductId && this.store.otPage.overlayProductActive);
    }

    onInputNameFocusin() {
        this.state.nameInputIsFilled = true;
    }

    onInputNameFocusout() {
        this.state.nameInputIsFilled = !!this.inputNameRef.el.value;
    }

    async getDataForSaveCustomization() {
        let overlayProductName = this.inputNameRef.el.value.trim();
        if (!overlayProductName) {
            alert('Listing name is empty!')
            return false;
        }
        let overlayAreaList;
        let previewImagesData;
        let overlayProductWasChanged;
        if (this.store.otPage.editMode) {
            overlayProductWasChanged = this.overlayEditor.checkAreasWasChanged() ||
                this.store.otPage.attrributesWasChanged;
        }
        if (!this.store.otPage.hasOverlayProductId ||
            (this.store.otPage.editMode && (overlayProductWasChanged))) {
            overlayAreaList = this.overlayEditor.getOverlayAreaList();
            if (!overlayAreaList) {
                return false;
            }
            previewImagesData = await this.overlayEditor.getPreviewImagesData();
        }
        return { overlayProductName, overlayAreaList, previewImagesData, overlayProductWasChanged }
    }

    async onClickEditCustomization() {
        if (this.store.otPage.overlayProductIsArchived || this.store.otPage.editMode) {
            return;
        }
        this.store.otPage.enableEditMode();
    }

    async onClickDeleteCustomization() {
        if (this.store.otPage.overlayProductIsArchived) {
            return;
        }
        await this.store.otPage.deleteOverlayProduct();
    }

    async onClickSaveCustomization() {
        if (this.store.otPage.overlayProductIsArchived) {
            return;
        }
        const customData = await this.getDataForSaveCustomization();
        if (!customData) {
            return false;
        }
        await this.store.otPage.saveOverlayProduct(customData);
        if (this.store.otPage.editMode) {
            this.store.otPage.disableEditMode();
        }
    }

    async onClickDuplicateCustomization() {
        if (this.store.otPage.overlayProductIsArchived) {
            return;
        }
    }

    onClickCancelCustomization() {
        window.location.reload();
    }

    async onClickAddToCart() {
        if (!this.store.otPage.canAddedToCart) {
            return;
        }
        let data = this.store.otPage.getCustomizedData();
        let overlayProductId = this.store.otPage.overlayProductId;
        if (!!overlayProductId) {
            data = {
                ...data,
                overlayProductId,
            };
        }
        if (!this.store.otPage.hasOverlayProductId ||
            (!!this.store.otPage.hasOverlayProductId && this.store.otPage.editMode)) {
            const customData = await this.getDataForSaveCustomization();
            if (!customData) {
                return false;
            }
            data = {
                ...data,
                ...customData,
            }
        }
        let res = await this.store.cart.addOverlayToCart(data);
        if (res) {
            this.store.otPage.updateOverlayProductData(res);
        }
        if (this.store.otPage.editMode) {
            this.store.otPage.disableEditMode();
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
