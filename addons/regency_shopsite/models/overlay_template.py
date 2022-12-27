import io
from base64 import b64decode, b64encode

from PIL import Image, ImageFont, ImageDraw
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import ValidationError, UserError
from odoo import fields, models, api, Command, _
from odoo.modules import get_module_resource

from odoo.addons.regency_contacts.models.const import HOTEL
from odoo.addons.regency_shopsite.const import TEXT_AREA_TYPE, ELLIPSE_AREA_TYPE, RECTANGLE_AREA_TYPE


class OverlayTemplate(models.Model):
    _name = 'overlay.template'
    _description = 'Shopsite item template'

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    product_template_id = fields.Many2one('product.template', required=True, string='Product',
                                          domain="[('is_fit_for_overlay', '=', True)]")
    is_ready_for_website = fields.Boolean(string='Website Published')
    website_published = fields.Boolean(compute='_compute_website_published', store=True)
    overlay_attribute_value_id = fields.Many2one('product.attribute.value',
                                                 compute='_compute_overlay_attribute_value_id',
                                                 compute_sudo=True)
    overlay_attribute_value_ids = fields.One2many('product.attribute.value', 'overlay_template_id',
                                                  string="Overlay attribute values")
    product_variant_ids = fields.One2many('product.product', compute='_compute_product_variant_ids')
    sale_order_line_ids = fields.One2many('sale.order.line', 'overlay_template_id')
    overlay_attribute_line_ids = fields.One2many('overlay.template.attribute.line', 'overlay_tmpl_id',
                                                 'Overlay Attributes', copy=True)
    overlay_product_ids = fields.One2many('overlay.product', 'overlay_template_id')
    price_item_ids = fields.One2many('product.pricelist.item', 'overlay_tmpl_id', copy=True)
    display_name = fields.Char(compute='_compute_display_name')
    hotel_ids = fields.Many2many('res.partner', 'hotel_template_rel', 'template_id', 'hotel_id', string='Hotels',
                                 domain=[('entity_type', "=", HOTEL)])
    hotels_without_prices = fields.One2many('res.partner', compute='_compute_hotels_without_prices')
    show_hotels_without_prices = fields.Boolean(compute='_compute_hotels_without_prices')

    areas_data = fields.Json()
    overlay_position_ids = fields.Many2many('overlay.position', required=True, string='Positions', ondelete='restrict')
    areas_image_attribute_id = fields.Many2one('product.attribute',
                                               domain="[('id', 'in', possible_areas_image_attribute_ids)]")
    possible_areas_image_attribute_ids = fields.Many2many('product.attribute',
                                                          compute='_compute_possible_areas_image_attribute_ids')
    areas_image_attribute_value_list = fields.Json(compute='_compute_areas_image_attribute_value_list')
    product_template_image_ids = fields.One2many(related='product_template_id.product_template_image_ids')
    areas_product_image_ids = fields.Many2many('product.image', compute='_compute_areas_data_values', store=True,
                                               ondelete='restrict')
    areas_image_attribute_selected_value_ids = fields.Many2many('product.attribute.value',
                                                                compute='_compute_areas_data_values',
                                                                store=True, ondelete='restrict')
    allow_edit = fields.Boolean(compute='_compute_allow_edit')
    all_overlay_fonts = fields.Json(compute='_compute_all_overlay_fonts')
    areas_overlay_font_ids = fields.Many2many('overlay.font', compute='_compute_areas_data_values', store=True,
                                              ondelete='restrict')
    all_overlay_colors = fields.Json(compute='_compute_all_overlay_colors')
    areas_overlay_color_ids = fields.Many2many('overlay.color', compute='_compute_areas_data_values', store=True,
                                               ondelete='restrict')
    preview_image = fields.Image(compute='_compute_preview_image', store=True)
    example_image = fields.Image()

    @api.constrains('areas_data')
    def _check_areas_data(self):
        for rec in self:
            if rec.areas_data and isinstance(rec.areas_data, dict) and rec.areas_data.get('errors', False):
                raise UserError('\n'.join(rec.areas_data['errors']))

    @api.onchange('product_template_id')
    def _onchange_product_template_id(self):
        attribute_ids = self.product_template_id.attribute_line_ids.mapped('attribute_id')
        if self.areas_image_attribute_id and self.areas_image_attribute_id.id not in attribute_ids.ids:
            self.areas_image_attribute_id = False

    def _compute_hotels_without_prices(self):
        for rec in self:
            rec.hotels_without_prices = False
            rec.show_hotels_without_prices = False
            for hotel in rec.hotel_ids:
                if not hotel.property_product_pricelist.item_ids.filtered(lambda f: f.overlay_tmpl_id == rec):
                    rec.hotels_without_prices += hotel
                    rec.show_hotels_without_prices = True

    @api.depends('product_template_id')
    def _compute_possible_areas_image_attribute_ids(self):
        overlay_attribute_id = self.env.ref('regency_shopsite.overlay_attribute')
        customize_attribute_id = self.env.ref('regency_shopsite.customization_attribute')
        for rec in self:
            rec.possible_areas_image_attribute_ids = rec.product_template_id.attribute_line_ids \
                .filtered(lambda x: x.attribute_id.id not in [overlay_attribute_id.id, customize_attribute_id.id]) \
                .mapped('attribute_id').ids

    @api.depends('product_template_id', 'areas_image_attribute_id', 'overlay_attribute_line_ids')
    def _compute_areas_image_attribute_value_list(self):
        for rec in self:
            data = []
            if rec.areas_image_attribute_id:
                overlay_attribute_line_id = self.overlay_attribute_line_ids\
                    .filtered(lambda x: x.attribute_id.id == rec.areas_image_attribute_id.id)
                if overlay_attribute_line_id:
                    value_ids = overlay_attribute_line_id.value_ids
                else:
                    value_ids = self.product_template_id.attribute_line_ids \
                        .filtered(lambda x: x.attribute_id.id == self.areas_image_attribute_id.id).value_ids
                data = [{
                    'id': x.id,
                    'name': x.name,
                } for x in self.env['product.attribute.value'].search([('id', 'in', value_ids.ids)])]
            rec.areas_image_attribute_value_list = data

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.product_template_id.name + ' ' + rec.name

    def _compute_product_variant_ids(self):
        for rec in self:
            rec.product_variant_ids = False
            product_variants = self.env['product.product'].search(
                [('product_tmpl_id', '=', rec.product_template_id.id)])
            overlay_template_attributes = {line.attribute_id: [value for value in line.value_ids] for line in
                                           rec.overlay_attribute_line_ids}
            overlay_template_attributes.update(
                {rec.overlay_attribute_value_id.attribute_id: [rec.overlay_attribute_value_id]})
            for product_variant in product_variants:
                product_template_attributes = {line.attribute_id: line.product_attribute_value_id for line in
                                               product_variant.product_template_attribute_value_ids}
                if all(product_template_attributes.get(k) in v for k, v in overlay_template_attributes.items()):
                    rec.product_variant_ids += product_variant

    @api.depends('areas_data')
    def _compute_areas_data_values(self):
        for rec in self:
            if not rec.areas_data or not isinstance(rec.areas_data, dict):
                rec.areas_product_image_ids = False
                rec.areas_image_attribute_selected_value_ids = False
            else:
                image_ids = []
                value_ids = []
                font_ids = []
                color_ids = []
                for overlay_position in rec.areas_data.values():
                    selected_images = overlay_position['selectedImages'].values()
                    image_ids += list(map(lambda x: x['imageId'], selected_images))
                    value_ids += list(map(lambda x: x['valueId'], selected_images))
                    for area in overlay_position['areaList'].values():
                        if area['areaType'] != TEXT_AREA_TYPE:
                            continue
                        font = area['data'].get('font', False)
                        if font and isinstance(font, dict) and isinstance(font['id'], int):
                            font_ids.append(font['id'])
                        color = area['data'].get('color', False)
                        if color and isinstance(color, dict) and isinstance(color['id'], int):
                            color_ids.append(color['id'])
                value_ids = list(filter(lambda x: x != 0, value_ids))
                rec.areas_product_image_ids = [Command.set(image_ids)]
                rec.areas_image_attribute_selected_value_ids = [Command.set(value_ids)]
                rec.areas_overlay_font_ids = [Command.set(font_ids)]
                rec.areas_overlay_color_ids = [Command.set(color_ids)]

    @api.depends('is_ready_for_website', 'product_template_id.website_published')
    def _compute_website_published(self):
        for rec in self:
            rec.website_published = rec.is_ready_for_website and rec.product_template_id.website_published


    @api.depends('overlay_attribute_value_ids')
    def _compute_overlay_attribute_value_id(self):
        for rec in self:
            if len(rec.overlay_attribute_value_ids) > 0:
                rec.overlay_attribute_value_id = rec.overlay_attribute_value_ids[0]
            else:
                rec.overlay_attribute_value_id = False

    @api.depends('overlay_product_ids')
    def _compute_allow_edit(self):
        for rec in self:
            rec.allow_edit = not bool(rec.overlay_product_ids) or not rec.id

    def _compute_all_overlay_fonts(self):
        all_overlay_fonts = self.env['overlay.font'].search([]).read(['id', 'font_name'])
        for rec in self:
            rec.all_overlay_fonts = all_overlay_fonts

    def _compute_all_overlay_colors(self):
        all_overlay_colors = self.env['overlay.color'].search([]).read(['id', 'name', 'color'])
        for rec in self:
            rec.all_overlay_colors = all_overlay_colors

    @api.depends('areas_data')
    def _compute_preview_image(self):
        for rec in self:
            if not rec.areas_data or not isinstance(rec.areas_data, dict):
                rec.preview_image = False
            else:
                position = list(rec.areas_data.values())[0]
                if not position.get('selectedImages'):
                    rec.preview_image = False
                    continue
                product_image_id = list(position['selectedImages'].values())[0]['imageId']
                product_image = self.env['product.image'].browse(product_image_id).exists()
                if not product_image:
                    rec.preview_image = False
                    continue
                background_image = Image.open(io.BytesIO(b64decode(product_image.image_1920)))
                width = position['canvasSize']['width']
                height = position['canvasSize']['height']
                background_image = background_image.resize((width, height))

                for area in position.get('areaList', {}).values():
                    area_type = area['areaType']
                    area_x = area['data']['x']
                    area_y = area['data']['y']
                    area_angle = area['data']['angle']

                    if area_type == ELLIPSE_AREA_TYPE:
                        area_width = area['data']['rx'] * 2
                        area_height = area['data']['ry'] * 2
                    else:
                        area_width = area['data']['width']
                        area_height = area['data']['height']

                    scale = 1
                    if area_type == RECTANGLE_AREA_TYPE:
                        scale = 0.8
                    elif area_type == ELLIPSE_AREA_TYPE:
                        if area_width > area_height:
                            scale = area_height / area_width * 1.2
                        elif area_width > area_height:
                            scale = area_width / area_height * 1.2
                        else:
                            scale = 0.7

                    if area_type == TEXT_AREA_TYPE:
                        font_size = area['data'].get('fontSize', 14)
                        image_color = '#000000'
                        image_font = ImageFont.truetype(
                            font=get_module_resource('regency_shopsite', 'static/src/fonts', 'Arial.ttf'), size=font_size)
                        area_font = area['data'].get('font', False)
                        if area_font and isinstance(area_font, dict) and isinstance(area_font['id'], int):
                            font_id = area_font['id']
                            font = self.env['overlay.font'].browse(font_id).exists()
                            if font:
                                font_file = io.BytesIO(b64decode(font.font))
                                image_font = ImageFont.truetype(font=font_file, size=font_size)
                        area_color = area['data'].get('color', False)
                        if area_color and isinstance(area_color, dict) and isinstance(area_color['id'], int):
                            color_id = area_color['id']
                            color = self.env['overlay.color'].browse(color_id)
                            if color:
                                image_color = color.color
                        logo_image = Image.new('RGBA', (area_width, area_height), '#FFFFFF00')
                        d = ImageDraw.Draw(logo_image)
                        d.text((int(area_width / 2), int(area_height / 2)), 'Text', fill=image_color, anchor='mm',
                               font=image_font)
                    else:
                        logo_image = Image.open(get_module_resource('regency_shopsite', 'static/src/img', 'logo.png'))

                    if area_type != TEXT_AREA_TYPE:
                        if area_width >= area_height and logo_image.width < logo_image.height:
                            scale_logo_height = int(area_height * scale)
                            scale_logo_width = int((logo_image.width * scale_logo_height) / logo_image.height)
                        else:
                            scale_logo_width = int(area_width * scale)
                            scale_logo_height = int((logo_image.height * scale_logo_width) / logo_image.width)
                        logo_image = logo_image.resize((scale_logo_width, scale_logo_height))

                    if area_angle != 0:
                        logo_image = logo_image.rotate((360 - area_angle), resample=Image.BICUBIC, expand=True)
                        area_bound_rect_width = area['data']['boundRect']['width']
                        area_bound_rect_height = area['data']['boundRect']['height']
                        area_bound_rect_x = area['data']['boundRect']['x']
                        area_bound_rect_y = area['data']['boundRect']['y']
                        x = area_bound_rect_x + int((area_bound_rect_width - logo_image.width) / 2)
                        y = area_bound_rect_y + int((area_bound_rect_height - logo_image.height) / 2)
                    else:
                        x = area_x + int((area_width - logo_image.width) / 2)
                        y = area_y + int((area_height - logo_image.height) / 2)
                    background_image.paste(logo_image, (x, y), logo_image)

                result_image = io.BytesIO()
                background_image.save(result_image, format='PNG')
                rec.preview_image = b64encode(result_image.getvalue())

    @api.onchange('product_template_id')
    @api.constrains('product_template_id')
    def _constrains_changes_if_has_overlay_product(self):
        for rec in self:
            if rec.overlay_product_ids:
                raise ValidationError(_("The '%s' shopsite item template (ID%s) has customize items."
                                        "A product template shouldn't be change for it.")
                                      % (rec.name, rec.id,))

    @api.constrains('active')
    def _constrains_archive_and_deletion(self):
        """ to restrict deletion the method should be used in def unlink"""
        for ot in self:
            active_overlay_product_ids = ot.overlay_product_ids.filtered(lambda op: op.active)
            if active_overlay_product_ids:
                raise ValidationError(f"Overlay template '{ot.name}' has active overlay product "
                                      f"'{active_overlay_product_ids[0].name}', cause could not be delete or archived")

    def _create_overlay_attribute_value(self):
        overlay_attribute_id = self.env.ref('regency_shopsite.overlay_attribute')
        for rec in self:
            attr_value_model = self.env['product.attribute.value']
            overlay_attribute_value_id = attr_value_model.search([('overlay_template_id', '=', rec.id)], limit=1)
            if not overlay_attribute_value_id:
                overlay_attribute_value_id = self.env['product.attribute.value'].create({
                    'name': rec.id,
                    'attribute_id': overlay_attribute_id.id,
                    'overlay_template_id': rec.id,
                })
            product_overlay_attribute_line_id = rec.product_template_id.attribute_line_ids.filtered(
                lambda x: x.attribute_id.id == overlay_attribute_id.id)
            if product_overlay_attribute_line_id:
                product_overlay_attribute_line_id.with_context(from_overlay_template=True) \
                    .value_ids = [Command.link(overlay_attribute_value_id.id)]
            else:
                product_overlay_attribute_line_id = self.env['product.template.attribute.line'].with_context(
                    from_overlay_template=True).create({
                    'attribute_id': overlay_attribute_id.id,
                    'value_ids': [Command.link(overlay_attribute_value_id.id)],
                    'product_tmpl_id': rec.product_template_id.id,
                })
            product_overlay_attribute_line_id._update_product_template_attribute_values()

    def _unlink_overlay_attribute_value(self):
        overlay_attribute_id = self.env.ref('regency_shopsite.overlay_attribute')
        for rec in self:
            product_overlay_attribute_line_id = rec.product_template_id.attribute_line_ids.filtered(
                lambda x: x.attribute_id.id == overlay_attribute_id.id)
            overlay_attribute_value_id = product_overlay_attribute_line_id.value_ids.filtered(
                lambda x: x.overlay_template_id.id == rec.id)
            if len(product_overlay_attribute_line_id.value_ids) > 1:
                product_overlay_attribute_line_id.with_context(from_overlay_template=True) \
                    .value_ids = [Command.unlink(overlay_attribute_value_id.id)]
                product_overlay_attribute_line_id._update_product_template_attribute_values()
            else:
                product_overlay_attribute_line_id.with_context(from_overlay_template=True).unlink()

    def _clear_overlay_attribute_line_ids(self):
        for rec in self:
            rec.overlay_attribute_line_ids.unlink()

    @api.model
    def default_get(self, fields):
        defaults = super().default_get(fields)
        defaults['all_overlay_fonts'] = self.env['overlay.font'].search([]).read(['id', 'font_name'])
        defaults['all_overlay_colors'] = self.env['overlay.color'].search([]).read(['id', 'name', 'color'])
        return defaults

    def write(self, vals):
        change_product_template_id = 'product_template_id' in vals
        if change_product_template_id:
            self._unlink_overlay_attribute_value()
        res = super(OverlayTemplate, self).write(vals)
        if change_product_template_id:
            self._create_overlay_attribute_value()
            self._clear_overlay_attribute_line_ids()
        return res

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        res.with_context(is_overlay_template_initiator=True)._create_overlay_attribute_value()
        return res

    def unlink(self):
        self._constrains_archive_and_deletion()
        self._unlink_overlay_attribute_value()
        return super().unlink()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (Copy)") % self.name
        return super().copy(default=default)

    def _get_product_template_attribute_value_id(self):
        self.ensure_one()
        product_template_value_ids = self.product_template_id.attribute_line_ids.product_template_value_ids
        product_template_value_id = product_template_value_ids.filtered(
            lambda x: x.product_attribute_value_id.id == self.overlay_attribute_value_id.id)
        return product_template_value_id

    def _preview_image_url(self):
        self.ensure_one()
        return f'/web/image?model={self._name}&id={self.id}&field=preview_image'

    def show_on_website(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': f'/shop/{slug(self)}',
        }
