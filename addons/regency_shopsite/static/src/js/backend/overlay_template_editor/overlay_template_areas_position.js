/** @odoo-module **/

import {
    PRODUCT_IMAGE_MODEL,
    PRODUCT_IMAGE_FIELD,
    AREAS_IMAGE_NON_ATTRIBUTE_VALUE_ID,
    RECTANGLE_AREA_TYPE,
    ELLIPSE_AREA_TYPE,
    TEXT_AREA_TYPE,
    FULL_IMAGE_WIDTH,
    MIN_IMAGE_WIDTH,
    computeImageSrc,
    enableCanvasPointerEvents,
    computeEditorScale,
} from '../../main';
import { AreaParameters, TEXT_AREA_ALIGN_LIST } from './area_parameters';

const { Component, onMounted, onPatched, useState, useRef, reactive, useBus } = owl;

const OVERLAY_AREAS_WIDGET_NAME = 'overlay_areas';
const AREAS_TAB = 'areas_tab';
const IMAGES_TAB = 'images_tab';
const DEFAULT_TEXT_AREA_FONT_SIZE = 14;
const DEFAULT_TEXT_FONT_ID = 'default_0';
const DEFAULT_TEXT_FONT_NAME = 'Arial';

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
            areaList: {},
            editorFullViewMode: false,
            editorFullViewModeContainerStyle: '',
            editorMinViewModeContainerStyle: '',
        });

        this.editorRef = useRef('editor');
        this.canvasRef = useRef('canvas_ref');
        this.imageRef = useRef('image_ref');
        this.canvasContainerRef = useRef('canvas_container_ref');

        this.lastMode = this.mode;
        this.lastSelectedImageIds = this.selectedImageIds;
        this.lastAreasImageAttributeId = this.props.areasImageAttributeId;
        this.areaList = this.props.areaList;
        this.firstEditorImageLoad = false;
        this.imageTimestamp = new Date().valueOf();
        this.fullViewModeScale = 1;
        this.minViewModeScale = 1;

        this.changeAreaFunctions = {
            width: this.changeAreaWidth.bind(this),
            height: this.changeAreaHeight.bind(this),
            rx: this.changeAreaRx.bind(this),
            ry: this.changeAreaRy.bind(this),
            x: this.changeAreaX.bind(this),
            y: this.changeAreaY.bind(this),
            angle: this.changeAreaAngle.bind(this),
            font: this.changeTextAreaFont.bind(this),
            fontSize: this.changeTextAreaFontSize.bind(this),
            lineSpacing: this.changeTextAreaLineSpacing.bind(this),
            charSpacing: this.changeTextAreaCharSpacing.bind(this),
            color: this.changeTextAreaColor.bind(this),
            align: this.changeTextAreaAlign.bind(this),
        };

        this.defaultTextColor = this.props.colorList.length ? this.props.colorList[0] : null;
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

    get editorContainerStyle() {
        return this.state.editorFullViewMode ?
            this.state.editorFullViewModeContainerStyle
            : this.state.editorMinViewModeContainerStyle;
    }

    get showToolsButtons() {
        return this.props.editMode && this.props.allowEditAreas && this.state.activeTab === AREAS_TAB;
    }

    onMounted() {
        this.setImageOnloadCallback();
        this.updateEditorSwitcherImageValueId();
        this.updateEditorImage();
    }

    onPatched() {
        if (this.lastMode !== this.props.editMode) {
            this.lastMode = this.props.editMode;
            if (this.canvas) {
                this.selectableCanvas(this.props.editMode && this.props.allowEditAreas);
                this.highlightArea();
                this.selectArea();
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

    createCanvas(target, areaList) {
        this.canvas = new fabric.Canvas(target);

        for (let area of Object.values(areaList)) {
            if (area.areaType === RECTANGLE_AREA_TYPE) {
                this.addRectangleArea({
                    area,
                    select: false,
                });
            } else if (area.areaType === ELLIPSE_AREA_TYPE) {
                this.addEllipseArea({
                    area,
                    select: false,
                });
            } else if (area.areaType === TEXT_AREA_TYPE) {
                this.addTextArea({
                    area,
                    select: false,
                });
            }
        }
    }

    computeEditorContainerStyles() {
        const imageWidth = this.imageRef.el.clientWidth;
        const imageHeight = this.imageRef.el.clientHeight;
        const fullParams = computeEditorScale({
            width: imageWidth,
            height: imageHeight,
            scaleWidth: FULL_IMAGE_WIDTH,
            transformOrigin: 'top',
        });
        this.state.editorFullViewModeContainerStyle = fullParams.editorStyle;
        this.fullViewModeScale = fullParams.scale;
        const minParams = computeEditorScale({
            width: imageWidth,
            height: imageHeight,
            scaleWidth: MIN_IMAGE_WIDTH,
        });
        this.state.editorMinViewModeContainerStyle = minParams.editorStyle;
        this.minViewModeScale = minParams.scale;
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
                imageId: newImageId,
                width: newWidth,
                height: newHeight,
                src: newProductTemplateImage.image.src,
            };
        } else {
            this.state.editorImageLoaded = false;
            if (this.canvas) {
                this.destroyCanvas();
            }
        }
        if (data.imageId !== this.state.editorImage.imageId) {
            this.state.editorImage = data;
        }
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
        if (this.canvas) {
            this.destroyCanvas();
        }
        this.canvasRef.el.width = this.imageRef.el.clientWidth;
        this.canvasRef.el.height = this.imageRef.el.clientHeight;

        this.createCanvas(this.canvasRef.el, this.areaList);
        this.selectableCanvas(this.props.editMode);
        this.computeEditorContainerStyles();
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

    onClickChangeEditorViewMode(event) {
        this.state.editorFullViewMode = !this.state.editorFullViewMode;
        this.scaleAreasControls();
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
    
    selectAreaListItem(areaIndex) {
        this.state.selectedAreaIndex = areaIndex;
        this.selectArea();
        this.highlightArea();
    }

    selectableCanvas(state) {
        for (let area of Object.values(this.state.areaList)) {
            area.object.selectable = state;
        }
        enableCanvasPointerEvents(this.canvas, state);
    }

    get sizeForNewArea() {
        return Math.floor(Math.min(this.canvas.width, this.canvas.height) / 4);
    }

    get newAreaIndex() {
        let areaListKeys = Object.keys(this.state.areaList).map(e => parseInt(e));
        return (areaListKeys.length ? Math.max(...areaListKeys) : 0) + 1;
    }

    getAreaObjectByIndex(areaIndex) {
        return this.canvas.getObjects().find(e => e.areaIndex === areaIndex);
    }

    getRectangleObjData(object) {
        return {
            width: (!object.scaleX || object.scaleX === 1)  ? object.width : Math.ceil(object.getScaledWidth()),
            height: (!object.scaleY || object.scaleY === 1) ? object.height : Math.ceil(object.getScaledHeight()),
            x: Math.ceil(object.left || 0),
            y: Math.ceil(object.top || 0),
            angle: Math.ceil(object.angle),
        }
    }

    getEllipseObjData(object) {
        return {
            rx: (!object.scaleX || object.scaleX === 1) ? object.rx : Math.ceil(object.getRx()),
            ry: (!object.scaleY || object.scaleY === 1) ? object.ry : Math.ceil(object.getRy()),
            x: Math.ceil(object.left || 0),
            y: Math.ceil(object.top || 0),
            angle: Math.ceil(object.angle),
        }
    }

    getTextObjData(object) {
        return  {
            ...this.getRectangleObjData(object),
            fontSize: object.textAreaFontSize,
            lineSpacing: object.textAreaLineSpacing,
            charSpacing: object.textAreaCharSpacing,
            font: object.textAreaFont,
            color: object.textAreaColor,
            align: object.textAreaAlign,
        };
    }

    createRectangle(index, { width, height, x, y, angle }, select) {
        let object = new fabric.Rect({
            width: width || this.sizeForNewArea,
            height: height || this.sizeForNewArea,
            top: y || 0,
            left: x || 0,
            angle: angle || 0,
            fill: '#0000003D',
        });
        object.areaIndex = index;
        object.areaType = RECTANGLE_AREA_TYPE;
        object.on('modified', this.onObjectModified.bind(this));
        object.on('selected', this.onObjectSelected.bind(this));
        this.canvas.add(object);
        if (select) {
            this.canvas.setActiveObject(object);
        }
        this.canvas.renderAll();
        return object;
    }

    createEllipse(index, { rx, ry, x, y, angle }, select) {
        let defaultRadius = Math.floor(this.sizeForNewArea / 2);
        let object = new fabric.Ellipse({
            rx: rx || defaultRadius,
            ry: ry || defaultRadius,
            top: y || 0,
            left: x || 0,
            angle: angle || 0,
            fill: '#0000003D',
        });
        object.areaIndex = index;
        object.areaType = ELLIPSE_AREA_TYPE;
        object.on('modified', this.onObjectModified.bind(this));
        object.on('selected', this.onObjectSelected.bind(this));
        this.canvas.add(object);
        if (select) {
            this.canvas.setActiveObject(object);
        }
        return object;
    }

    createTextRectangle(
        index,
        {
            width,
            height,
            x,
            y,
            angle,
            fontSize,
            lineSpacing,
            charSpacing,
            font,
            color,
            align,
        },
        select,
    ) {
        let object = new fabric.Rect({
            width: width || this.sizeForNewArea,
            height: height || this.sizeForNewArea,
            top: y || 0,
            left: x || 0,
            angle: angle || 0,
            fill: '#0000003D',
            textAreaFontSize: fontSize || DEFAULT_TEXT_AREA_FONT_SIZE,
            textAreaLineSpacing: lineSpacing || 0,
            textAreaCharSpacing: charSpacing || 0,
            textAreaFont: {
                id: font ? font.id : DEFAULT_TEXT_FONT_ID,
                name: font ? font.name : DEFAULT_TEXT_FONT_NAME,
            },
            textAreaColor: {
                id: color ? color.id : (this.defaultTextColor ? this.defaultTextColor.id : null),
                name: color ? color.name : (this.defaultTextColor ? this.defaultTextColor.name : null),
                color: color ? color.color : (this.defaultTextColor ? this.defaultTextColor.color : null),
            },
            textAreaAlign: align || TEXT_AREA_ALIGN_LIST[0],
        });
        object.areaIndex = index;
        object.areaType = TEXT_AREA_TYPE;
        object.on('modified', this.onObjectModified.bind(this));
        object.on('selected', this.onObjectSelected.bind(this));
        this.canvas.add(object);
        if (select) {
            this.canvas.setActiveObject(object);
        }
        return object;
    }

    onObjectModified(event) {
        this.updateAreaData(this.state.areaList[event.target.areaIndex]);
    }

    onObjectSelected(event) {
         this.state.selectedAreaIndex = event.target.areaIndex;
    }

    computeAreaControlSize() {
        let controlSize = 13;
        if (this.state.editorFullViewMode) {
            controlSize = Math.ceil(controlSize / this.fullViewModeScale);
        } else {
            controlSize = Math.ceil(controlSize / this.minViewModeScale);
        }
        return controlSize;
    }

    computeAreaControlRotateOffset() {
        let offset = 20;
        if (this.state.editorFullViewMode) {
            offset = Math.ceil(offset / this.fullViewModeScale);
        } else {
            offset = Math.ceil(offset / this.minViewModeScale);
        }
        return offset;
    }

    setControlsParams(object) {
        object.padding = 0;
        object.borderColor = 'transparent';
        object.cornerColor = '#000000';
        object.cornerStrokeColor = '#000000';
        object.cornerSize = this.computeAreaControlSize();
        object.transparentCorners = false;
        object.controls.mtr.offsetY = -this.computeAreaControlRotateOffset();
        this.canvas.renderAll();
    }
    addRectangleArea({ area, select=true }) {
        const index = area ? area.index : this.newAreaIndex;
        const data = area ? area.data : {};
        let object = this.createRectangle(index, data, select);
        this.setControlsParams(object);
        this.state.areaList[index] = {
            object,
            index,
            areaType: RECTANGLE_AREA_TYPE,
            change: this.changeAreaFunctions,
            data: this.getRectangleObjData(object),
        }
    }

    addEllipseArea({ area, select=true }) {
        const index = area ? area.index : this.newAreaIndex;
        const data = area ? area.data : {};
        let object = this.createEllipse(index, data, select);
        this.setControlsParams(object);
        this.state.areaList[index] = {
            object,
            index,
            areaType: ELLIPSE_AREA_TYPE,
            change: this.changeAreaFunctions,
            data: this.getEllipseObjData(object),
        }
    }

    addTextArea({ area, select=true }) {
        const index = area ? area.index : this.newAreaIndex;
        const data = area ? area.data : {};
        let object = this.createTextRectangle(index, data, select);
        this.setControlsParams(object);
        this.state.areaList[index] = {
            object,
            index,
            areaType: TEXT_AREA_TYPE,
            change: this.changeAreaFunctions,
            data: this.getTextObjData(object),
        }
    }

    updateAreaData(area) {
        let data = {};
        if (area.areaType === RECTANGLE_AREA_TYPE) {
            data = this.getRectangleObjData(area.object);
        } else if (area.areaType === ELLIPSE_AREA_TYPE) {
            data = this.getEllipseObjData(area.object);
        } else if (area.areaType === TEXT_AREA_TYPE) {
            data = this.getTextObjData(area.object);
        }
        area.data = data;
    }

    changeAreaObjectParam(param, areaIndex, val) {
        const area = this.state.areaList[areaIndex];
        area.object.set(param, val);
        this.canvas.renderAll();
        this.updateAreaData(area);
    }

    changeAreaWidth(areaIndex, val) {
        const area = this.state.areaList[areaIndex];
        area.object.scale(1, 1);
        area.object.set('height', area.data.height);
        area.object.set('width', val);
        this.canvas.renderAll();
        this.updateAreaData(area);
    }

    changeAreaHeight(areaIndex, val) {
        const area = this.state.areaList[areaIndex];
        area.object.scale(1, 1);
        area.object.set('width', area.data.width);
        area.object.set('height', val);
        this.canvas.renderAll();
        this.updateAreaData(area);
    }

    changeAreaX(areaIndex, val) {
        this.changeAreaObjectParam('left', areaIndex, val);
    }

    changeAreaY(areaIndex, val) {
        this.changeAreaObjectParam('top', areaIndex, val);
    }

    changeAreaRx(areaIndex, val) {
        this.changeAreaObjectParam('rx', areaIndex, val);
    }

    changeAreaRy(areaIndex, val) {
        this.changeAreaObjectParam('ry', areaIndex, val);
    }

    changeAreaAngle(areaIndex, val) {
        this.changeAreaObjectParam('angle', areaIndex, val);
    }

    changeTextAreaFontSize(areaIndex, fontSize) {
        const area = this.state.areaList[areaIndex];
        area.object.textAreaFontSize = fontSize;
        this.updateAreaData(area);
    }

    changeTextAreaLineSpacing(areaIndex, lineSpacing) {
        const area = this.state.areaList[areaIndex];
        area.object.textAreaLineSpacing = lineSpacing;
        this.updateAreaData(area);
    }

    changeTextAreaCharSpacing(areaIndex, charSpacing) {
        const area = this.state.areaList[areaIndex];
        area.object.textAreaCharSpacing = charSpacing;
        this.updateAreaData(area);
    }

    changeTextAreaFont(areaIndex, font) {
        const area = this.state.areaList[areaIndex];
        area.object.textAreaFont = font;
        this.updateAreaData(area);
    }
    
    changeTextAreaColor(areaIndex, color) {
        const area = this.state.areaList[areaIndex];
        area.object.textAreaColor = color;
        this.updateAreaData(area);
    }

    changeTextAreaAlign(areaIndex, align) {
        const area = this.state.areaList[areaIndex];
        area.object.textAreaAlign = align;
        this.updateAreaData(area);
    }

    removeArea(areaIndex) {
        if (this.state.selectedAreaIndex === areaIndex) {
            this.state.selectedAreaIndex = null;
        }
        this.canvas.discardActiveObject().renderAll();
        this.canvas.remove(this.getAreaObjectByIndex(areaIndex));
        delete this.state.areaList[areaIndex];
    }

    selectArea() {
        if (this.props.editMode && this.props.allowEditAreas && this.state.selectedAreaIndex) {
            this.canvas.setActiveObject(this.state.areaList[this.state.selectedAreaIndex].object).renderAll();
        } else {
            this.canvas.discardActiveObject().renderAll();
        }
    }

    highlightArea() {
        for (let area of Object.values(this.state.areaList)) {
            area.object.set('fill', '#0000003D');
        }
        if (!(this.props.editMode && this.props.allowEditAreas) && this.state.selectedAreaIndex) {
            this.state.areaList[this.state.selectedAreaIndex].object.set('fill', '#E5112473');
        }
        this.canvas.renderAll();
    }

    scaleAreasControls() {
        for (let area of Object.values(this.state.areaList)) {
            this.setControlsParams(area.object);
        }
        this.canvas.renderAll();
    }

    destroyCanvas() {
        this.canvas.dispose();
        this.canvas = null;
        this.state.areaList = {};
        this.areaList = {};
    }
}

OverlayAreasPositionComponent.components = {
  AreaParameters,
};

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
    fontList: Array,
    colorList: Array,
}

OverlayAreasPositionComponent.template = 'overlay_areas_position'

export {
    OverlayAreasPositionComponent,
}
