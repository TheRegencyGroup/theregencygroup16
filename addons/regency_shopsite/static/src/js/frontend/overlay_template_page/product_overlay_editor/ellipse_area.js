/** @odoo-module **/

import { Area } from './area';
import { ELLIPSE_AREA_TYPE } from '../../../main';

export class EllipseArea extends Area {
    init() {
        this.areaType = ELLIPSE_AREA_TYPE;
    }

    get newImageObjectWidth() {
        return this.data.rx;
    }

    get newImageObjectHeight() {
        return this.data.ry;
    }

    getMaskObject() {
        return new fabric.Ellipse({
            rx: this.data.rx,
            ry: this.data.ry,
            top: this.data.y - this.data.boundRect.y,
            left: this.data.x - this.data.boundRect.x,
            angle: this.data.angle,
        });
    }
}
