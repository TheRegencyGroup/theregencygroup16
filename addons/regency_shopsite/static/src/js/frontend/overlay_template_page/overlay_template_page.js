/** @odoo-module **/

import './store';
import { mountComponentAsWidget, useStore } from '@fe_owl_base/js/main';
import { ProductOverlayEditorComponent } from './product_overlay_editor/product_overlay_editor';
import { AttributeSelector, ColorAttributeSelector } from './attribute_selector';
import { QuantitySelector } from './quantity_selector';
import env from 'web.public_env';

const { Component, useState, useRef, onMounted } = owl;

export class OverlayTemplatePageComponent extends Component {
    setup() {
        onMounted(this.onMounted.bind(this));

        this.store = useStore();
        this.state = useState({
            nameInputIsFilled: !!this.store.otPage.overlayProduct?.name,
        });

        this.inputNameRef = useRef('name_input');
        this.listingNameInfoRef = useRef('listing_name_info')

        env.bus.on('active-hotel-changed', null, this.onChangedActiveHotel.bind(this));
    }

    onMounted() {
        this.listingNameInfoPopover = tippy(this.listingNameInfoRef.el, {
            sticky: true,
            zIndex: 999,
            maxWidth: 215,
            placement: 'top-start',
            theme: 'listing-name-info',
            appendTo: () => document.getElementById('wrap'),
            content: 'This is where you supply the name of your customized item',
            trigger: 'mouseenter focus',
            offset: [-10, 10],
        });
    }

    get sortedAttributeList() {
        let initAttributeList = Object.values(this.store.otPage.attributeList);;
        return initAttributeList.filter(e => this.store.otPage.colorAttributeId !== e.id);
    }

    get showColorAttributeSelector() {
        return Object.values(this.store.otPage.attributeList).find(e => this.store.otPage.colorAttributeId === e.id);
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
        return this.store.otPage.hasOverlayProductId &&
            !this.store.otPage.overlayProductIsArchived &&
            !this.store.otPage.editMode;
    }

    get showDeleteBtn() {
        return this.store.otPage.hasOverlayProductId &&
            !this.store.otPage.overlayProductIsArchived &&
            !this.store.otPage.editMode;
    }

    get showCancelBtn() {
        return this.store.otPage.hasOverlayProductId &&
            !this.store.otPage.overlayProductIsArchived &&
            this.store.otPage.editMode;
    }

    get showSaveBtn() {
        return (this.store.otPage.hasOverlayProductId &&
            !this.store.otPage.overlayProductIsArchived &&
            this.store.otPage.editMode) || !this.store.otPage.hasOverlayProductId;
    }

    get showDuplicateBtn() {
        return this.store.otPage.hasOverlayProductId &&
            !this.store.otPage.overlayProductIsArchived &&
            !this.store.otPage.editMode;
    }

    get showQuantitySelector() {
        return !this.store.otPage.overlayProductIsArchived && this.store.otPage.hasPriceList;
    }

    get showAddToCartBtn() {
        return !this.store.otPage.overlayProductIsArchived &&
            ((this.store.otPage.hasPriceList &&
                    this.store.otPage.overlayTemplate?.isAvailableForActiveHotel) ||
                (!this.store.otPage.hasPriceList &&
                    !this.store.otPage.overlayTemplate?.isAvailableForActiveHotel));
    }

    get showListingNameInfoPopover() {
        return !this.store.otPage.hasOverlayProductId || this.store.otPage.editMode;
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
        if (!window.confirm('Do you really want to delete this customization?')) {
            return;
        }
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
        this.store.otPage.duplicateOverlayProduct();
    }

    onClickCancelCustomization() {
        window.location.reload();
    }

    async onClickAddToCart() {
        if (this.store.cart.addingToCart) {
            return;
        }
        if (!this.store.otPage.canAddedToCart) {
            return;
        }
        if (this.store.otPage.quantity < this.store.otPage.minimumOrderQuantity) {
            return;
        }
        let data = this.store.otPage.getCustomizedData();
        let overlayProductId = this.store.otPage.overlayProduct?.id;
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
            };
        }
        if (this.store.otPage.duplicateOverlayProductId) {
            data.duplicateOverlayProductId = this.store.otPage.duplicateOverlayProductId;
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
    QuantitySelector,
};

OverlayTemplatePageComponent.template = 'overlay_template_page';

mountComponentAsWidget('OverlayTemplatePageComponent', OverlayTemplatePageComponent).catch();
