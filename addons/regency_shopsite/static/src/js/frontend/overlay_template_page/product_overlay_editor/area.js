/** @odoo-module **/

export class Area {

    constructor(data, parent, areaIndex, areaObjectData) {
        this.data = data;
        this.parent = parent;
        this.areaIndex = areaIndex;
        this.areaObjectData = areaObjectData;

        this.imageObjectList = {};
        this.imageObjectIndex = 1;

        this.createCanvas();
        this.createMask();
        this.init();
        this.initAreaObjects()
    }

    init() {}

    initAreaObjects() {
        if (this.areaObjectData && this.areaObjectData.length) {
            this.imageObjectIndex = Math.max(...this.areaObjectData.map(e => e.index));
            let promises = []
            for (let imageObj of this.areaObjectData) {
                promises.push(new Promise(resolve => {
                    const image = new Image();
                    image.onload = () => {
                        resolve({
                            image,
                            index: imageObj.index,
                            data: imageObj.objectData,
                        })
                    };
                    image.src = imageObj.imageUrl;
                }));
            }
            Promise.all(promises).then((res) => {
                for (let obj of res) {
                    this.addImageObject(obj);
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

    addImageObject({ image, imgIndex, data }) {
        const object = new fabric.Image(image, {});
        let objIndex = imgIndex;
        if (!objIndex) {
            objIndex = this.imageObjectIndex;
            this.imageObjectIndex += 1;
        }
        object.objIndex = objIndex;
        if (!data) {
            if (image.width >= image.height) {
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

        let imageSplit = image.src.split(',');
        this.imageObjectList[objIndex] = {
            index: objIndex,
            image: imageSplit[1],
            imageFormat: imageSplit[0].split('/')[1].split(';')[0],
            object,
        };
        this.canvas.add(object);
        this.clipMask();
    }

    removeActiveObject() {
        let activeObj = this.canvas.getActiveObject();
        delete this.imageObjectList[activeObj.objIndex];
        this.canvas.remove(activeObj);
    }

    removeAllObjects() {
        this.canvas.clear();
        this.createMask();
        this.selectedArea();
        this.imageObjectList = {};
        this.imageObjectIndex = 1;
    }

    getOverlayImagesData() {
        this.canvas.discardActiveObject().renderAll();
        this.unselectedArea();

        let res = [];
        for (let imageObj of Object.values(this.imageObjectList)) {
            res.push({
                index: imageObj.index,
                image: imageObj.image,
                imageFormat: imageObj.imageFormat,
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

        // return new Promise((resolve) => {
        //     this.canvasEl.toBlob((blob) => {
        //         this.createMask();
        //         this.clipMask();
        //         this.selectedArea();
        //         this.reInit();
        //         let reader = new FileReader();
        //         reader.onloadend = () => {
        //             let base64data = reader.result;
        //             resolve({
        //                 data: base64data.split(',')[1],
        //                 size: {
        //                     x: this.data.boundRect.x,
        //                     y: this.data.boundRect.y,
        //                 },
        //             });
        //         }
        //         reader.readAsDataURL(blob);
        //     });
        // });
    }

    reInit() {
    }

    // checkAreas() {
    //     let objects = this.canvas.getObjects();
    //     objects = objects.filter(e => !e.isAreaMask);
    //     objects = objects.filter(e => !e.isTextArea || (!!e.isTextArea && !!e.text));
    //     return !!objects.length;
    // }

    destroy() {
        this.canvas.dispose();
    }
}
