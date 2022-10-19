odoo.define('web_one2many_duplicate_cr.EditableListRenderer', function (require) {
"use strict";

    var ListRenderer = require('web.ListRenderer');
    var core = require('web.core');
    var utils = require('web.utils');
    var _t = core._t;


    ListRenderer.include({
        events: _.extend({}, ListRenderer.prototype.events, {
            'click tr .o_list_record_copy' : '_onCopyRecord',
        }),

        _renderFooter: function () {
            const $footer = this._super.apply(this, arguments);
            var is_one2many = this.__parentedParent.formatType == 'one2many' || this.__parentedParent.formatType == 'many2many' ? true : false;
            var is_copy_enabled = this.__parentedParent.attrs && this.__parentedParent.attrs.options && this.__parentedParent.attrs.options.copy == false ? false : true;
            if(this.addCreateLine && is_one2many == true && is_copy_enabled == true){
                $footer.find('tr').append($('<td>'));
            }
            return $footer;
        },

        _renderHeader: function () {
            var $thead = this._super.apply(this, arguments);
            var is_one2many = this.__parentedParent.formatType == 'one2many' || this.__parentedParent.formatType == 'many2many' ? true : false;
            var is_copy_enabled = this.__parentedParent.attrs && this.__parentedParent.attrs.options && this.__parentedParent.attrs.options.copy == false ? false : true;
            if (this.addCreateLine && is_one2many == true && is_copy_enabled == true) {
                $thead.find('tr').append($('<th>', {class: 'o_list_record_copy_header'}));
            }
            return $thead;
        },

        _renderRow: function (record, index) {
            var $row = this._super.apply(this, arguments);
            var is_one2many = this.__parentedParent.formatType == 'one2many' || this.__parentedParent.formatType == 'many2many' ? true : false;
            var is_copy_enabled = this.__parentedParent.attrs && this.__parentedParent.attrs.options && this.__parentedParent.attrs.options.copy == false ? false : true;
            if (this.addCreateLine && is_one2many == true && is_copy_enabled == true) {
                var $icon = $('<button>', {'class': 'fa fa-copy', 'name': 'copy', 'title':'Copy row','aria-label': _t('Copy row ') + (index + 1)});
                var $td = $('<td>', {class: 'o_list_record_copy'}).append($icon);
                $row.append($td);
            }
            return $row;
        },

        _onCopyRecord: async function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var self = this;
            var row_id = $(ev.currentTarget).parent().data('id');
            var res_id = false
            var record_to_copy = false
            _.each(this.state.data,function(record){
                if(record.id == row_id){
                    res_id = record.res_id
                    record_to_copy = record
                }
            });

            if(res_id){
                this._rpc({
                model: self.state.model,
                method: 'copy_data',
                args: [res_id],
                context: self.state.context,
                }).then(function(copy_data_dict){
                    var new_copy_data_dict = {}
                    _.each(copy_data_dict,function(fieldvalue,fieldname){
                        new_copy_data_dict['default_' + fieldname] = fieldvalue
                    })
                    var context_to_pass = Object.assign({},self.state.context,new_copy_data_dict)
                    self.trigger_up('add_record', {context: context_to_pass && [context_to_pass]})
                });
            }
            else{
                var copy_data_dict = record_to_copy.evalContext
                var new_copy_data_dict = {}
                _.each(copy_data_dict,function(fieldvalue,fieldname){
                    if(fieldname.includes('default_')){
                        new_copy_data_dict[fieldname] = fieldvalue
                    }
                });
                var context_to_pass = Object.assign({},self.state.context,new_copy_data_dict)
                self.trigger_up('add_record', {context: context_to_pass && [context_to_pass]})
            }
        },
    });

});