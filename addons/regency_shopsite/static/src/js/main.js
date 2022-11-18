/** @odoo-module **/

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

export function computeAttachmentLink(attachmentId) {
    let baseUrl = window.location.origin;
    return `${baseUrl}/web/content/${attachmentId}`;
}

export function enableCanvasPointerEvents(canvas, state) {
    canvas.upperCanvasEl.style.pointerEvents = state ? 'all' : 'none';
}
