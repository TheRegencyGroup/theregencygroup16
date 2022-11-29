/** @odoo-module **/

import env from 'web.public_env';
import {
    enableCanvasPointerEvents,
    readImageDataFromFile,
} from '../../../main';

export class Area {

    constructor(areaInitData, parent, areaObjectData) {
        this.data = areaInitData.data;
        this.areaIndex = areaInitData.index;
        this.type = areaInitData.areaType;
        this.parent = parent;
        this.areaObjectData = areaObjectData;

        this.objectList = {};
        this.objectIndex = 1;

        this.createCanvas();
        this.createMask();
        this.init();
        this.initAreaObjects()

        this.enablePointerEvents(false);

        this.wasChanged = false;
    }

    init() {}

    initAreaObjects() {
        if (this.areaObjectData && this.areaObjectData.length) {
            this.objectIndex = Math.max(...this.areaObjectData.map(e => e.index)) + 1;
            let promises = []
            for (let imageObj of this.areaObjectData) {
                promises.push(new Promise(async (resolve, reject) => {
                    try {
                        let res = await env.services.rpc({
                            route: '/shop/area_image',
                            params: {
                               overlay_product_area_image_id: imageObj.areaImageId,
                            },
                        });
                        const image = new Image();
                        image.src = res.bitmap;
                        image.onload = () => {
                            resolve({
                                previewImage: image,
                                originalImageData: res.vector,
                                imageType: imageObj.imageType,
                                imageExtension: imageObj.imageExtension,
                                objIndex: imageObj.index,
                                data: imageObj.objectData,
                            });
                        };
                    } catch (e) {
                        alert(e.message?.data?.message || e.toString());
                        reject();
                    }
                }));
            }
            Promise.all(promises).then((res) => {
                for (let obj of res) {
                    this.addObject(obj);
                }
            });
        }
    }

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

    addObject({
                  previewImage,
                  originalImageData,
                  imageType,
                  imageExtension,
                  objIndex,
                  data,
                  addByUser,
              }) {
        if (addByUser) {
            this.wasChanged = true;
        }
        const object = new fabric.Image(previewImage, {});
        if (!objIndex) {
            objIndex = this.objectIndex;
            this.objectIndex += 1;
        }
        object.objIndex = objIndex;
        if (!data) {
            if (previewImage.width >= previewImage.height) {
                object.scaleToWidth(this.newImageObjectWidth);
            } else {
                object.scaleToHeight(this.newImageObjectHeight);
            }
            this.canvas.centerObject(object);
        } else {
            object.scaleToWidth(data.width);
            object.scaleToHeight(data.height);
            object.left = data.x;
            object.top = data.y;
            object.angle = data.angle;
        }

        this.objectList[objIndex] = {
            index: objIndex,
            image: originalImageData || previewImage.src,
            imageType,
            imageExtension,
            object,
        };
        object.setControlsVisibility({
            'mb': false,
            'ml': false,
            'mr': false,
            'mt': false,
        });
        object.on('moving', () => this.wasChanged = true);
        object.on('scaling', () => this.wasChanged = true);
        this.canvas.add(object);
        this.clipMask();
    }

    removeActiveObject() {
        let activeObj = this.canvas.getActiveObject();
        if (!activeObj) {
            return;
        }
        delete this.objectList[activeObj.objIndex];
        this.canvas.remove(activeObj);
        this.wasChanged = true;
    }

    removeAllObjects() {
        this.canvas.clear();
        this.createMask();
        this.selectedArea();
        this.objectList = {};
        this.wasChanged = true;
    }

    getOverlayData() {
        this.canvas.discardActiveObject().renderAll();
        this.unselectedArea();

        let res = [];
        for (let imageObj of Object.values(this.objectList)) {
            res.push({
                index: imageObj.index,
                image: imageObj.image,
                imageType: imageObj.imageType,
                imageExtension: imageObj.imageExtension,
                objectData: {
                    width: Math.ceil(imageObj.object.getScaledWidth()),
                    height: Math.ceil(imageObj.object.getScaledHeight()),
                    x: Math.ceil(imageObj.object.left),
                    y: Math.ceil(imageObj.object.top),
                    angle: Math.ceil(imageObj.object.angle),
                },
            });
        }
        return res;
    }

    async getPreviewImageData() {
        this.canvas.discardActiveObject().renderAll();
        this.removeMask();
        this.unselectedArea();
        return new Promise((resolve) => {
            let canvasEl = this.canvas.upperCanvasEl;
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
                        scale: +(canvasEl.clientWidth / canvasEl.width).toFixed(2),
                    });
                }
                reader.readAsDataURL(blob);
            });
        });
    }

    reInit() {}

    enablePointerEvents(state) {
        enableCanvasPointerEvents(this.canvas, state);
    }

    showMaskBorders(state) {
        this.mask.set('stroke', state ? '#000000' : 'transparent');
        this.canvas.backgroundColor = 'transparent';
        this.canvas.renderAll();
    }

    destroy() {
        this.canvas.dispose();
    }
}
