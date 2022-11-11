/** @odoo-module **/

import { useStore } from "@fe_owl_base/js/main";
import {
    ELLIPSE_AREA_TYPE,
    RECTANGLE_AREA_TYPE,
    TEXT_AREA_TYPE,
    PRODUCT_IMAGE_MODEL,
    OVERLAY_PRODUCT_AREA_IMAGE,
    computeImageSrc,
} from '../../../main';
import { RectangleArea } from './rectangle_area';
import { EllipseArea } from './ellipse_area';
import { TextArea } from './text_area';

const { Component, onMounted, onPatched, useState, useRef } = owl;

const ACCEPT_FILE_EXTENSIONS_FOR_AREAS = ['png', 'jpg', 'jpeg', 'svg'];

export class ProductOverlayPositionComponent extends Component {
    setup() {
        this.acceptFileExtensionsForAreas = ACCEPT_FILE_EXTENSIONS_FOR_AREAS
            .map(e => `.${e}`).join(', ');

        onPatched(this.onPatched.bind(this));
        onMounted(this.onMounted.bind(this));

        this.store = useStore();

        this.state = useState({
            backgroundImage: {},
            selectedAreaIndex: null,
        });

        this.areas = {};

        this.imageRef = useRef('image_ref');
        this.canvasContainerRef = useRef('canvas_container_ref');

        this.loadImage = false;
        this.lastSelectedAreasImageAttributeValueId = this.store.otPage.selectedAreasImageAttributeValueId;
        this.lastOverlayProductId = this.store.otPage.overlayProductId;
        this.lastEditModeState = this.store.otPage.editMode;
        
        this.imageTimestamp = new Date().valueOf();
    }

    onMounted() {
        this.setImageOnloadCallback();
        this.updateImageSrc();
    }

    onPatched() {
        if (this.lastSelectedAreasImageAttributeValueId !== this.store.otPage.selectedAreasImageAttributeValueId) {
            this.lastSelectedAreasImageAttributeValueId = this.store.otPage.selectedAreasImageAttributeValueId;
            this.updateImageSrc();
        }
        let editModeWasChange = false;
        if (this.lastEditModeState !== this.store.otPage.editMode) {
            this.lastEditModeState = this.store.otPage.editMode;
            editModeWasChange = true;
        }
        if (this.lastOverlayProductId !== this.store.otPage.overlayProductId || editModeWasChange) {
            this.lastOverlayProductId = this.store.otPage.overlayProductId;
            for (let area of Object.values(this.areas)) {
                area.showMaskBorders(!this.store.otPage.hasOverlayProductId || this.store.otPage.editMode);
                area.enablePointerEvents(!this.store.otPage.hasOverlayProductId || this.store.otPage.editMode);
                area.wasChanged = false;
            }
        }
    }

    get overlayPositionId() {
        return this.props.overlayPosition.id;
    }

    updateImageSrc() {
        const position = this.props.overlayPosition;
        const valueId = this.store.otPage.selectedAreasImageAttributeValueId;
        let imageId = position.selectedImages[valueId]?.imageId;
        if (!imageId) {
            imageId = Object.values(position.selectedImages)[0].imageId;
        }
        this.state.backgroundImage = {
            id: imageId,
            src: computeImageSrc({
                id: imageId,
                model: PRODUCT_IMAGE_MODEL,
                field: 'image_512',
                timestamp: this.imageTimestamp,
            }),
        };
    }

    setImageOnloadCallback() {
        if (!this.imageRef.el) {
            return;
        }
        this.imageRef.el.onload = () => {
            if (!this.loadImage) {
                this.loadImage = true;
                this.updateAreas();
            }
        };
    }

    updateAreas() {
        if (this.canvasContainerRef.el) {
            let areaObjectData;
            if (this.store.otPage.overlayProductAreaList) {
                areaObjectData = this.store.otPage.overlayProductAreaList[this.overlayPositionId];
            }
            for (let areaData of Object.values(this.props.overlayPosition.areaList)) {
                let area;
                let areaObjList = [];
                if (areaObjectData) {
                    areaObjList = areaObjectData.areaList[areaData.index].data;
                    for (let obj of areaObjList) {
                        let imageId = this.store.otPage.overlayProductAreaImageList[this.overlayPositionId][areaData.index][obj.index];
                        obj.imageUrl = computeImageSrc({
                            id: imageId,
                            model: OVERLAY_PRODUCT_AREA_IMAGE,
                            field: 'image',
                        });
                    }
                }
                if (areaData.areaType === RECTANGLE_AREA_TYPE) {
                    area = new RectangleArea(areaData.data, this.canvasContainerRef.el, areaData.index, areaObjList);
                } else if (areaData.areaType === ELLIPSE_AREA_TYPE) {
                    area = new EllipseArea(areaData.data, this.canvasContainerRef.el, areaData.index, areaObjList);
                } else if (areaData.areaType === TEXT_AREA_TYPE) {
                    area = new TextArea(areaData.data, this.canvasContainerRef.el, areaData.index, areaObjList);
                }
                if (area) {
                    area.onSelectedArea(this.onSelectedArea.bind(this));
                    area.enablePointerEvents(!this.store.otPage.hasOverlayProductId);
                    area.showMaskBorders(!this.store.otPage.hasOverlayProductId || this.store.otPage.editMode);
                    this.areas[areaData.index] = area;
                }
            }
        }
    }

    onSelectedArea(areaIndex) {
        this.state.selectedAreaIndex = areaIndex;
        for (let area of Object.values(this.areas)) {
            if (area.areaIndex === areaIndex) {
                continue;
            }
            area.unselectedArea();
        }
    }

    onChangeUploadImage(event) {
        if (!this.state.selectedAreaIndex) {
            return;
        }
        const reader = new FileReader();
        reader.onloadend = () => {
            const image = new Image();
            image.src = reader.result;
            image.onload = () => {
                this.areas[this.state.selectedAreaIndex].addImageObject({
                    image,
                    uploadedByUser: true,
                });
                event.target.value = '';
            };
        };
        if (event.target.files.length) {
            reader.readAsDataURL(event.target.files[0]);
        }
    }

    onClickRemoveAllObjects(event) {
        if (!this.state.selectedAreaIndex) {
            return;
        }
        this.areas[this.state.selectedAreaIndex].removeAllObjects();
    }

    onClickRemoveActiveObject(event) {
        if (!this.state.selectedAreaIndex) {
            return;
        }
        this.areas[this.state.selectedAreaIndex].removeActiveObject();
    }
}

ProductOverlayPositionComponent.props = {
    overlayPosition: Object,
}

ProductOverlayPositionComponent.template = 'product_overlay_position'
