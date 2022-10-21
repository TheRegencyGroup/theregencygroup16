/** @odoo-module **/

import { FormCompiler } from '@web/views/form/form_compiler';
import { OVERLAY_AREAS_WIDGET_NAME } from './overlay_template_areas';
import { patch } from 'web.utils';

patch(FormCompiler.prototype, 'regency_shopsite/static/src/js/backend/form_compiler', {
    compileSheet(el, params) {
        let sheetBG = this._super(...arguments);
        if (el.innerHTML.includes(OVERLAY_AREAS_WIDGET_NAME)) {
            let formContainer = sheetBG.closest('.o_form_view_container');
            if (formContainer) {
                formContainer.classList.add('form_view_for_overlay_template');
            }
        }
        return sheetBG;
    },
});
