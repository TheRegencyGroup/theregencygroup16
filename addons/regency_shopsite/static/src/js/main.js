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
export const MIN_IMAGE_WIDTH = 500;
export const FULL_IMAGE_WIDTH = 1200;

export function computeImageSrc({ id, model, field, timestamp }) {
    let baseUrl = window.location.origin;
    if (!timestamp) {
        timestamp = new Date().valueOf();
    }
    return `${baseUrl}/web/content/${model}/${id}/${field}?unique=${timestamp}`;
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

export function computeEditorScale({ width, height, scaleWidth, transformOrigin=false }) {
    let scale = 1;
    let deltaX = 0;
    let deltaY = 0;
    let marginBottom = 0;
    if (width > scaleWidth) {
        scale = scaleWidth / width;
        deltaX = -((width - scaleWidth) / 2);
        deltaY = -((height * (1 - scale)) / 2);
        marginBottom = deltaY * 2;
    }
    const editorStyle = `
        scale: ${scale};
        margin-bottom: ${marginBottom}px;
        transform-origin: ${transformOrigin || 'left top'};
    `;
    return { scale, editorStyle };
}

export function convertCanvasPixelsToLineSpacing({ lineSpacingPixels, fontSize }) {
    return (lineSpacingPixels + fontSize) / fontSize / fabric.Text.prototype._fontSizeMult;
}

export function convertCanvasPixelsToCharSpacing({ charSpacingPixels, fontSize }) {
    return (charSpacingPixels * 1000) / fontSize;
}
