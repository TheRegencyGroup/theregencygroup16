/** @odoo-module **/

import {
    ELLIPSE_AREA_TYPE,
    RECTANGLE_AREA_TYPE,
    TEXT_AREA_TYPE,
} from '../../main';

const { useState } = owl;

export class Area {

    constructor(data, parent, areaIndex) {
        this.data = data;
        this.parent = parent;
        this.areaIndex = areaIndex;

        this.createCanvas();
        this.createMask();
        this.init();
    }

    init() {}

    get newImageObjectWidth() {}

    get newImageObjectHeight() {}

    getMaskObject() {}

    createMask() {
        let object = this.getMaskObject();
        object.isAreaMask = true;
        object.fill = 'transparent';
        object.stroke = '#000000';
        object.strokeWidth = 1;
        object.hoverCursor = 'default';
        object.selectable = false;
        this.canvas.add(object);
        this.mask = object;
        this.mask.on('mouseover', this.onMaskMouseover.bind(this));
        this.mask.on('mouseout', this.onMaskMouseout.bind(this));
    }

    removeMask() {
        this.canvas.remove(this.mask);
        this.canvas.renderAll();
    }

    clipMask() {
        this.canvas.clipPath = this.getMaskObject();
    }

    createCanvas() {
        this.canvasEl = document.createElement('canvas');
        this.canvasEl.width = this.data.boundRect.width + 2;
        this.canvasEl.height = this.data.boundRect.height + 2;
        this.areaEl = document.createElement('div');
        this.areaEl.classList.add('product_overlay_area');
        this.areaEl.style.top = this.data.boundRect.y + 'px';
        this.areaEl.style.left = this.data.boundRect.x + 'px';
        this.areaEl.appendChild(this.canvasEl);
        this.parent.appendChild(this.areaEl);

        this.canvas = new fabric.Canvas(this.canvasEl);
        this.canvas.on('mouse:down', this.onCanvasMousedown.bind(this));
    }

    onMaskMouseover(event) {
        this.mask.set('stroke', 'red');
        this.canvas.renderAll();
    }

    onMaskMouseout(event) {
        this.mask.set('stroke', '#000000');
        this.canvas.renderAll();
    }

    onCanvasMousedown(event) {
        if (event.target) {
            this.selectedAreaCallback(this.areaIndex);
            this.selectedArea();
        }
    }

    onSelectedArea(f) {
        this.selectedAreaCallback = f;
    }

    selectedArea() {
        this.canvas.backgroundColor = '#00000022';
        this.clipMask();
        this.canvas.renderAll();
    }

    unselectedArea() {
        this.canvas.backgroundColor = 'transparent';
        this.clipMask();
        this.canvas.renderAll();
    }

    addImageObject(image) {
        const object = new fabric.Image(image, {});
        if (image.width >= image.height) {
            object.scaleToWidth(this.newImageObjectWidth);
        } else {
            object.scaleToHeight(this.newImageObjectHeight);
        }
        this.canvas.centerObject(object);
        this.canvas.add(object);
        this.clipMask();
    }

    removeActiveObject(){
        this.canvas.remove(this.canvas.getActiveObject());
    }

    removeAllObjects(){
        this.canvas.clear();
        this.createMask();
        this.selectedArea();
    }

    async getOverlayImagesData() {
        this.canvas.discardActiveObject().renderAll();
        this.removeMask();
        this.unselectedArea();
        return await new Promise((resolve) => {
            this.canvasEl.toBlob((blob) => {
                this.createMask();
                this.clipMask();
                this.selectedArea();
                this.reInit();
                let reader = new FileReader();
                reader.onloadend = () => {
                    let base64data = reader.result;
                    resolve({
                        data: base64data.split(',')[1],
                        size: {
                            x: this.data.boundRect.x,
                            y: this.data.boundRect.y,
                        },
                    });
                }
                reader.readAsDataURL(blob);
            });
        });
    }

    reInit() {}

    checkAreas() {
        let objects = this.canvas.getObjects();
        objects = objects.filter(e => !e.isAreaMask);
        objects = objects.filter(e => !e.isTextArea || (!!e.isTextArea && !!e.text));
        return !!objects.length;
    }

    destroy () {
        this.canvas.dispose();
    }
}
