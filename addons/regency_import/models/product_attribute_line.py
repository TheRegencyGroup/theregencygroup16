from odoo import fields, models, api, Command


class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"

    product_id = fields.Many2one('product.product')
    value = fields.Char()

    @api.model_create_multi
    def create(self, val_list):
        for val in val_list:
            if 'product_id' in val:
                val['product_tmpl_id'] = self.env['product.product'].browse(val.get('product_id')).product_tmpl_id.id
            if 'value' in val:
                value_ids = self.env['product.attribute.value'].search([('attribute_id', '=', val.get('attribute_id')),
                                                            ('name', '=', val.get('value'))]).ids
                if not value_ids:
                    value_ids = self.env['product.attribute.value'].search([('attribute_id', '=', val.get('attribute_id')),
                                                                ('name', '=ilike', val.get('value'))]).ids
                if value_ids:
                    val['value_ids'] = value_ids
        recs = super().create(val_list)
        return recs
