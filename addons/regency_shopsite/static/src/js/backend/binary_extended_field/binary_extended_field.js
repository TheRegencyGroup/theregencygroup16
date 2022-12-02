/** @odoo-module **/

import { BinaryField } from '@web/views/fields/binary/binary_field';
import { registry } from "@web/core/registry";

export class BinaryExtendedField extends BinaryField {
    update({ data, name, type }) {
        this.state.fileName = name || "";
        const { fileNameField, fileTypeField, record } = this.props;
        const changes = { [this.props.name]: data || false };
        if (fileNameField in record.fields && record.data[fileNameField] !== name) {
            changes[fileNameField] = name || false;
        }
        if (fileTypeField in record.fields) {
            changes[fileTypeField] = type || false;
        }
        return this.props.record.update(changes);
    }
}

BinaryField.props = {
    ...BinaryField.props,
    fileTypeField: { type: String, optional: true },
};

BinaryExtendedField.extractProps = ({ attrs }) => {
    return {
        acceptedFileExtensions: attrs.options.accepted_file_extensions,
        fileNameField: attrs.filename,
        fileTypeField: attrs.filetype,
    };
};

registry.category('fields').add('binary_extended', BinaryExtendedField);
