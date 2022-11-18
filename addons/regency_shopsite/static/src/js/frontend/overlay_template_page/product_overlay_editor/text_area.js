/** @odoo-module **/

import { RectangleArea } from './rectangle_area';

export class TextArea extends RectangleArea {
    initAreaObjects() {
        if (this.areaObjectData && this.areaObjectData.length) {
            this.objectIndex = Math.max(...this.areaObjectData.map(e => e.index)) + 1;
            for (let textObj of this.areaObjectData) {
                this.addObject({
                    objIndex: textObj.index,
                    data: textObj.objectData,
                });
            }
        }
    }

    addObject({ text, objIndex, data, addByUser }) {
        if (addByUser) {
            this.wasChanged = true;
        }
        if (!text) {
            text = data.text;
        }
        const object = new fabric.Textbox(text, {
            editable: false,
            fill: this.data.color.color || '#000000',
            fontFamily: this.data.font.name,
            fontSize: this.data.fontSize,
            lineHeight: 1,
        });
        if (!objIndex) {
            objIndex = this.objectIndex;
            this.objectIndex += 1;
        }
        object.objIndex = objIndex;
        if (!data) {
            this.canvas.centerObject(object);
        } else {
            object.left = data.x;
            object.top = data.y;
            object.angle = data.angle;
        }
        this.objectList[objIndex] = {
            index: objIndex,
            text,
            object,
        };
        object.setControlsVisibility({
            'mt': false,
            'tl': false,
            'tr': false,
            'mb': false,
            'bl': false,
            'br': false,
            'ml': false,
            'mr': false,
        });
        object.on('moving', () => this.wasChanged = true);
        object.on('scaling', () => this.wasChanged = true);
        this.canvas.add(object);
        this.clipMask();
    }

    getOverlayData() {
        this.canvas.discardActiveObject().renderAll();
        this.unselectedArea();

        let res = [];
        for (let textObj of Object.values(this.objectList)) {
            res.push({
                index: textObj.index,
                objectData: {
                    text: textObj.object.text,
                    fontName: textObj.object.fontFamily,
                    fontColor: textObj.object.fill,
                    fontSize: textObj.object.fontSize,
                    x: Math.ceil(textObj.object.left),
                    y: Math.ceil(textObj.object.top),
                    angle: Math.ceil(textObj.object.angle),
                },
            });
        }
        return res;
    }
}
