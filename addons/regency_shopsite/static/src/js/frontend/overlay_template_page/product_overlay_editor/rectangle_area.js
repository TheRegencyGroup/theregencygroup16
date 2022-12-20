/** @odoo-module **/

import { Area } from './area';
import { RECTANGLE_AREA_TYPE } from '../../../main';

export class RectangleArea extends Area {
    init() {
        this.areaType = RECTANGLE_AREA_TYPE;
    }

    get newImageObjectWidth() {
        return Math.ceil(this.data.width / 2);
    }

    get newImageObjectHeight() {
        return Math.ceil(this.data.height / 2);
    }

    getMaskObject() {
        return new fabric.Rect({
            width: this.data.width,
            height: this.data.height,
            top: this.data.y - this.data.boundRect.y,
            left: this.data.x - this.data.boundRect.x ,
            angle: this.data.angle,
        });
    }
}
