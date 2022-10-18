odoo.define("product_multiple_images", function(require) {
    "use strict";

    var core = require("web.core");
    var AbstractField = require("web.AbstractField");
    var rel_fields = require("web.relational_fields");
    var rpc = require("web.rpc");
    var _t = core._t;

    var MultiImages = AbstractField.extend({
        template: "FieldBinaryFileUploader",
        init: function() {
            this._super.apply(this, arguments);
            this.loadedFiles = {};
            this.loadingFiles = [];
        },
        _onLoaded: function(ev, files, res) {
            var self = this;
            this.loadingFiles = [];

            var uploaded_ids = this.value.res_ids;
            $("body").removeClass("loading");
            _.each(files, function(file) {
                if (file.error) {
                    self.do_warn(_t("Uploading Issue"), file.error);
                } else {
                    uploaded_ids.push(file.id);
                    self.loadedFiles[file.id] = true;
                }
            });
            this.viewType = res.record.viewType;
            this._setValue({
                operation: "REPLACE_WITH",
                ids: uploaded_ids,
            });
        },
    });

    rel_fields.FieldOne2Many.include({
        _renderButtons: function() {
            var self = this;
            this._super();
            var multiple_files = false;
            if (this.$buttons) {
                multiple_files = this.$buttons.find(".o_multi_files");
            }
            if (!this.isReadonly && multiple_files && multiple_files.length && this.view.arch.tag === "kanban" && this.view.arch.attrs.multi_images) {
                this.upload_at_field = {};
                this.upload_at_field.name = this.name;
                this.upload_at_field.model = this.field.relation;
                if (this.model == 'product.template'){
                    this.upload_at_field.field = this.field.relation_field;
                    this.upload_at_field.res_id = this.record.res_id;
                } else if(this.model == 'product.product') {
                    this.upload_at_field.field = 'product_tmpl_id';
                    this.upload_at_field.res_id = this.record.data['product_tmpl_id'].res_id;
                } else {
                    return false
                }  
                var multiimgs = new MultiImages(this.getParent(), this.upload_at_field.name, this.record, {mode: "edit"});

                multiple_files.parent().attr("style", "display: inline-block;");
                this.$buttons.find(".multiple-upload").attr("style", "background-color: lightgray; margin-bottom:0;");
                multiple_files.on("change", function(ev) {
                    self.added_files(ev).then(function(res) {
                        multiimgs._onLoaded(ev, self.updated_files, self);
                    });
                });
                
                var rem_all = this.$buttons.find(".rall");
                rem_all.attr("style", "display: inline-block; background-color: lightgray;");
                rem_all.on("click", function(ev) {
                    if ($('.o_kanban_view .card').length > 0) {
                        if(confirm("Are you sure you want to remove all extra images?")){
                            var arg = [];
                            arg.push(self.upload_at_field.res_id);
                            self._rpc({
                                model: self.upload_at_field.model,
                                method: "removeimages",
                                args: arg,
                            }).then(function(res) {
                                window.location.reload();
                            });
                        }
                        else{
                            return false;
                        }
                    }
                });
            }
        },

        added_files: function(event) {
            var self = this;
            $("body").append('<div class="overlay"></div>');
            this.updated_files = [];

            var loop_files = function(files) {
                var file = files.shift();
                var complete = $.Deferred();
                if (typeof(file) != "object") {
                    return complete.resolve();
                }

                var uploaded = $.Deferred();
                var freader = new FileReader();
                $("body").addClass("loading");
                freader.onloadend = function(doc) {
                    var info = doc.target.result;
                    file.image = info.split(",")[1];
                    file.res_id = self.upload_at_field.res_id;
                    uploaded.resolve();
                };
                freader.readAsDataURL(file);
                uploaded.then(function() {
                    var arg = {
                        name: file.name,
                        image_1920: file.image,
                    };
                    arg[self.upload_at_field.field] = self.upload_at_field.res_id;
                    rpc.query({
                        model: self.upload_at_field.model,
                        method: "create",
                        args: [arg],
                    }).then(function(result) {
                        self.updated_files.push(_.extend(file, {id: result}));
                        if (files.length) {
                            loop_files(files).then(function() {
                                complete.resolve();
                            });
                        } else {
                            complete.resolve();
                        }
                    });
                });
                return complete;
            };
            var files = event.currentTarget.files;
            return loop_files(_.values(files));
        },
    });
});
