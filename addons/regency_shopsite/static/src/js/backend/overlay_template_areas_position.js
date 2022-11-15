/** @odoo-module **/

import { Overlay } from './overlay';
import {
    PRODUCT_IMAGE_MODEL,
    PRODUCT_IMAGE_FIELD,
    AREAS_IMAGE_NON_ATTRIBUTE_VALUE_ID,
    computeImageSrc,
} from '../main';

const { Component, onMounted, onPatched, useState, useRef } = owl;

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
            editorImageLoaded: false,
            editorImage: false,
            editorSwitcherImageValueId: false,
            selectedAreaIndex: false,
            activeTab: AREAS_TAB,
        });

        this.canvasRef = useRef('canvas_ref');
        this.imageRef = useRef('image_ref');
        this.canvasContainerRef = useRef('canvas_container_ref');

        this.lastMode = this.mode;
        this.lastSelectedImageIds = this.selectedImageIds;
        this.lastAreasImageAttributeId = this.props.areasImageAttributeId;
        this.areaList = this.props.areaList;

        this.firstEditorImageLoad = false;
        this.imageTimestamp = new Date().valueOf();
    }

    get areasImageValueList() {
        return this.props.areasImageValueList.map(e => {
            let selectedImageId = false;
            if (this.props.selectedImages[e.id]) {
               selectedImageId = this.props.selectedImages[e.id].imageId;
            }
            const selectedImageSrc = selectedImageId
                ? computeImageSrc({
                    id: selectedImageId,
                    model: PRODUCT_IMAGE_MODEL,
                    field: PRODUCT_IMAGE_FIELD,
                    timestamp: this.imageTimestamp,
                })
                : false;
            return {
                ...e,
                selectedImageSrc,
            };
        });
    }
    
    get selectedImageIds() {
        return Object.values(this.props.selectedImages).map(e => e.imageId).sort((a, b) => a - b);
    }

    get showEditorImageSwitcher() {
        const selectedImages = Object.values(this.props.selectedImages);
        return selectedImages.length && !selectedImages.find(e => e.valueId === AREAS_IMAGE_NON_ATTRIBUTE_VALUE_ID);
    }

    get editorSwitcherImageList() {
        return Object.values(this.props.selectedImages).map(e => ({
            ...e,
            imageSrc: computeImageSrc({
                id: e.imageId,
                model: PRODUCT_IMAGE_MODEL,
                field: PRODUCT_IMAGE_FIELD,
                timestamp: this.imageTimestamp,
            }),
            name: this.props.areasImageValueList.find(f => f.id === e.valueId).name,
        }));
    }

    onMounted() {
        this.setImageOnloadCallback();
        this.updateEditorSwitcherImageValueId();
        this.updateEditorImage();
    }

    onPatched() {
        if (this.lastMode !== this.props.editMode) {
            this.lastMode = this.props.editMode;
            if (this.overlay) {
                this.overlay.selectable = !!this.props.editMode && this.props.allowEditAreas;
            }
        }
        if (this.lastAreasImageAttributeId !== this.props.areasImageAttributeId) {
            this.lastAreasImageAttributeId = this.props.areasImageAttributeId;
            this.state.editorSwitcherImageValueId = false;
            this.updateEditorSwitcherImageValueId();
            this.updateEditorImage();
        }
        if (JSON.stringify(this.lastSelectedImageIds) !== JSON.stringify(this.selectedImageIds)) {
            this.lastSelectedImageIds = this.selectedImageIds;
            this.updateEditorSwitcherImageValueId();
            this.updateEditorImage();
        }
        if (!!Object.keys(this.areaList).length && !Object.keys(this.props.areaList).length) {
            this.areaList = this.props.areaList;
        }
    }

    updateEditorSwitcherImageValueId() {
        if ((!this.state.editorSwitcherImageValueId ||
                !this.props.selectedImages[this.state.editorSwitcherImageValueId]) &&
            !!this.selectedImageIds.length) {
            this.state.editorSwitcherImageValueId = Object.values(this.props.selectedImages)
                .find(e => e.imageId === this.selectedImageIds[0])
                .valueId;
        } else if (this.state.editorSwitcherImageValueId && !this.selectedImageIds.length) {
            this.state.editorSwitcherImageValueId = false;
        }
    }
    
    updateEditorImage() {
        let data = false;
        if (Object.values(this.props.selectedImages).length && this.state.editorSwitcherImageValueId !== false) {
            const newImageId = this.props.selectedImages[this.state.editorSwitcherImageValueId].imageId;
            const newProductTemplateImage = this.props.productTemplateImages.find(e => e.id === newImageId);
            const newWidth = newProductTemplateImage.image.width;
            const newHeight = newProductTemplateImage.image.height;
            if (newWidth !== this.state.editorImage.width || newHeight !== this.state.editorImage.height) {
                this.state.editorImageLoaded = false;
            }
            data = {
                width: newWidth,
                height: newHeight,
                src: computeImageSrc({
                    id: newImageId,
                    model: PRODUCT_IMAGE_MODEL,
                    field: 'image_1920',
                    timestamp: this.imageTimestamp,
                })
            };
        } else {
            this.state.editorImageLoaded = false;
            if (this.overlay) {
                this.destroyOverlay();
            }
        }
        this.state.editorImage = data;
    }

    setImageOnloadCallback() {
        this.imageRef.el.onload = () => {
            if (!this.firstEditorImageLoad) {
                this.firstEditorImageLoad = true;
            }
            if (!this.state.editorImageLoaded) {
                this.state.editorImageLoaded = true;
                this.updateCanvas();
            }
        };
    }

    updateCanvas() {
        if (this.overlay) {
            this.destroyOverlay();
        }
        this.canvasRef.el.width = this.imageRef.el.clientWidth;
        this.canvasRef.el.height = this.imageRef.el.clientHeight;

        this.overlay = new Overlay(this.canvasRef.el, this.areaList);
        this.overlay.selectable = this.props.editMode;
        this.overlay.onSelectedArea = (areaIndex) => {
            this.state.selectedAreaIndex = areaIndex;
        };
    }

    destroyOverlay() {
        this.overlay.destroy();
        this.overlay = null;
        this.areaList = {};
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

    onClickChangeValueImage(areasImageAttributeValueId) {
        this.props.openImageListModal({
            overlayPositionId: this.props.overlayPositionId,
            areasImageAttributeValueId,
        });
    }

    onChangeEditorImage(valueId) {
        this.state.editorSwitcherImageValueId = valueId;
        this.updateEditorImage();
    }

    onChangeTextFont(areaIndex, event) {
        let font = event.target.value;
        this.overlay.changeTextAreaFont(areaIndex, font);
    }

    onClickAddRectangleArea(event) {
        this.overlay.addRectangleArea();
    }

    onClickAddEllipseArea(event) {
        this.overlay.addEllipseArea();
    }

    onClickAddTextArea(event) {
        // this.overlay.addTextArea();
    }

    onClickAreaListItem(areaIndex) {
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
}

OverlayAreasPositionComponent.props = {
    editMode: Boolean,
    productTemplateId: Number,
    overlayPositionId: Number,
    overlayPositionName: String,
    areasImageAttributeId: Number,
    areaList: Object,
    selectedImages: Object,
    areasImageValueList: Array,
    productTemplateImages: Array,
    openImageListModal: Function,
    allowEditAreas: Boolean,
}

OverlayAreasPositionComponent.template = 'overlay_areas_position'

export {
    OverlayAreasPositionComponent,
}
