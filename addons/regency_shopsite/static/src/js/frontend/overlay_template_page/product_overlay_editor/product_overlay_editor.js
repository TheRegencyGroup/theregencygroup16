/** @odoo-module **/

import { useStore } from '@fe_owl_base/js/main';
import { ProductOverlayPositionComponent } from './product_overlay_position';
import Dialog from 'web.Dialog';
import env from 'web.public_env';
import {
    PRODUCT_IMAGE_MODEL,
    computeImageSrc
} from "../../../main";

const { Component, useRef, useState, onMounted } = owl;

export class ProductOverlayEditorComponent extends Component {
    setup() {
        onMounted(this.onMounted.bind(this));

        this.store = useStore();
        this.state = useState({
            selectedOverlayPositionId: Object.values(this.store.otPage.overlayPositions)[0].id,
        });

        this.imageUploadRef = useRef('image_upload_ref');

        this.imageTimestamp = new Date().valueOf();
    }

    async onMounted() {

    }

    get overlayPositionComponents() {
        return Object.values(this.__owl__.children)
            .filter(e => e.component.constructor.name === 'ProductOverlayPositionComponent')
            .map(e => e.component);
    }

    get overlayPositionSwitcherList() {
        return Object.values(this.store.otPage.overlayPositions).map(e => {
            const valueId = this.store.otPage.selectedAreasImageAttributeValueId;
            let imageId = e.selectedImages[valueId]?.imageId;
            if (!imageId) {
                imageId = Object.values(e.selectedImages)[0].imageId;
            }
            return {
                id: e.id,
                name: e.name,
                previewImageSrc: computeImageSrc({
                    id: imageId,
                    model: PRODUCT_IMAGE_MODEL,
                    field: 'image_128',
                    timestamp: this.imageTimestamp,
                }),
            }
        });
    }

    checkAreasWasChanged() {
       for (let component of this.overlayPositionComponents) {
           for (let area of Object.values(component.areas)) {
                if (area.wasChanged) {
                    return true;
                }
           }
       }
       return false;
    }

    getOverlayAreaList() {
        let data = {};
        for (let component of this.overlayPositionComponents) {
            const overlayPosition = component.props.overlayPosition;
            const areaList = {};
            for (let area of Object.values(component.areas)) {
                let areaData = area.getOverlayImagesData();
                if (!areaData.length) {
                    alert('All area must be filled!');
                    return false;
                }
                areaList[area.areaIndex] = {
                    'index': area.areaIndex,
                    'type': area.areaType,
                    'data': areaData,
                };
            }
            data[overlayPosition.id] = {
                overlayPositionId: overlayPosition.id,
                areaList,
            };
        }
        return data;
    }

    async getPreviewImagesData() {
        let data = [];
        for (let component of this.overlayPositionComponents) {
            let overlayPosition = component.props.overlayPosition;
            let backgroundImageId = component.state.backgroundImage.id;
            let imageData = {
                overlayPositionId: overlayPosition.id,
                backgroundImageSize: {
                    width: overlayPosition.canvasSize.width,
                    height: overlayPosition.canvasSize.height,
                },
                backgroundImageId,
            }
            const areaList = [];
            for (let area of Object.values(component.areas)) {
                areaList.push(await area.getPreviewImageData());
            }
            if (areaList.length) {
                imageData.images = areaList;
            }
            data.push(imageData);
        }
        return data;
    }

    onClickSelectOverlayPosition(id, event) {
        this.state.selectedOverlayPositionId = id;
    }
}

ProductOverlayEditorComponent.components = {
    ProductOverlayPositionComponent,
};

ProductOverlayEditorComponent.template = 'product_overlay_editor';
