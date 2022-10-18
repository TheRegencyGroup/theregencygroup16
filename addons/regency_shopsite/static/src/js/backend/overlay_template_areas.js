/** @odoo-module **/

import AbstractField from 'web.AbstractFieldOwl';
import fieldRegistry from 'web.field_registry_owl';
import { OverlayAreasPositionComponent } from './overlay_template_areas_position';

const { onMounted, onPatched, useState, useRef } = owl.hooks;

const OVERLAY_AREAS_WIDGET_NAME = 'overlay_areas';

class OverlayAreasWidget extends AbstractField {
    static supportedFieldTypes = ['char'];
    static template = 'overlay_areas';
    static components = { OverlayAreasPositionComponent };

    constructor(...args) {
        super(...args);

        onPatched(this.onPatched.bind(this));
        onMounted(this.onMounted.bind(this));

        this.valueObj = JSON.parse(this.value);

        this.state = useState({
            productTemplateId: this.valueObj.productTemplateId,
            productImageList: this.valueObj.productImageList || [],
            overlayPositions: this.valueObj.overlayPositions || {},
            showImageListForOverlayPosId: false,
        });

        this.imageListPopupRef = useRef('image_list_popup');

        this.productImageUnique = new Date().valueOf();
    }

    onMounted() {
        let popup = this.imageListPopupRef.el;
        this.imageListPopupRef.el.remove();
        document.body.appendChild(popup);

        window.onbeforeunload = () => {
            this.reloadPage = true;
        };
    }

    onPatched() {
        let update = false;
        this.valueObj = JSON.parse(this.value);
        if (this.props.event) {
            if (this.props.event.data.changes?.product_template_id !== undefined) {
                this.state.productTemplateId = this.valueObj.productTemplateId;
                this.state.productImageList = this.valueObj.productImageList;
                this.productImageUnique = new Date().valueOf();
                for (let overlayPosition of Object.values(this.state.overlayPositions)) {
                    overlayPosition.areaList = {};
                    for (let colorImage of Object.values(overlayPosition.colorImages)) {
                        colorImage.imageId = false;
                        colorImage.imageModel = false;
                    }
                }
            } else if (this.props.event.data.changes?.overlay_position_ids !== undefined) {
                for (let overlayPosition of Object.values(this.valueObj.overlayPositions)) {
                    if (!this.state.overlayPositions[overlayPosition.id]) {
                        this.state.overlayPositions[overlayPosition.id] = overlayPosition;
                    }
                }
                let removedOverlayPositionIds = Object.keys(this.state.overlayPositions)
                    .filter(e => !Object.keys(this.valueObj.overlayPositions).includes(e));
                for (let overlayPositionId of removedOverlayPositionIds) {
                    delete this.state.overlayPositions[overlayPositionId];
                }
            } else if (this.props.event.data.changes?.overlay_attribute_line_ids !== undefined) {
                for (let overlayPosition of Object.values(this.valueObj.overlayPositions)) {
                    for (let colorImage of Object.values(overlayPosition.colorImages)) {
                        if (!this.state.overlayPositions[overlayPosition.id].colorImages[colorImage.id]) {
                            this.state.overlayPositions[overlayPosition.id].colorImages[colorImage.id] = colorImage;
                        }
                    }
                    let removedColorIds = Object.keys(this.state.overlayPositions[overlayPosition.id].colorImages)
                        .filter(e => !Object.keys(overlayPosition.colorImages).includes(e));
                    for (let colorId of removedColorIds) {
                        delete this.state.overlayPositions[overlayPosition.id].colorImages[colorId];
                    }
                }
            }
            this.props.event.data.changes = null;
        }
    }

    get editMode() {
        return this.mode === 'edit';
    }

    get filteredProductImageList() {
        let selectedImages = Object.values(this.state.overlayPositions)
            .map(e => Object.values(e.colorImages))
            .flat()
            .filter(e => !!e.imageId && !!e.imageModel);
        if (!selectedImages) {
            return this.state.productImageList;
        }
        return this.state.productImageList.filter(e => {
            for (let image of selectedImages) {
                if (e.id === image.imageId && e.model === image.imageModel) {
                    return false;
                }
            }
            return true;
        })
    }

    getProductImageSrc(id, model) {
        let baseUrl = window.location.origin;
        return `${baseUrl}/web/image?model=${model}&id=${id}&field=image_512&unique=${this.productImageUnique}`;
    }

    changeOverlayAreasImage(event) {
        this.state.showImageListForOverlayPosId = {
            id: event.detail.id,
            colorId: event.detail.colorId,
        };
    }

    commitChanges() {
        if (!this.editMode) {
            return;
        }
        let val = {
            productTemplateId: this.state.productTemplateId || false,
            productImageList: this.state.productImageList,
            overlayPositions: {},
        }
        let OverlayAreasPositionComponents = Object.values(this.__owl__.children)
            .filter(e => e.constructor.name === 'OverlayAreasPositionComponent');
        for (let component of OverlayAreasPositionComponents) {
            let overlayPositionId = component.props.overlayPositionId;
            // if (!component.state.imageLoad) {
            //     val.overlayPositions[overlayPositionId] = this.valueObj.overlayPositions[overlayPositionId];
            //     continue;
            // }
            let areaList = {};
            if (component.overlay) {
                for (let area of Object.values(component.overlay.areaList)) {
                    let objectBoundingRect = area.object.getBoundingRect();
                    areaList[area.index] = {
                        index: area.index,
                        data: {
                            ...area.data,
                            boundRect: {
                                width: Math.ceil(objectBoundingRect.width),
                                height: Math.ceil(objectBoundingRect.height),
                                x: Math.ceil(objectBoundingRect.left),
                                y: Math.ceil(objectBoundingRect.top),
                            },
                        },
                        areaType: area.areaType,
                    }
                }
            }
            let name = component.props.overlayPositionName;
            let imageId = component.props.imageId;
            let imageModel = component.props.imageModel;
            let canvasSize = false;
            // if (component.overlay?.canvas) {
            //     canvasSize = {
            //         width: component.overlay.canvas.width,
            //         height: component.overlay.canvas.height,
            //     };
            // }
            canvasSize = {
                width: 500,
                height: 500,
            };
            let colorImages = component.props.colorImages;
            val.overlayPositions[overlayPositionId] = {
                id: overlayPositionId,
                name,
                imageId,
                imageModel,
                areaList,
                canvasSize,
                colorImages,
            };
        }
        this._setValue(JSON.stringify(val));
    }

    closeImageListPopup() {
        this.state.showImageListForOverlayPosId = false;
    }

    onClickImage(id, model, event) {
        let overlayPositionId = this.state.showImageListForOverlayPosId.id;
        let colorId = this.state.showImageListForOverlayPosId.colorId;
        this.state.overlayPositions[overlayPositionId].colorImages[colorId].imageId = id;
        this.state.overlayPositions[overlayPositionId].colorImages[colorId].imageModel = model;
        this.state.overlayPositions[overlayPositionId].areaList = {};
        this.closeImageListPopup();
    }

    onClickCloseImageListPopup(event) {
        this.closeImageListPopup();
    }
}

fieldRegistry.add(OVERLAY_AREAS_WIDGET_NAME, OverlayAreasWidget);

export {
    OverlayAreasWidget,
    OVERLAY_AREAS_WIDGET_NAME,
}
