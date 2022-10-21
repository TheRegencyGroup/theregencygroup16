/** @odoo-module **/

    import { patch } from "@web/core/utils/patch";
    import { ListRenderer } from "@web/views/list/list_renderer";

    patch(ListRenderer.prototype, 'web_one2many_duplicate_cr/static/src/js/list_editable_renderer.js', {

        async onCopyRecord(record) {
            var self = this;
            var res_id = record.resId;
            var res_model = record.resModel;
            var context = record.context;

            if(!res_id) {
                await record.save()
                res_id = record.resId;
            }

            if(res_id){
                var copy_data_dict =  await self.env.model.orm.call(res_model, 'copy_data', [res_id], { context: context })
                var new_copy_data_dict = {}
                _.each(copy_data_dict,function(fieldvalue,fieldname){
                    new_copy_data_dict['default_' + fieldname] = fieldvalue
                });
                var context_to_pass = Object.assign({},context,new_copy_data_dict);
                await self.add({context: context_to_pass});
            }
        },
    });
