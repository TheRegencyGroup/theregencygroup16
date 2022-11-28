/** @odoo-module **/

// The space is not considered a word joiner and the text breaks only when the user types Enter
fabric.Textbox.prototype._wordJoiners = /[]/;

export const RECTANGLE_AREA_TYPE = 'rectangle';
export const ELLIPSE_AREA_TYPE = 'ellipse';
export const TEXT_AREA_TYPE = 'text';
export const PRODUCT_IMAGE_MODEL = 'product.image';
export const OVERLAY_PRODUCT_AREA_IMAGE = 'overlay.product.area.image';
export const PRODUCT_IMAGE_FIELD = 'image_512';
export const AREAS_IMAGE_NON_ATTRIBUTE_VALUE_ID = 0;

export function computeImageSrc({ id, model, field, timestamp }) {
    let baseUrl = window.location.origin;
    let src =`${baseUrl}/web/image?model=${model}&id=${id}&field=${field}`;
    if (!timestamp) {
        timestamp = new Date().valueOf();
    }
    return `${baseUrl}/web/image?model=${model}&id=${id}&field=${field}&unique=${timestamp}`;
}

export function enableCanvasPointerEvents(canvas, state) {
    canvas.upperCanvasEl.style.pointerEvents = state ? 'all' : 'none';
}

export async function readImageDataFromFile(blob) {
    return await new Promise((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => {
            resolve(reader.result);
        };
        reader.readAsDataURL(blob);
    });
}
