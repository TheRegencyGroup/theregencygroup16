/** @odoo-module **/

import BasicModel from 'web.BasicModel';

BasicModel.include({
    setDirtyForce(recordID) {
        let record = this.localData[recordID];
        record._isDirty = true;
    },
});
