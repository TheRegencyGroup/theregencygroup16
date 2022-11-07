/** @odoo-module **/

import { MailFormCompiler } from '@mail/views/form/form_compiler';
import { FormCompiler } from '@web/views/form/form_compiler';
import { patch } from "@web/core/utils/patch";
import { setAttributes } from '@web/core/utils/xml';

patch(MailFormCompiler.prototype, 'regency_estimate', {
    compile(node, params) {
        const res = this._super(...arguments);
        const chatterContainerHookXml = res.querySelector('.o_FormRenderer_chatterContainer');
        if (chatterContainerHookXml && chatterContainerHookXml.classList.contains('oe_chatter_bottom')) {
            setAttributes(chatterContainerHookXml, {
                't-if': 'false',
            });
        }
        return res;
    },
});

patch(FormCompiler.prototype, 'regency_estimate', {
    compile(node, params) {
        const res = this._super(...arguments);
        const chatterContainerHookXml = res.querySelector('.o_FormRenderer_chatterContainer');
        if (chatterContainerHookXml && chatterContainerHookXml.classList.contains('oe_chatter_bottom')) {
            setAttributes(chatterContainerHookXml, {
                't-if': 'true',
            });
        }
        return res;
    },

    compileForm(el, params) {
        const form = this._super(...arguments);
        const chatterContainerHookXml = form.querySelector('.o_FormRenderer_chatterContainer');
        if (chatterContainerHookXml && chatterContainerHookXml.classList.contains('oe_chatter_bottom')) {
            console.log(form.getAttribute('t-attf-class'))
            form.setAttribute('t-attf-class', form.getAttribute('t-attf-class') + ' form_view_with_bottom_chatter')
        }
        return form;
    }
});
