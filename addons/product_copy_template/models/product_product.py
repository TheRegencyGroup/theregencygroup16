from odoo import api, fields, models

NOT_COPIED_FIELDS = ['product_source_id', 'name']


class Product(models.Model):
    _inherit = 'product.template'

    product_source_id = fields.Many2one('product.template', string='Template Product')

    @api.onchange('product_source_id')
    def _onchange_product_source_id(self):
        if self.product_source_id:
            vals = self.product_source_id.with_context(active_test=False).copy_data()[0]
            for key, val in vals.items():
                if not key in NOT_COPIED_FIELDS:
                    if key == 'attribute_line_ids':
                        val = self._remove_attribute_values(val)
                    self[key] = val

    def _remove_attribute_values(self, values):
        for val in values:
            val[2]['value_ids'] = []
        return values
