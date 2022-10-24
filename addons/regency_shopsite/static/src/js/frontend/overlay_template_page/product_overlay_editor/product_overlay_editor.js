/** @odoo-module **/

import { useStore } from '@fe_owl_base/js/main';
import { ProductOverlayPositionComponent } from './product_overlay_position';
import Dialog from 'web.Dialog';
import env from 'web.public_env';

const { Component, useRef, useState, onMounted } = owl;

export class ProductOverlayEditorComponent extends Component {
    setup() {
        onMounted(this.onMounted.bind(this));

        this.store = useStore();
        this.state = useState({
            selectedOverlayPositionId: Object.values(this.store.otPage.overlayPositions)[0].id,
        });

        this.imageUploadRef = useRef('image_upload_ref');

        env.bus.on('get-overlay-editor-data', null, this.getOverlayAreaList.bind(this));
    }

    async onMounted() {

    }

    getOverlayAreaList() {
        let overlayPositionComponents = Object.values(this.__owl__.children)
            .filter(e => e.component.constructor.name === 'ProductOverlayPositionComponent')
            .map(e => e.component);
        let data = {};
        for (let component of overlayPositionComponents) {
            let overlayPosition = component.props.overlayPosition;
            let image = component.getColorImage();
            let imageData = {
                position_name: overlayPosition.name,
                background_image_size: {
                    width: overlayPosition.canvasSize.width,
                    height: overlayPosition.canvasSize.height,
                },
                background_image_id: image.imageId,
                background_image_model: image.imageModel,
            }
            let areaList = {};
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
            // if (areaList.length) {
            //     imageData.images = areaList;
            // }
            data[overlayPosition.id] = {
                overlayPositionId: overlayPosition.id,
                areaList,
            };
        }
        return data;
    }

    getImageSrc(colorImages) {
        let baseUrl = window.location.origin;
        let timestamp = new Date().valueOf();
        if (!colorImages) {
            return false;
        }
        let image = colorImages[this.store.otPage.selectedColorValueId];
        if (!image) {
            image = Object.values(colorImages).find(e => !!e.imageId && !!e.imageModel);
        }
        let id;
        let model;
        if (image) {
            id = image.imageId;
            model = image.imageModel;
        }
        return (id && model)
            ? `${baseUrl}/web/image?model=${model}&id=${id}&field=image_128&unique=${timestamp}`
            : false;
    }

    onClickSelectOverlayPosition(id, event) {
        this.state.selectedOverlayPositionId = id;
    }
}

ProductOverlayEditorComponent.components = {
    ProductOverlayPositionComponent,
};

ProductOverlayEditorComponent.template = 'product_overlay_editor';
