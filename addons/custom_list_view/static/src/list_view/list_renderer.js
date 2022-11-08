/** @odoo-module **/

import { ListRenderer } from '@web/views/list/list_renderer';
import { patch } from 'web.utils';

const { onMounted } = owl;

patch(ListRenderer.prototype, 'custom_list_view', {
    setup() {
        this._super(...arguments);
        onMounted(() => {
            for (let th of document.querySelectorAll('thead th')) {
                let fieldName = th.dataset.name;
               if (!fieldName) {
                   continue;
               }
               let column = this.state.columns.find(e => e.name === fieldName);
               if (!column) {
                   continue;
               }
               if (!column.options.hide_sort_icon) {
                   continue;
               }
               let sortIcon = th.querySelector('div i');
               if (sortIcon) {
                   sortIcon.classList.add('d-none');
               }
            }
        });
    },

    freezeColumnWidths() {
        this._super(...arguments);
        if(this.tableRef.el){
            const headers = [...this.tableRef.el.querySelectorAll("thead th:not(.o_list_actions_header)")];
            for (let th of headers) {
                const fieldName = th.dataset.name;
                if (!fieldName) {
                    continue;
                }
                const column = this.state.columns.find(e => e.name === fieldName);
                if (!column) {
                    continue;
                }
                const widthOption = column.options.width;
                if (!widthOption) {
                    continue;
                }
                th.style.width = widthOption;
                th.style.maxWidth = 'unset';
                th.style.minWidth = 'unset';
            }
        }
    },
});
