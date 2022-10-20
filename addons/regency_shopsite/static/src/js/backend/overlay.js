/** @odoo-module **/

import {
    ELLIPSE_AREA_TYPE,
    RECTANGLE_AREA_TYPE,
    TEXT_AREA_TYPE,
} from '../main';

const DEFAULT_TEXT_AREA_FONT_SIZE = 14;
const DEFAULT_TEXT_AREA_NUMBER_LINES = 1;
const DEFAULT_TEXT_FONT = 'Arial';

class Overlay {
    constructor(target, areaList) {
        this.canvas = new fabric.Canvas(target);

        this.areaList_ = areaList || {};

        for (let area of Object.values(this.areaList_)) {
            if (area.areaType === RECTANGLE_AREA_TYPE) {
                area.object = this.createRectangle(area.index, area.data, false);
            } else if (area.areaType === ELLIPSE_AREA_TYPE) {
                area.object = this.createEllipse(area.index, area.data, false);
            } else if (area.areaType === TEXT_AREA_TYPE) {
                area.object = this.createTextRectangle(area.index, area.data, false);
            }
        }
    }

    set selectable(state) {
        for (let area of Object.values(this.areaList_)) {
            area.object.selectable = state;
        }
    }

    set onSelectedArea(f) {
        this.onSelectedAreaCallback = f;
    }

    get areaList() {
        return this.areaList_;
    }

    get sizeForNewArea() {
        return Math.floor(Math.min(this.canvas.width, this.canvas.height) / 4);
    }

    get newAreaIndex() {
        let areaListKeys = Object.keys(this.areaList_).map(e => parseInt(e));
        return (areaListKeys.length ? Math.max(...areaListKeys) : 0) + 1;
    }

    getAreaObjectByIndex(areaIndex) {
        return this.canvas.getObjects().find(e => e.areaIndex === areaIndex);
    }

    getRectangleObjData(object) {
        return {
            width: Math.ceil(object.getScaledWidth()),
            height: Math.ceil(object.getScaledHeight()),
            x: Math.ceil(object.left || 0),
            y: Math.ceil(object.top || 0),
            angle: Math.ceil(object.angle),
        }
    }

    getEllipseObjData(object) {
        return {
            rx: Math.ceil(object.getRx()),
            ry: Math.ceil(object.getRy()),
            x: Math.ceil(object.left || 0),
            y: Math.ceil(object.top || 0),
            angle: Math.ceil(object.angle),
        }
    }

    getTextObjData(object) {
        let data = {
            width: Math.ceil(object.getScaledWidth()),
            height: this.getTextLineHeight(object.textAreaFontSize, object.textAreaFont) * object.textAreaNumberOfLines,
            fontSize: object.textAreaFontSize,
            numberOfLines: object.textAreaNumberOfLines,
            x: Math.ceil(object.left || 0),
            y: Math.ceil(object.top || 0),
            angle: Math.ceil(object.angle),
        };
        if (object.textAreaFont) {
            data.font = object.textAreaFont;
        }
        return data;
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

    getTextLineHeight(fontSize, font) {
        let tempTb = new fabric.Textbox('123', {
            fontSize: fontSize,
            lineHeight: 1,
            fontFamily: font,
        });
        return tempTb.getScaledHeight();
    }

    createTextRectangle(index, { width, fontSize, numberOfLines, font, x, y, angle }, select) {
        fontSize = fontSize || DEFAULT_TEXT_AREA_FONT_SIZE;
        numberOfLines = numberOfLines || DEFAULT_TEXT_AREA_NUMBER_LINES;
        let object = new fabric.Rect({
            width: width || this.sizeForNewArea,
            height: this.getTextLineHeight(fontSize, DEFAULT_TEXT_FONT) * numberOfLines,
            top: y || 0,
            left: x || 0,
            angle: angle || 0,
            fill: '#0000003D',
            textAreaFontSize: fontSize,
            textAreaNumberOfLines: numberOfLines,
            textAreaFont: font || DEFAULT_TEXT_FONT,
        });
        object.areaIndex = index;
        object.areaType = TEXT_AREA_TYPE;
        object.setControlsVisibility({
            'mt': false,
            'tl': false,
            'tr': false,
            'mb': false,
            'bl': false,
            'br': false,
        });
        object.on('modified', this.onObjectModified.bind(this));
        object.on('selected', this.onObjectSelected.bind(this));
        this.canvas.add(object);
        if (select) {
            this.canvas.setActiveObject(object);
        }
        return object;
    }

    onObjectModified(event) {
        let object = event.target;
        if (object.areaType === RECTANGLE_AREA_TYPE) {
            this.areaList_[object.areaIndex].data = this.getRectangleObjData(object);
        } else if (object.areaType === ELLIPSE_AREA_TYPE) {
            this.areaList_[object.areaIndex].data = this.getEllipseObjData(object);
        } else if (object.areaType === TEXT_AREA_TYPE) {
            this.areaList_[object.areaIndex].data = this.getTextObjData(object);
        }
    }

    onObjectSelected(event) {
        this.onSelectedAreaCallback(event.target.areaIndex);
    }

    addRectangleArea() {
        let index = this.newAreaIndex;
        let object = this.createRectangle(index, {}, true);
        this.areaList_[index] = {
            object,
            index,
            areaType: RECTANGLE_AREA_TYPE,
            data: this.getRectangleObjData(object),
        }
    }

    addEllipseArea() {
        let index = this.newAreaIndex;
        let object = this.createEllipse(index, {}, true);
        this.areaList_[index] = {
            object,
            index,
            areaType: ELLIPSE_AREA_TYPE,
            data: this.getEllipseObjData(object),
        }
    }

    addTextArea() {
        let index = this.newAreaIndex;
        let object = this.createTextRectangle(index, {}, true);
        this.areaList_[index] = {
            object,
            index,
            areaType: TEXT_AREA_TYPE,
            data: this.getTextObjData(object),
        }
    }

    changeTextAreaFontSize(areaIndex, newFontSize) {
        let area = this.areaList_[areaIndex];
        area.object.textAreaFontSize = newFontSize;
        area.object.set('height', this.getTextLineHeight(newFontSize, area.object.textAreaFont) * area.object.textAreaNumberOfLines);
        area.data = this.getTextObjData(area.object);
        this.canvas.renderAll();
    }

    changeTextAreaNumberOfLines(areaIndex, newNumberOfLines) {
        let area = this.areaList_[areaIndex];
        area.object.textAreaNumberOfLines = newNumberOfLines;
        area.object.set('height', newNumberOfLines * this.getTextLineHeight(area.object.textAreaFontSize, area.object.textAreaFont));
        area.data = this.getTextObjData(area.object);
        this.canvas.renderAll();
    }

    changeTextAreaFont(areaIndex, font) {
        let area = this.areaList_[areaIndex];
        area.object.textAreaFont = font;
        area.object.set('height', area.object.textAreaNumberOfLines * this.getTextLineHeight(area.object.textAreaFontSize, area.object.textAreaFont));
        area.data = this.getTextObjData(area.object);
        this.canvas.renderAll();
    }

    removeArea(areaIndex) {
        this.canvas.remove(this.getAreaObjectByIndex(areaIndex));
        delete this.areaList_[areaIndex];
    }

    selectArea(areaIndex) {
        this.canvas.setActiveObject(this.areaList_[areaIndex].object).renderAll();
    }

    highlightArea(areaIndex) {
        for (let area of Object.values(this.areaList_)) {
            area.object.set('fill', '#0000003D');
        }
        this.areaList_[areaIndex].object.set('fill', '#E5112473');
        this.canvas.renderAll();
    }

    destroy() {
        this.canvas.dispose();
        this.areaList_ = {};
    }
}

export {
    Overlay,
}
