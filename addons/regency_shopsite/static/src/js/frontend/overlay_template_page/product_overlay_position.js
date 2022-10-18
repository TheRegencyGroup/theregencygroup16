/** @odoo-module **/

import {
    ELLIPSE_AREA_TYPE,
    RECTANGLE_AREA_TYPE,
    TEXT_AREA_TYPE,
} from '../../main';
import { RectangleArea } from './rectangle_area';
import { EllipseArea } from './ellipse_area';
import { TextArea } from './text_area';
import {OVERLAY_TEMPLATE_PAGE_KEY} from "./store";
import {env} from "../base/main";

const { Component } = owl;
const { onMounted, onPatched, useState, useStore, useRef } = owl.hooks;

export class ProductOverlayPositionComponent extends Component {
    constructor(...args) {
        super(...args);

        onPatched(this.onPatched.bind(this));
        onMounted(this.onMounted.bind(this));

        this.store = useStore(state => {
            const selectedAttributeValues = state[OVERLAY_TEMPLATE_PAGE_KEY].selectedAttributeValues;
            const colorAttributeId = state[OVERLAY_TEMPLATE_PAGE_KEY].data.colorAttributeId;
            return {
                colorValueId: selectedAttributeValues[colorAttributeId].valueId,
            }
        }, {
            store: env.store,
        });

        this.state = useState({
            imageSrc: null,
            selectedAreaIndex: null,
        });

        this.areas = {};

        this.imageRef = useRef('image_ref');
        this.canvasContainerRef = useRef('canvas_container_ref');

        this.loadImage = false;
        this.currentColorValueId = this.store.colorValueId;
    }

    onMounted() {
        this.setImageOnloadCallback();
        this.state.imageSrc = this.getImageSrc();
    }

    onPatched() {
        if (this.currentColorValueId !== this.store.colorValueId) {
            this.currentColorValueId = this.store.colorValueId;
            this.state.imageSrc = this.getImageSrc();
        }
    }

    getColorImage() {
        let image = this.props.overlayPosition.colorImages[this.store.colorValueId];
        if (!image) {
            image = Object.values(this.props.overlayPosition.colorImages).find(e => !!e.imageId && !!e.imageModel)
        }
        return image;
    }

    getImageSrc() {
        let baseUrl = window.location.origin;
        let timestamp = new Date().valueOf();
        if (!this.props.overlayPosition.colorImages) {
            return false;
        }
        let image = this.getColorImage();
        let id;
        let model;
        if (image) {
            id = image.imageId;
            model = image.imageModel;
        }
        return (id && model)
            ? `${baseUrl}/web/image?model=${model}&id=${id}&field=image_512&unique=${timestamp}`
            : false;
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
        // if (this.overlay) {
        //     this.overlay.destroy();
        // }
        if (this.canvasContainerRef.el) {
            for (let areaData of Object.values(this.props.overlayPosition.areaList)) {
                let area;
                if (areaData.areaType === RECTANGLE_AREA_TYPE) {
                    area = new RectangleArea(areaData.data, this.canvasContainerRef.el, areaData.index);
                } else if (areaData.areaType === ELLIPSE_AREA_TYPE) {
                    area = new EllipseArea(areaData.data, this.canvasContainerRef.el, areaData.index);
                } else if (areaData.areaType === TEXT_AREA_TYPE) {
                    area = new TextArea(areaData.data, this.canvasContainerRef.el, areaData.index);
                }
                if (area) {
                    area.onSelectedArea(this.onSelectedArea.bind(this));
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
        reader.onload = (ev) => {
            const image = new Image();
            image.src = ev.target.result;
            image.onload = () => {
                this.areas[this.state.selectedAreaIndex].addImageObject(image);
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
