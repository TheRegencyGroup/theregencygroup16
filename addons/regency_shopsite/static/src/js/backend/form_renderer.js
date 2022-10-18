/** @odoo-module **/

import FormRenderer from 'web.FormRenderer';
import { OVERLAY_AREAS_WIDGET_NAME } from './overlay_template_areas';

FormRenderer.include({
    _renderView: function () {
        return this._super(...arguments).then(() => {
            let fieldWidgets = Object.values(this.state.fieldsInfo.form).map(f => f.widget);
            if (fieldWidgets.includes(OVERLAY_AREAS_WIDGET_NAME)) {
                this.el.classList.add('form_view_with_design_areas');
            }
        });
    },
});
