/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import {
    serializeDate,
    serializeDateTime,
} from "@web/core/l10n/dates";

const { onMounted } = owl;


patch(ListRenderer.prototype, 'web_one2many_duplicate_cr/static/src/js/list_editable_renderer.js', {
    setup() {
        this._super();
        onMounted(this.onMountedCopyRecord.bind(this));
    },

    onMountedCopyRecord() {
        if (this.isX2Many && this.activeActions.create) {
            const theadRow = document.querySelector(`div[name="${this.props.list.__fieldName__}"] table thead tr`);
            if (theadRow) {
                const thCopyRecord = document.createElement('th');
                thCopyRecord.classList.add('o_list_record_copy_th');
                theadRow.appendChild(thCopyRecord);
            }
        }
    },

    async onCopyRecord(record) {
        let self = this;
        let res_id = record.resId;
        let res_model = record.resModel;
        let context = record.context;

        if (res_id) {
            let copy_data_dict = await self.env.model.orm.call(res_model, 'copy_data', [res_id], { context: context })
            let new_copy_data_dict = {}
            _.each(copy_data_dict, function (fieldvalue, fieldname) {
                new_copy_data_dict['default_' + fieldname] = fieldvalue
            });
            let context_to_pass = Object.assign({}, context, new_copy_data_dict);
            await self.add({ context: context_to_pass });
        } else {
            let new_copy_data_dict = {}
            _.each(record.fields, function (fieldprops, fieldname) {
                let value;
                if (fieldprops.type == 'many2one') {
                    value = record.data[fieldname] ? record.data[fieldname][0] : false
                } else if (fieldprops.type == 'many2many' || fieldprops.type == 'one2many') {
                    let recs = []
                    value = []
                    _.each(record.data[fieldname].records, function (rec) {
                        recs.push(rec.data.id)
                    })
                    value = [[6, 0, recs]]
                } else if (fieldprops.type == 'datetime') {
                    value = serializeDateTime(record.data[fieldname])
                } else if (fieldprops.type == 'date') {
                    value = serializeDate(record.data[fieldname])
                } else {
                    value = record.data[fieldname]
                }

                if (value != null) {
                    new_copy_data_dict['default_' + fieldname] = value
                }
            })
            let context_to_pass = Object.assign({}, context, new_copy_data_dict);
            await self.add({ context: context_to_pass });
        }
    },
});
