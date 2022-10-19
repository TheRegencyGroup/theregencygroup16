/** @odoo-module **/

import {Area} from './area';

export class EllipseArea extends Area {
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
