/** @odoo-module **/

import {Area} from './area';

export class TextArea extends Area {
    getMaskObject() {
        return new fabric.Rect({
            width: this.data.width,
            height: this.data.height,
            top: this.data.y - this.data.boundRect.y,
            left: this.data.x - this.data.boundRect.x,
            angle: this.data.angle,
        });
    }

    init() {
        let object = new fabric.Textbox('', {
            width: this.data.width,
            top: this.data.y - this.data.boundRect.y,
            left: this.data.x - this.data.boundRect.x,
            angle: this.data.angle,
            editable: true,
            fontSize: this.data.fontSize,
            lineHeight: 1,
            lockMovementX: true,
            lockMovementY: true,
            hoverCursor: 'text',
        });
        object.setControlsVisibility({
            'mt': false,
            'tl': false,
            'tr': false,
            'mb': false,
            'bl': false,
            'br': false,
            'ml': false,
            'mr': false,
            'mtr': false,
        });
        if (this.data.font) {
            object.set('fontFamily', this.data.font);
        }
        object.isTextArea = true;
        this.canvas.add(object);
        this.clipMask();
        this.canvas.renderAll();
        this.textBox = object;
    }

    reInit() {
        this.canvas.setActiveObject(this.textBox);
        this.canvas.renderAll();
    }

    removeActiveObject() {
        this.textBox.text = '';
        this.selectedArea();
    }

    removeAllObjects() {
        this.textBox.text = '';
        this.selectedArea();
    }
}
