/** @odoo-module **/

import { X2ManyField } from '@web/views/fields/x2many/x2many_field';
import { FormArchParser } from "@web/views/form/form_arch_parser";
import { useEnv } from "@odoo/owl";
import { session } from "@web/session";
import { formatFloat } from "@web/views/fields/formatters";
import { patch } from '@web/core/utils/patch';
import { useService } from "@web/core/utils/hooks";
import { makeContext } from "@web/core/context";
import { loadSubViews } from "@web/views/form/form_controller";
import { getDataURLFromFile } from "@web/core/utils/urls";

const DEFAULT_MAX_FILE_SIZE = 128 * 1024 * 1024;

patch(X2ManyField.prototype, 'product_multiple_images_upload', {
    setup() {
        this._super(...arguments);

        if (this.isProductMultipleImagesUpload) {
            this.pmiNotificationService = useService('notification');
            this.pmiUiService = useService('ui');
            this.pmiuViewService = useService('view');
            this.pmiuUserService = useService('user');
            this.pmiuEnv = useEnv();
        }
    },

    get isProductMultipleImagesUpload() {
        return this.viewMode === 'kanban' && this.activeField.options?.multiple_images_upload;
    },

    get maxUploadSize() {
        return session.max_file_upload_size || DEFAULT_MAX_FILE_SIZE;
    },

    async onAddMultipleImages(event) {
        const input = event.target;
        const files = [...input.files];
        input.value = null;
        if (!files) {
            return;
        }
        let promises = [];
        let errors = [];
        this.pmiUiService.block();
        files.forEach(file => {
            if (file.size > this.maxUploadSize) {
                const maxFileSizeStr = formatFloat(this.maxUploadSize, { humanReadable: true });
                errors.push(`${file.name} file exceed the maximum file size of ${maxFileSizeStr}.`);
                return;
            }
            promises.push(new Promise(async (resolve) => {
                try {
                    const fileData = await getDataURLFromFile(file);
                    let fileName = file.name;
                    if (fileName.includes('.')) {
                        fileName = fileName.split('.')[0];
                    }
                    await this.addImage(fileName, fileData.split(',')[1])
                } catch (e) {
                    errors.push(`Error when read ${file.name} file.`);
                }
                resolve();
            }));
        });
        await Promise.all(promises);
        this.pmiUiService.unblock();
        if (errors.length) {
            this.pmiNotificationService.add(
                errors.join('\n'),
                {
                    title: 'Images upload',
                    type: 'danger',
                },
            );
        }
    },

    async addImage(name, imageData) {
        const form = await this.getFormViewInfo({
            list: this.list,
            activeField: this.activeField,
            viewService: this.pmiuViewService,
            userService: this.pmiuUserService,
            env: this.pmiuEnv,
        });

        const recordParams = {
            context: makeContext([this.list.context, {
                default_name: name,
                default_image_1920: imageData,
            }]),
            resModel: this.list.resModel,
            activeFields: form.activeFields,
            fields: { ...form.fields },
            views: { form },
            mode: 'edit',
            viewType: 'form',
        };

        const record = await this.list.model.addNewRecord(this.list, recordParams);

        this.list.add(record);
    },

    async getFormViewInfo({ list, activeField, viewService, userService, env }) {
        // function copied from /web/static/src/views/fields/relational_utils.js
        let formViewInfo = activeField.views.form;
        const comodel = list.resModel;
        if (!formViewInfo) {
            const { fields, relatedModels, views } = await viewService.loadViews({
                context: list.context,
                resModel: comodel,
                views: [[false, "form"]],
            });
            const archInfo = new FormArchParser().parse(views.form.arch, relatedModels, comodel);
            formViewInfo = { ...archInfo, fields }; // should be good to memorize this on activeField
        }

        await loadSubViews(
            formViewInfo.activeFields,
            formViewInfo.fields,
            {}, // context
            comodel,
            viewService,
            userService,
            env.isSmall
        );

        return formViewInfo;
    }
});
