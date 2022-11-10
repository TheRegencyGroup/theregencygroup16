/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { OverlayAreasPositionComponent } from "./overlay_template_areas_position";
import { useBus } from "@web/core/utils/hooks";
import legacyEnv from "web.env";
import {
    PRODUCT_IMAGE_FIELD,
    PRODUCT_IMAGE_MODEL,
    AREAS_IMAGE_NON_ATTRIBUTE_VALUE_ID,
    computeImageSrc,
} from "../main";

const { Component, onMounted, onPatched, useRef, useState, useEnv } = owl;

const OVERLAY_AREAS_WIDGET_NAME = 'overlay_areas';
const PRODUCT_TEMPLATE_ID_FIELD = 'product_template_id';
const PRODUCT_TEMPLATE_IMAGE_IDS_FIELD = 'product_template_image_ids';
const OVERLAY_POSITION_IDS_FIELD = 'overlay_position_ids';
const AREAS_IMAGE_ATTRIBUTE_ID_FIELD = 'areas_image_attribute_id';
const AREAS_IMAGE_ATTRIBUTE_VALUE_LIST_FIELD = 'areas_image_attribute_value_list';

class OverlayAreasWidget extends Component {
    setup() {
        onPatched(this.onPatched);
        onMounted(this.onMounted);

        this.state = useState({});
        this.imageListPopupRef = useRef('image_list_modal');

        this.env = useEnv();
        useBus(this.env.bus, "RELATIONAL_MODEL:WILL_SAVE_URGENTLY", this.commitChanges.bind(this));
        useBus(this.env.bus, "RELATIONAL_MODEL:NEED_LOCAL_CHANGES", this.commitChanges.bind(this));
        legacyEnv.bus.on("change-field", this, this.onChangeField.bind(this));

        this.init();
    }

    init() {
        this.state.overlayPositions =  this.value || {};
        this.state.productTemplateImages = [];
        this.state.productTemplateImagesLoaded = false;
        this.state.imagesListModalData = false;

        this.lastRecordId = this.props.record.__bm_handle__;
        this.lastProductTemplateId = this.productTemplateId;
        this.lastOverlayPositionIds = [...this.overlayPositionIds];
        this.lastAreasImageAttributeId = this.areasImageAttributeId;
        this.lastAreasImageAttributeValueList = [...this.areasImageAttributeValueList];

        this.downloadProductTemplateImages();
    }

    get editMode() {
        return this.env.model.root.isDirty;
    }

    get value() {
        return this.props.value || {};
    }

    get productTemplateId() {
        const productTemplateIdField = this.props.record.data[PRODUCT_TEMPLATE_ID_FIELD];
        return productTemplateIdField && productTemplateIdField.length
            ? productTemplateIdField[0]
            : false;
    }

    get productTemplateImageIds() {
        return this.props.record.data[PRODUCT_TEMPLATE_IMAGE_IDS_FIELD].resIds;
    }

    get overlayPositionIds() {
        return this.props.record.data[OVERLAY_POSITION_IDS_FIELD].resIds.sort((a, b) => a - b);
    }

    get areasImageAttributeId() {
        const areasImageAttributeIdField = this.props.record.data[AREAS_IMAGE_ATTRIBUTE_ID_FIELD];
        return areasImageAttributeIdField && areasImageAttributeIdField.length
            ? areasImageAttributeIdField[0]
            : false;
    }

    get areasImageAttributeValueList() {
        return this.props.record.data[AREAS_IMAGE_ATTRIBUTE_VALUE_LIST_FIELD] || [{
            id: AREAS_IMAGE_NON_ATTRIBUTE_VALUE_ID,
            name: 'FOR ALL ATTRIBUTES',
        }];
    }

    get filteredProductImageList() {
        let selectedImageIds = [];
        for (let position of Object.values(this.state.overlayPositions)) {
            if (!!Object.values(position.selectedImages).length) {
                selectedImageIds = [
                    ...selectedImageIds,
                    ...Object.values(position.selectedImages).map(e => e.imageId),
                ];
            }
        }
        const positionId = this.state.imagesListModalData.overlayPositionId;
        const valueId = this.state.imagesListModalData.areasImageAttributeValueId;
        const positionSelectedImageIds = Object.values(this.state.overlayPositions[positionId].selectedImages)
            .map(e => e.imageId);
        const positionSelectedImageValueIds = Object.values(this.state.overlayPositions[positionId].selectedImages)
            .map(e => e.valueId);
        let list = this.state.productTemplateImages.filter(e => !selectedImageIds.includes(e.id));
        for (let item of list) {
            let firstSelectedImage = false;
            if (positionSelectedImageIds.length &&
                !(positionSelectedImageValueIds.length === 1 && positionSelectedImageValueIds[0] === valueId)) {
                firstSelectedImage = this.state.productTemplateImages.find(e => e.id === positionSelectedImageIds[0]).image;
            }
            item.isAvailable = firstSelectedImage
                ? item.image.width === firstSelectedImage.width && item.image.height === firstSelectedImage.height
                : true;
        }
        return list;
    }

    get overlayAreasPositions() {
        return Object.values(this.__owl__.children)
            .filter(e => e.component.constructor.name === 'OverlayAreasPositionComponent')
            .map(e => e.component);
    }

    onMounted() {

    }

    onPatched() {
        if (this.lastRecordId !== this.props.record.__bm_handle__) {
            this.init();
        }
    }

    onChangeField(data) {
        const changedFields = Object.keys(data.changes || data);
        if (changedFields.includes(PRODUCT_TEMPLATE_ID_FIELD)) {
            this.changeProductTemplateId();
        } else if (changedFields.includes(OVERLAY_POSITION_IDS_FIELD)) {
            this.changeOverlayPositionIds();
        } else if (changedFields.filter(e =>
            [AREAS_IMAGE_ATTRIBUTE_ID_FIELD, AREAS_IMAGE_ATTRIBUTE_VALUE_LIST_FIELD].includes(e))) {
            this.changeAreasImageAttributeValueList();
        }
    }

    changeProductTemplateId() {
        if (this.lastProductTemplateId !== this.productTemplateId) {
            this.lastProductTemplateId = this.productTemplateId;
            Object.values(this.state.overlayPositions).forEach(e => {
                e.areaList = {};
                e.selectedImages = {};
            });
            this.downloadProductTemplateImages();
        }
    }

    changeOverlayPositionIds() {
        if (JSON.stringify(this.lastOverlayPositionIds) !== JSON.stringify(this.overlayPositionIds)) {
            this.lastOverlayPositionIds = [...this.overlayPositionIds];

            let positionRecords = this.props.record.data[OVERLAY_POSITION_IDS_FIELD].records;
            let existingPositionIds = [];
            for (let position of Object.values(this.state.overlayPositions)) {
                if (!this.overlayPositionIds.includes(position.id)) {
                    delete this.state.overlayPositions[position.id];
                } else {
                    existingPositionIds.push(position.id);
                }
            }
            let newOverlayPositionIds = this.overlayPositionIds.filter(e => !existingPositionIds.includes(e));
            for (let positionId of newOverlayPositionIds) {
                let record = positionRecords.find(e => e.resId === positionId);
                this.state.overlayPositions[positionId] = {
                    id: positionId,
                    name: record.data.display_name,
                    areaList: {},
                    selectedImages: {},
                }
            }
        }
    }

    changeAreasImageAttributeValueList() {
        const lastValueIds = this.lastAreasImageAttributeValueList.map(e => e.id).sort((a, b) => a - b);
        const currentValueIds = this.areasImageAttributeValueList.map(e => e.id).sort((a, b) => a - b);
        if (this.lastAreasImageAttributeId !== this.areasImageAttributeId ||
           JSON.stringify(lastValueIds) !== JSON.stringify(currentValueIds)) {
            this.lastAreasImageAttributeId = this.areasImageAttributeId;
            this.lastAreasImageAttributeValueList = [...this.areasImageAttributeValueList];

            for (let position of Object.values(this.state.overlayPositions)) {
                let valueIds = this.areasImageAttributeValueList.map(e => e.id);
                for (let selectedImage of Object.values(position.selectedImages)) {
                    if (valueIds.length) {
                        let newValueId = valueIds.shift();
                        position.selectedImages[newValueId] = {
                            imageId: selectedImage.imageId,
                            valueId: newValueId,
                        };
                    }
                    delete position.selectedImages[selectedImage.valueId];
                }
            }
        }
    }

    downloadProductTemplateImages() {
        let promises = [];
        for (let imageId of this.productTemplateImageIds) {
            promises.push(new Promise(async resolve => {
                const imageUrl = computeImageSrc({
                    id: imageId,
                    model: PRODUCT_IMAGE_MODEL,
                    field: PRODUCT_IMAGE_FIELD,
                });
                const image = new Image();
                const res = await fetch(imageUrl);
                const blob = await res.blob();
                image.src = await new Promise(resolve => {
                    const reader = new FileReader();
                    reader.onloadend = () => resolve(reader.result);
                    reader.readAsDataURL(blob);
                });
                image.onload = () => {
                    resolve({
                        id: imageId,
                        image,
                    });
                };
            }));
        }
        Promise.all(promises).then((data) => {
            this.state.productTemplateImages = data;
            this.state.productTemplateImagesLoaded = true;
        });
    }

    openImageListModal({ overlayPositionId, areasImageAttributeValueId, }) {
        this.state.imagesListModalData = { overlayPositionId, areasImageAttributeValueId };
    }

    closeImageListModal() {
        this.state.imagesListModalData = false;
    }

    onClickImage(imageId) {
        if (imageId !== false && !this.state.productTemplateImages.find(e => e.id === imageId)?.isAvailable) {
            return;
        }
        let overlayPositionId = this.state.imagesListModalData.overlayPositionId;
        let valueId = this.state.imagesListModalData.areasImageAttributeValueId;
        if (overlayPositionId === undefined || !valueId === undefined) {
            return;
        }
        const selectedImages = this.state.overlayPositions[overlayPositionId].selectedImages;
        if (imageId) {
            selectedImages[valueId] = { valueId, imageId };
        } else {
            delete selectedImages[valueId];
        }
        this.closeImageListModal();
    }

    onClickCloseImageListModal(event) {
        this.closeImageListModal();
    }

    onClickToEditMode(event) {
        this.env.model.__bm__.setDirtyForce(this.props.record.__bm_handle__);
        this.env.model.root.update();
    }

    async commitChanges() {
        if (!this.editMode) {
            return;
        }
        for (let position of this.overlayAreasPositions) {
            if (!!position.state.editorImage && !position.firstEditorImageLoad) {
                this.props.update({
                    errors: ['Wait for images to load!']
                });
                return;
            }
        }
        let value = {}
        for (let position of this.overlayAreasPositions) {
            let areaList = {};
            if (position.overlay) {
                for (let area of Object.values(position.overlay.areaList)) {
                    let objectBoundingRect = area.object.getBoundingRect();
                    areaList[area.index] = {
                        index: area.index,
                        data: {
                            ...area.data,
                            boundRect: {
                                width: Math.ceil(objectBoundingRect.width),
                                height: Math.ceil(objectBoundingRect.height),
                                x: Math.ceil(objectBoundingRect.left),
                                y: Math.ceil(objectBoundingRect.top),
                            },
                        },
                        areaType: area.areaType,
                    }
                }
            }
            value[position.props.overlayPositionId] = {
                id: position.props.overlayPositionId,
                name: position.props.overlayPositionName,
                areaList,
                selectedImages: position.props.selectedImages,
                canvasSize: {
                    width: position.state.editorImage.width,
                    height: position.state.editorImage.height,
                },
            };
        }
        let errors = [];
        const positionSelectedImages = Object.values(value).map(e => !!Object.keys(e.selectedImages).length);
        if (positionSelectedImages.some(e => !e)) {
            errors.push('All positions must have at least one selected image!');
        }
        const positionAreas = Object.values(value).map(e => !!Object.keys(e.areaList).length);
        if (positionAreas.every(e => !e)) {
            errors.push('At least one position must have areas!');
        }
        if (errors.length) {
            this.props.update({ errors });
            return;
        }
        this.props.update(value);
    }
}

OverlayAreasWidget.props = {
    ...standardFieldProps,
};

OverlayAreasWidget.supportedTypes = ["json"];
OverlayAreasWidget.template = "overlay_areas";
OverlayAreasWidget.components = {
    OverlayAreasPositionComponent,
};

registry.category("fields").add(OVERLAY_AREAS_WIDGET_NAME, OverlayAreasWidget);

export {
    OverlayAreasWidget,
    OVERLAY_AREAS_WIDGET_NAME,
}
