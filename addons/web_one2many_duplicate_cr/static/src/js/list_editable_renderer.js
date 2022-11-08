/** @odoo-module **/

    import { patch } from "@web/core/utils/patch";
    import { ListRenderer } from "@web/views/list/list_renderer";
    import {
        serializeDate,
        serializeDateTime,
    } from "@web/core/l10n/dates";

    const { onMounted, onPatched, useRef } = owl;


    patch(ListRenderer.prototype, 'web_one2many_duplicate_cr/static/src/js/list_editable_renderer.js', {
        setup() {
            this._super();
            onMounted(this.addThTag.bind(this));
        },

        addThTag () {
                const buttonTag = document.querySelector('td.o_list_record_copy');
                if (!buttonTag) {
                    return;
                }
                const indexButtonTag = [...buttonTag.parentElement.children].indexOf(buttonTag);

                const newThTag = document.createElement("th");
                newThTag.classList.add('o_list_button');
                newThTag.style.width = '30px';

                const tableEl = buttonTag.parentElement.parentElement.parentElement;
                const allCells = tableEl.tHead.firstElementChild.children;
                (allCells[indexButtonTag - 1] || allCells[indexButtonTag]).after(newThTag);
            },

        async onCopyRecord(record) {
            let self = this;
            let res_id = record.resId;
            let res_model = record.resModel;
            let context = record.context;

            if(res_id){
                let copy_data_dict =  await self.env.model.orm.call(res_model, 'copy_data', [res_id], { context: context })
                let new_copy_data_dict = {}
                _.each(copy_data_dict,function(fieldvalue,fieldname){
                    new_copy_data_dict['default_' + fieldname] = fieldvalue
                });
                let context_to_pass = Object.assign({},context,new_copy_data_dict);
                await self.add({context: context_to_pass});
            } else {
                let new_copy_data_dict = {}
                _.each(record.fields, function (fieldprops, fieldname){
                    let value;
                    if(fieldprops.type == 'many2one')
                    {
                        value = record.data[fieldname] ? record.data[fieldname][0] : false
                    } else if (fieldprops.type == 'many2many' || fieldprops.type == 'one2many'){
                        let recs = []
                        value = []
                        _.each(record.data[fieldname].records, function(rec){
                           recs.push(rec.data.id)
                        })
                        value = [[6, 0, recs]]
                    } else if(fieldprops.type == 'datetime') {
                        value = serializeDateTime(record.data[fieldname])
                    } else if(fieldprops.type == 'date'){
                        value = serializeDate(record.data[fieldname])
                    } else {
                        value = record.data[fieldname]
                    }

                    if (value !=null){
                        new_copy_data_dict['default_' + fieldname] = value
                    }
                })
                let context_to_pass = Object.assign({},context,new_copy_data_dict);
                await self.add({context: context_to_pass});
            }
        },
    });
