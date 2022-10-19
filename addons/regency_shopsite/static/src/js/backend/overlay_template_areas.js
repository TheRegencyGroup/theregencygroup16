/** @odoo-module **/

import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {OverlayAreasPositionComponent} from "./overlay_template_areas_position";
import {useBus} from "@web/core/utils/hooks";
import legacyEnv from "web.env";

const {Component, onMounted, onPatched, useRef, useState, useEnv} = owl;

const OVERLAY_AREAS_WIDGET_NAME = 'overlay_areas';
const OVERLAY_AREAS_FIELD = 'areas_json';
const PRODUCT_TEMPLATE_ID_FIELD = 'product_template_id';
const OVERLAY_POSITION_IDS_FIELD = 'overlay_position_ids';
const OVERLAY_ATTRIBUTE_LINE_IDS_FIELD = 'overlay_attribute_line_ids';
const ATTRIBUTE_VALUE_IDS = 'value_ids';
const COLOR_ATTRIBUTE_NAME = 'Color';

class OverlayAreasWidget extends Component {
    setup() {
        onPatched(this.onPatched);
        onMounted(this.onMounted);

        this.state = useState({});
        this.imageListPopupRef = useRef('image_list_popup');

        this.env = useEnv();
        useBus(this.env.bus, "RELATIONAL_MODEL:WILL_SAVE_URGENTLY", this.commitChanges.bind(this));
        useBus(this.env.bus, "RELATIONAL_MODEL:NEED_LOCAL_CHANGES", this.commitChanges.bind(this));
        legacyEnv.bus.on("change-field", this, this.onChangeField.bind(this));

        this.init();
    }

    onMounted() {
        let popup = this.imageListPopupRef.el;
        this.imageListPopupRef.el.remove();
        document.body.appendChild(popup);
    }

    onPatched() {
        if (this.currentRecordId !== this.props.record.__bm_handle__) {
            this.init();
        }
    }

    init() {
        this.valueObj = JSON.parse(this.props.record.data[OVERLAY_AREAS_FIELD]);

        this.state.productTemplateId = this.valueObj.productTemplateId;
        this.state.productImageList = this.valueObj.productImageList || [];
        this.state.overlayPositions = this.valueObj.overlayPositions || {};
        this.state.showImageListForOverlayPosId = false;

        this.productImageUnique = new Date().valueOf();

        this.currentRecordId = this.props.record.__bm_handle__;
        this.currentProductTemplateId = this.getProductTemplateId();
        this.currentOverlayPositionIds = this.getOverlayPositionIds();
        this.currentOverlayColorAttributeValueIds = this.getOverlayAttributeColorValueIds();
    }

    onChangeField(data) {
        const changedFields = Object.keys(data.changes || data);
        if (changedFields.includes(PRODUCT_TEMPLATE_ID_FIELD)) {
            this.checkChangeProductTemplateId();
        }
        if (changedFields.includes(OVERLAY_POSITION_IDS_FIELD)) {
            this.checkChangeOverlayPositionIds();
        }
        if (changedFields.includes(OVERLAY_ATTRIBUTE_LINE_IDS_FIELD)) {
            this.checkChangeOverlayAttributeColorValueIds();
        }
    }

    getProductTemplateId() {
        const productTemplateIdField = this.props.record.data[PRODUCT_TEMPLATE_ID_FIELD];
        return productTemplateIdField && productTemplateIdField.length
            ? productTemplateIdField[0]
            : null;
    }

    getOverlayPositionIds() {
        const overlayPositionIdsField = this.props.record.data[OVERLAY_POSITION_IDS_FIELD];
        return overlayPositionIdsField && overlayPositionIdsField.records.length
            ? overlayPositionIdsField.records.map(e => e.data.id)
            : [];
    }

    getOverlayAttributeColorValueIds() {
        const overlayAttributeLineIdsField = this.props.record.data[OVERLAY_ATTRIBUTE_LINE_IDS_FIELD];
        if (!overlayAttributeLineIdsField) {
            return [];
        }
        const overlayColorAttributeLineIdField = overlayAttributeLineIdsField.records
            .find(e => {
                const attributeIdField = e.data.attribute_id;
                if (!attributeIdField.length) {
                    return false;
                }
                return attributeIdField[1] === COLOR_ATTRIBUTE_NAME;
            });
        if (!overlayColorAttributeLineIdField) {
            return [];
        }
        const overlayColorAttributeValueIdsField = overlayColorAttributeLineIdField[ATTRIBUTE_VALUE_IDS];
        return overlayColorAttributeValueIdsField && overlayColorAttributeValueIdsField.records.length
            ? overlayColorAttributeValueIdsField.records.map(e => e.data.id)
            : [];
    }

    checkChangeProductTemplateId() {
        const productTemplateId = this.getProductTemplateId();
        if (this.currentProductTemplateId !== productTemplateId) {
            this.currentProductTemplateId = productTemplateId;

            this.valueObj = JSON.parse(this.props.record.data[OVERLAY_AREAS_FIELD]);
            this.state.productTemplateId = this.valueObj.productTemplateId;
            this.state.productImageList = this.valueObj.productImageList;
            this.productImageUnique = new Date().valueOf();
            for (let overlayPosition of Object.values(this.state.overlayPositions)) {
                overlayPosition.areaList = {};
                for (let colorImage of Object.values(overlayPosition.colorImages)) {
                    colorImage.imageId = false;
                    colorImage.imageModel = false;
                }
            }
        }
    }

    checkChangeOverlayPositionIds() {
        const overlayPositionIds = this.getOverlayPositionIds();
        if (JSON.stringify(this.currentOverlayPositionIds) !== JSON.stringify(overlayPositionIds)) {
            this.currentOverlayPositionIds = overlayPositionIds;

            this.valueObj = JSON.parse(this.props.record.data[OVERLAY_AREAS_FIELD]);
            for (let overlayPosition of Object.values(this.valueObj.overlayPositions)) {
                if (!this.state.overlayPositions[overlayPosition.id]) {
                    this.state.overlayPositions[overlayPosition.id] = overlayPosition;
                }
            }
            let removedOverlayPositionIds = Object.keys(this.state.overlayPositions)
                .filter(e => !Object.keys(this.valueObj.overlayPositions).includes(e));
            for (let overlayPositionId of removedOverlayPositionIds) {
                delete this.state.overlayPositions[overlayPositionId];
            }
        }
    }

    checkChangeOverlayAttributeColorValueIds() {
        const overlayColorAttributeValueIds = this.getOverlayAttributeColorValueIds();
        if (JSON.stringify(this.currentOverlayColorAttributeValueIds) !== JSON.stringify(overlayColorAttributeValueIds)) {
            this.currentOverlayColorAttributeValueIds = overlayColorAttributeValueIds;

            this.valueObj = JSON.parse(this.props.record.data[OVERLAY_AREAS_FIELD]);
            for (let overlayPosition of Object.values(this.valueObj.overlayPositions)) {
                for (let colorImage of Object.values(overlayPosition.colorImages)) {
                    if (!this.state.overlayPositions[overlayPosition.id].colorImages[colorImage.id]) {
                        this.state.overlayPositions[overlayPosition.id].colorImages[colorImage.id] = colorImage;
                    }
                }
                let removedColorIds = Object.keys(this.state.overlayPositions[overlayPosition.id].colorImages)
                    .filter(e => !Object.keys(overlayPosition.colorImages).includes(e));
                for (let colorId of removedColorIds) {
                    delete this.state.overlayPositions[overlayPosition.id].colorImages[colorId];
                }
            }
        }
    }

    get editMode() {
        // return this.props.record.mode === 'edit';
        return this.env.model.root.isDirty;
    }

    get filteredProductImageList() {
        let selectedImages = Object.values(this.state.overlayPositions)
            .map(e => Object.values(e.colorImages))
            .flat()
            .filter(e => !!e.imageId && !!e.imageModel);
        if (!selectedImages) {
            return this.state.productImageList;
        }
        return this.state.productImageList.filter(e => {
            for (let image of selectedImages) {
                if (e.id === image.imageId && e.model === image.imageModel) {
                    return false;
                }
            }
            return true;
        })
    }

    getProductImageSrc(id, model) {
        let baseUrl = window.location.origin;
        return `${baseUrl}/web/image?model=${model}&id=${id}&field=image_512&unique=${this.productImageUnique}`;
    }

    changeOverlayAreasImage({id, colorId,}) {
        this.state.showImageListForOverlayPosId = {id, colorId};
    }

    async commitChanges() {
        if (!this.editMode) {
            return;
        }
        let val = {
            productTemplateId: this.state.productTemplateId || false,
            productImageList: this.state.productImageList,
            overlayPositions: {},
        }
        let OverlayAreasPositionComponents = Object.values(this.__owl__.children)
            .filter(e => e.component.constructor.name === 'OverlayAreasPositionComponent')
            .map(e => e.component);
        for (let component of OverlayAreasPositionComponents) {
            let overlayPositionId = component.props.overlayPositionId;
            // if (!component.state.imageLoad) {
            //     val.overlayPositions[overlayPositionId] = this.valueObj.overlayPositions[overlayPositionId];
            //     continue;
            // }
            let areaList = {};
            if (component.overlay) {
                for (let area of Object.values(component.overlay.areaList)) {
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
            let name = component.props.overlayPositionName;
            let imageId = component.props.imageId;
            let imageModel = component.props.imageModel;
            let canvasSize = false;
            // if (component.overlay?.canvas) {
            //     canvasSize = {
            //         width: component.overlay.canvas.width,
            //         height: component.overlay.canvas.height,
            //     };
            // }
            canvasSize = {
                width: 500,
                height: 500,
            };
            let colorImages = component.props.colorImages;
            val.overlayPositions[overlayPositionId] = {
                id: overlayPositionId,
                name,
                imageId,
                imageModel,
                areaList,
                canvasSize,
                colorImages,
            };
        }
        this.props.update(JSON.stringify(val));
    }

    closeImageListPopup() {
        this.state.showImageListForOverlayPosId = false;
    }

    onClickImage(id, model, event) {
        let overlayPositionId = this.state.showImageListForOverlayPosId.id;
        let colorId = this.state.showImageListForOverlayPosId.colorId;
        if (!overlayPositionId || !colorId) {
            return;
        }
        this.state.overlayPositions[overlayPositionId].colorImages[colorId].imageId = id;
        this.state.overlayPositions[overlayPositionId].colorImages[colorId].imageModel = model;
        this.state.overlayPositions[overlayPositionId].areaList = {};
        this.closeImageListPopup();
    }

    onClickCloseImageListPopup(event) {
        this.closeImageListPopup();
    }

    onClickToEditMode(event) {
        this.env.model.__bm__.setDirtyForce(this.props.record.__bm_handle__);
        this.env.model.root.update();
    }
}

OverlayAreasWidget.props = {
    ...standardFieldProps,
};

OverlayAreasWidget.supportedTypes = ["char"];
OverlayAreasWidget.template = "overlay_areas";
OverlayAreasWidget.components = {
    OverlayAreasPositionComponent,
};

registry.category("fields").add(OVERLAY_AREAS_WIDGET_NAME, OverlayAreasWidget);

export {
    OverlayAreasWidget,
    OVERLAY_AREAS_WIDGET_NAME,
}
