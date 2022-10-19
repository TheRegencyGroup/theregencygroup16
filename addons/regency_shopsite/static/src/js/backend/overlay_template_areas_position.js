/** @odoo-module **/

import {Overlay} from './overlay';

const {Component, onMounted, onPatched, useState, useRef} = owl;

const OVERLAY_AREAS_WIDGET_NAME = 'overlay_areas';
const AREAS_TAB = 'areas_tab';
const IMAGES_TAB = 'images_tab';

class OverlayAreasPositionComponent extends Component {
    setup() {
        this.AREAS_TAB = AREAS_TAB;
        this.IMAGES_TAB = IMAGES_TAB;

        onPatched(this.onPatched);
        onMounted(this.onMounted);

        this.state = useState({
            imageLoad: false,
            imageSrc: null,
            selectedAreaIndex: null,
            activeTab: AREAS_TAB,
        });

        this.canvasRef = useRef('canvas_ref');
        this.imageRef = useRef('image_ref');
        this.canvasContainerRef = useRef('canvas_container_ref');

        this.setCurrentData();
        this.currentMode = this.mode;

        this.currentImageTimestamp = new Date().valueOf();
    }

    onMounted() {
        this.setImageOnloadCallback();
        // TODO: implement proper solution
        this.updateCanvas(); //TEMPORARY!!!!!!!!!!!!!!!
        let image = this.getImageForOverlay();
        if (image) {
            this.state.imageSrc = this.getImageSrc(image.imageId, image.imageModel);
            this.setCurrentData();
        }
    }

    onPatched() {
        if (this.currentMode !== this.props.editMode) {
            this.currentMode = this.props.editMode;
            if (this.overlay) {
                this.overlay.selectable = !!this.props.editMode;
            }
        }
        let colorImages = Object.values(this.props.colorImages).filter(e => !!e.imageId && !!e.imageModel);
        let imageIds = colorImages.map(e => e.imageId);
        let imageModel = colorImages.map(e => e.imageModel);
        if (!imageIds.includes(this.state.currentData.imageId) ||
            !imageModel.includes(this.state.currentData.imageModel)) {
            this.setCurrentData();
            if (this.overlay) {
                this.overlay.destroy();
                this.overlay = null;
            }
            this.state.imageLoad = false;
            this.state.imageSrc = this.getImageSrc(this.state.currentData.imageId, this.state.currentData.imageModel);
            this.updateCanvas(); //TEMPORARY!!!!!!!!!!!!!!!
        }
    }

    setCurrentData(colorId) {
        let imageId = false;
        let imageModel = false;
        if (colorId) {
            imageId = this.props.colorImages[colorId]?.imageId;
            imageModel = this.props.colorImages[colorId]?.imageModel;
        } else {
            let image = this.getImageForOverlay();
            if (image) {
                imageId = image.imageId;
                imageModel = image.imageModel;
            }
        }
        this.state.currentData = {imageId, imageModel};
    }

    getImageForOverlay() {
        return Object.values(this.props.colorImages).find(e => !!e.imageId && !!e.imageModel);
    }

    setImageOnloadCallback() {
        if (!this.imageRef.el) {
            return;
        }
        this.imageRef.el.onload = () => {
            if (!this.state.imageLoad) {
                this.state.imageLoad = true;
                // this.updateCanvas();
            }
        };
    }

    getImageSrc(id, model) {
        let baseUrl = window.location.origin;
        return (id && model)
            ? `${baseUrl}/web/image?model=${model}&id=${id}&field=image_512&unique=${this.currentImageTimestamp}`
            : false;
    }

    updateCanvas() {
        if (this.overlay) {
            this.overlay.destroy();
        }
        // if (this.imageRef.el) {
        // this.canvasRef.el.width = this.imageRef.el.clientWidth;
        // this.canvasRef.el.height = this.imageRef.el.clientHeight;
        this.canvasRef.el.width = 500;
        this.canvasRef.el.height = 500;

        this.overlay = new Overlay(this.canvasRef.el, this.props.areaList);
        this.overlay.selectable = this.props.editMode;
        this.overlay.onSelectedArea = (areaIndex) => {
            this.state.selectedAreaIndex = areaIndex;
        };
        // }
    }

    // onClickChangeImage(event) {
    //     this.trigger('change-overlay-image', {
    //         id: this.props.overlayPositionId,
    //     });
    // }

    onClickAddRectangleArea(event) {
        this.overlay.addRectangleArea();
    }

    onClickAddEllipseArea(event) {
        this.overlay.addEllipseArea();
    }

    onClickAddTextArea(event) {
        this.overlay.addTextArea();
    }

    onClickAreaListItem(areaIndex, event) {
        if (this.props.editMode) {
            this.overlay.selectArea(areaIndex);
        } else {
            this.overlay.highlightArea(areaIndex);
        }
        this.state.selectedAreaIndex = areaIndex;
    }

    onClickRemoveArea(areaIndex, event) {
        if (this.state.selectedAreaIndex === areaIndex) {
            this.state.selectedAreaIndex = null;
        }
        this.overlay.removeArea(areaIndex);
    }

    onChangeTextFontSize(areaIndex, event) {
        let newFontSize = parseInt(event.target.value);
        this.overlay.changeTextAreaFontSize(areaIndex, newFontSize);
    }

    onChangeTextNumberOfLines(areaIndex, event) {
        let newNumberOfLines = parseInt(event.target.value);
        this.overlay.changeTextAreaNumberOfLines(areaIndex, newNumberOfLines);
    }

    onChangeTextFont(areaIndex, event) {
        let font = event.target.value;
        this.overlay.changeTextAreaFont(areaIndex, font);
    }

    onClickOpenAreasTab(event) {
        if (this.state.activeTab !== AREAS_TAB) {
            this.state.activeTab = AREAS_TAB;
        }
    }

    onClickOpenImagesTab(event) {
        if (this.state.activeTab !== IMAGES_TAB) {
            this.state.activeTab = IMAGES_TAB;
        }
    }

    onClickChangeColorImage(colorId) {
        this.props.changeOverlayImage({
            id: this.props.overlayPositionId,
            colorId,
        });
    }

    onClickOverlayColorImage(colorId, event) {
        this.setCurrentData(colorId);
        this.state.imageSrc = this.getImageSrc(this.state.currentData.imageId, this.state.currentData.imageModel);
    }
}

OverlayAreasPositionComponent.props = {
    overlayPositionId: Number,
    overlayPositionName: String,
    productTemplateId: Number,
    areaList: Object,
    editMode: Boolean,
    colorImages: Object,
    changeOverlayImage: Function,
}

OverlayAreasPositionComponent.template = 'overlay_areas_position'

export {
    OverlayAreasPositionComponent,
}
