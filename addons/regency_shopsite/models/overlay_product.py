from datetime import datetime
from collections import namedtuple

ImageParams = namedtuple('ImageParams', ['model_name', 'rec_id', 'field_name'])

from odoo import api, Command, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.regency_shopsite.const import OVERLAY_PRODUCT_ID_URL_PARAMETER, TEXT_AREA_TYPE


class OverlayProduct(models.Model):
    _name = 'overlay.product'
    _description = 'Overlay product'

    active = fields.Boolean(default=True)
    overlay_template_id = fields.Many2one('overlay.template', required=True, ondelete='restrict')
    product_tmpl_id = fields.Many2one(string="Product template", related='overlay_template_id.product_template_id',
                                      store=True)
    website_published = fields.Boolean(related='overlay_template_id.website_published')
    hotel_ids = fields.Many2many(related='overlay_template_id.hotel_ids')
    name = fields.Char()
    product_id = fields.Many2one('product.product', copy=False)
    customize_attribute_value_id = fields.Many2one('product.attribute.value',
                                                   compute='_compute_customize_attribute_value_id',
                                                   compute_sudo=True)
    customize_attribute_value_ids = fields.One2many('product.attribute.value', 'overlay_product_id')
    product_template_attribute_value_ids = fields.Many2many('product.template.attribute.value')
    overlay_product_image_ids = fields.One2many('overlay.product.image', 'overlay_product_id', readonly=True,
                                                copy=False)
    overlay_product_area_image_ids = fields.One2many('overlay.product.area.image', 'overlay_product_id', copy=False)
    area_list_data = fields.Json()
    areas_text_table = fields.Html(compute='_compute_areas_text_table', store=True)
    last_updated_date = fields.Datetime(readonly=True, copy=False)
    updated_by_id = fields.Many2one('res.users', readonly=True, copy=False)

    @api.depends('customize_attribute_value_ids')
    def _compute_customize_attribute_value_id(self):
        for rec in self:
            if len(rec.customize_attribute_value_ids) > 0:
                rec.customize_attribute_value_id = rec.customize_attribute_value_ids[0]
            else:
                rec.customize_attribute_value_id = False

    @api.depends('area_list_data')
    def _compute_areas_text_table(self):
        for rec in self:
            if not rec.area_list_data:
                rec.areas_text_table = False
                continue
            table_content = ''
            for position in rec.area_list_data.values():
                text_areas = list(filter(lambda x: x['type'] == TEXT_AREA_TYPE, position['areaList'].values()))
                text_objects = list(map(lambda x: x['data'], text_areas))
                text_objects = [item for sublist in text_objects for item in sublist]
                for index, area in enumerate(text_objects):
                    first_cell = ''
                    if index == 0:
                        first_cell = f'''
                            <td rowspan={len(text_objects)}>
                                {position.get('overlayPositionName') or ''}
                            </td>
                        '''
                    table_content += f'''
                        <tr>
                            {first_cell}
                            <td>{area['objectData'].get('text', '')}</td>
                            <td>{area['objectData'].get('fontName', '')}</td>
                            <td>{area['objectData'].get('fontSize', '0')}</td>
                            <td>{area['objectData'].get('lineSpacing') or '0'}</td>
                            <td>{area['objectData'].get('charSpacing', '0')}</td>
                            <td>{area['objectData'].get('fontColor', '')}</td>
                            <td>{area['objectData'].get('align', '').capitalize()}</td>
                        </tr>
                    '''
            table = f'''
                <table class="table table-bordered">
                    <thead>
                        <th>Position</th>
                        <th>Text</th>
                        <th>Font</th>
                        <th>Font size</th>
                        <th>Line spacing</th>
                        <th>Char spacing</th>
                        <th>Color</th>
                        <th>Align</th>
                    </thead>
                    <tbody>
                        {table_content}
                    </tbody>
                </table>
            '''
            rec.areas_text_table = table

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        res.with_context(from_overlay_product=True)._create_attribute_value()
        return res

    def unlink(self):
        self._constrains_if_has_sale()
        res = super(OverlayProduct, self).unlink()
        return res

    def write(self, vals):
        res = super(OverlayProduct, self).write(vals)
        if 'active' in vals.keys():
            self.product_id.active = vals['active']
        return res

    def _constrains_if_has_sale(self):
        sales = self._get_sale_order_line_ids(limit=1)
        if sales:
            model_name, model_id = sales._name, sales.id
            raise ValidationError(_("The operation cannot be completed: another model requires "
                                    "the record being deleted. If possible, archive it instead.\n\n"
                                    f"Model: {model_name}s, ID: {model_id}"
                                    ))

    def _get_sale_order_line_ids(self, limit=None):
        # TODO [REF] if necessary: add field sale_order_line_ids instead and add ondelete=restrict (tech debt from REG-151)
        return self.env['sale.order.line'].search([('product_id', 'in', self.product_id.ids)], limit=limit)

    def _create_attribute_value(self):
        customization_attr = self.env.ref('regency_shopsite.customization_attribute')
        attr_value_model = self.env['product.attribute.value']
        attr_line_model = self.env['product.template.attribute.line']
        for entry in self:
            pav = attr_value_model.create({
                'name': f"{entry.id}",
                'attribute_id': customization_attr.id,
                'overlay_product_id': entry.id,
                'sequence': 1,
            })
            ptal = entry.product_tmpl_id.attribute_line_ids.filtered(lambda f: f.attribute_id == customization_attr)
            if ptal:
                ptal.write({'value_ids': [Command.link(pav.id)]})
            else:
                attr_line_model.create({
                    'product_tmpl_id': entry.product_tmpl_id.id,
                    'attribute_id': customization_attr.id,
                    'value_ids': [Command.link(pav.id)]
                })

    def _set_update_info(self):
        for rec in self:
            rec.last_updated_date = datetime.now()
            rec.updated_by_id = self.env.user.id

    def _preview_image_url(self):
        self.ensure_one()
        params = self._preview_image_params()
        return f'/web/image?model={params.model_name}&id={params.rec_id}&field={params.field_name}'

    def _preview_image(self):
        self.ensure_one()
        params = self._preview_image_params()
        return self.env[params.model_name].browse(params.rec_id)[params.field_name]

    def _preview_image_params(self):
        self.ensure_one()
        if self.overlay_product_image_ids:
            image_params = ImageParams(self.overlay_product_image_ids._name, self.overlay_product_image_ids[0].id,
                                       'image')
        else:
            image_params = ImageParams(self.product_tmpl_id._name, self.product_tmpl_id.id, 'image_512')
        return image_params

    @property
    def url(self):
        self.ensure_one()
        return f'/shop/{slug(self.overlay_template_id)}?{OVERLAY_PRODUCT_ID_URL_PARAMETER}={self.id}'

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        res = super().copy(default=default)
        for overlay_product_image_id in self.overlay_product_image_ids:
            new_overlay_product_image_id = overlay_product_image_id.copy()
            new_overlay_product_image_id.overlay_product_id = res.id
        for overlay_product_area_image_id in self.overlay_product_area_image_ids:
            new_overlay_product_area_image_id = overlay_product_area_image_id.copy()
            new_overlay_product_area_image_id.overlay_product_id = res.id
        res.name = self.name + ' (Copy)'
        res._set_update_info()
        return res
