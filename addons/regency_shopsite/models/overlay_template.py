import json

from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.exceptions import ValidationError
from odoo import fields, models, api, Command, _


class OverlayTemplate(models.Model):
    _name = 'overlay.template'
    _description = 'Shopsite item template'

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    product_template_id = fields.Many2one('product.template', required=True, string='Product',
                                          domain="[('is_fit_for_overlay', '=', True)]")
    overlay_attribute_value_id = fields.Many2one('product.attribute.value',
                                                 compute='_compute_overlay_attribute_value_id',
                                                 compute_sudo=True)
    overlay_attribute_value_ids = fields.One2many('product.attribute.value', 'overlay_template_id')
    product_variant_ids = fields.One2many('product.product', compute='_compute_product_variant_ids')
    sale_order_line_ids = fields.One2many('sale.order.line', 'overlay_template_id')
    overlay_position_ids = fields.Many2many('overlay.position', required=True, string='Positions', ondelete='restrict')
    overlay_attribute_line_ids = fields.One2many('overlay.template.attribute.line', 'overlay_tmpl_id',
                                                 'Overlay Attributes', copy=True)
    product_image_ids = fields.Many2many('product.image', compute='_compute_images', store=True, ondelete='restrict')

    use_product_template_image = fields.Boolean(compute='_compute_images', store=True)
    areas_json = fields.Char()
    overlay_product_ids = fields.One2many('overlay.product', 'overlay_template_id')
    price_item_ids = fields.One2many('product.pricelist.item', 'overlay_tmpl_id', copy=True)
    display_name = fields.Char(compute='_compute_display_name')

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

    @api.onchange('product_template_id', 'overlay_position_ids', 'overlay_attribute_line_ids')
    def _compute_areas_json(self):
        for rec in self:
            json_val = json.loads(rec.areas_json) if rec.areas_json else {}

            product_template_id = json_val.get('productTemplateId', False)
            product_template_changed = False
            if product_template_id != rec.product_template_id.id:
                product_template_changed = True

            image_list = []
            if rec.product_template_id:
                for product_image in rec.product_template_id._get_images():
                    if product_image.image_1920:
                        image_list.append({
                            'id': product_image.id,
                            'model': product_image._name,
                        })
            json_val['productTemplateId'] = rec.product_template_id.id
            json_val['productImageList'] = image_list

            overlay_positions = json_val.get('overlayPositions', {})
            for overlay_position_id in rec.overlay_position_ids.ids:
                overlay_position = overlay_positions.get(str(overlay_position_id))
                if not overlay_position:
                    overlay_position = {
                        'id': overlay_position_id,
                        'name': self.env['overlay.position'].browse(overlay_position_id).name,
                        'imageColorId': False,
                        'areaList': {}
                    }
                color_images = overlay_position.get('colorImages', {})
                overlay_attribute_line_ids = rec.overlay_attribute_line_ids
                color_attribute_id = self.env.ref('regency_shopsite.color_attribute')
                overlay_color_attribute_line_id = overlay_attribute_line_ids.filtered(
                    lambda x: x.attribute_id.id == color_attribute_id.id)
                if not overlay_color_attribute_line_id or not overlay_color_attribute_line_id.value_ids:
                    color_attribute_line_id = rec.product_template_id.attribute_line_ids.filtered(
                        lambda x: x.attribute_id.id == color_attribute_id.id)
                    color_attribute_value_ids = color_attribute_line_id.value_ids
                else:
                    color_attribute_value_ids = overlay_color_attribute_line_id.value_ids
                for color_value in color_attribute_value_ids:
                    color_value_id = color_value.ids[0]
                    if not color_images.get(str(color_value_id)):
                        color_images[str(color_value_id)] = {
                            'id': color_value_id,
                            'name': color_value.name,
                            'imageId': False,
                            'imageModel': False,
                        }
                removed_images_color_ids = list(
                    set(map(int, color_images.keys())).difference(set(color_attribute_value_ids.ids)))
                for color_id in removed_images_color_ids:
                    del color_images[str(color_id)]
                overlay_position['colorImages'] = color_images
                overlay_positions[str(overlay_position_id)] = overlay_position

            removed_overlay_position_ids = list(
                set(map(int, overlay_positions.keys())).difference(set(rec.overlay_position_ids.ids)))
            for overlay_position_id in removed_overlay_position_ids:
                del overlay_positions[str(overlay_position_id)]
            if product_template_changed:
                for overlay_position in overlay_positions.values():
                    overlay_position['areaList'] = {}
            json_val['overlayPositions'] = overlay_positions

            rec.areas_json = json.dumps(json_val)

    @api.depends('areas_json')
    def _compute_images(self):
        for rec in self:
            json_val = json.loads(rec.areas_json) if rec.areas_json else {}
            product_image_ids = []
            use_product_template_image = False
            overlay_positions = json_val.get('overlayPositions', {})
            for overlay_pos in overlay_positions.values():
                for image in overlay_pos.get('colorImages', {}).values():
                    image_id = image.get('imageId', False)
                    image_model = image.get('imageModel', False)
                    if image_id and image_model == 'product.image':
                        product_image_ids.append(image_id)
                    elif image_id and image_model == 'product.template':
                        use_product_template_image = True
            rec.product_image_ids = [Command.set(product_image_ids)]
            rec.use_product_template_image = use_product_template_image

    def get_main_image_url(self):
        self.ensure_one()
        pt = self.product_template_id
        model, id_, image_field = pt._name, pt.id, 'image_256'
        url = f'/web/image?model={model}&id={id_}&field={image_field}'
        return url

    @api.depends('overlay_attribute_value_ids')
    def _compute_overlay_attribute_value_id(self):
        for rec in self:
            if len(rec.overlay_attribute_value_ids) > 0:
                rec.overlay_attribute_value_id = rec.overlay_attribute_value_ids[0]
            else:
                rec.overlay_attribute_value_id = False

    @api.onchange('product_template_id')
    @api.constrains('product_template_id')
    def _constrains_changes_if_has_sale(self):
        for record in self:
            if not record.active:
                continue
            if record.sale_order_line_ids:
                raise ValidationError(_("The '%s' shopsite item template (ID%s) has sales."
                                        "A product template shouldn't be change for it.")
                                      % (record.name, record.id,))

    def _create_overlay_attribute_value(self):
        overlay_attribute_id = self.env.ref('regency_shopsite.overlay_attribute')
        for rec in self:
            ProductAttributeValue = self.env['product.attribute.value']
            overlay_attribute_value_id = ProductAttributeValue.search([('overlay_template_id', '=', rec.id)], limit=1)
            if not overlay_attribute_value_id:
                overlay_attribute_value_id = self.env['product.attribute.value'].create({
                    'name': rec.id,
                    'attribute_id': overlay_attribute_id.id,
                    'overlay_template_id': rec.id,
                    'is_custom': True,
                })
            product_overlay_attribute_line_id = rec.product_template_id.attribute_line_ids.filtered(
                lambda x: x.attribute_id.id == overlay_attribute_id.id)
            if product_overlay_attribute_line_id:
                product_overlay_attribute_line_id.with_context(from_overlay_template=True)\
                    .value_ids = [Command.link(overlay_attribute_value_id.id)]
            else:
                product_overlay_attribute_line_id = self.env['product.template.attribute.line'].with_context(from_overlay_template=True).create({
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
                product_overlay_attribute_line_id.with_context(from_overlay_template=True)\
                    .value_ids = [Command.unlink(overlay_attribute_value_id.id)]
                product_overlay_attribute_line_id._update_product_template_attribute_values()
            else:
                product_overlay_attribute_line_id.with_context(from_overlay_template=True).unlink()

    def _clear_overlay_attribute_line_ids(self):
        for rec in self:
            rec.overlay_attribute_line_ids.unlink()

    def write(self, vals):
        change_product_template_id = 'product_template_id' in vals
        if change_product_template_id:
            self._unlink_overlay_attribute_value()
        res = super(OverlayTemplate, self).write(vals)
        if change_product_template_id:
            self._create_overlay_attribute_value()
            self._clear_overlay_attribute_line_ids()
        return res

    @api.model
    def create(self, vals):
        res = super(OverlayTemplate, self).create(vals)
        res._create_overlay_attribute_value()
        return res

    def unlink(self):
        self._constrains_changes_if_has_sale()
        self._unlink_overlay_attribute_value()
        return super(OverlayTemplate, self).unlink()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (Copy)") % self.name
        return super(OverlayTemplate, self).copy(default=default)

    def _get_product_template_attribute_value_id(self):
        self.ensure_one()
        product_template_value_ids = self.product_template_id.attribute_line_ids.product_template_value_ids
        product_template_value_id = product_template_value_ids.filtered(
            lambda x: x.product_attribute_value_id.id == self.overlay_attribute_value_id.id)
        return product_template_value_id

    def show_on_website(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': f'/shopsite/{slug(self)}',
        }
