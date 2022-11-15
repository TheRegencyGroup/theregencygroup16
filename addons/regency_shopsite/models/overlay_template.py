import json

from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import ValidationError, UserError
from odoo import fields, models, api, Command, _

from odoo.addons.regency_contacts.models.const import HOTEL


class OverlayTemplate(models.Model):
    _name = 'overlay.template'
    _description = 'Shopsite item template'

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    product_template_id = fields.Many2one('product.template', required=True, string='Product',
                                          domain="[('is_fit_for_overlay', '=', True)]")
    website_published = fields.Boolean(related='product_template_id.website_published')
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
    hotels_without_prices = fields.One2many('res.partner', compute='_compute_hotels_without_prices')
    show_hotels_without_prices = fields.Boolean(compute='_compute_hotels_without_prices')

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
                for overlay_position in rec.areas_data.values():
                    selected_images = overlay_position['selectedImages'].values()
                    image_ids += list(map(lambda x: x['imageId'], selected_images))
                    value_ids += list(map(lambda x: x['valueId'], selected_images))
                value_ids = filter(lambda x: x != 0, value_ids)
                rec.areas_product_image_ids = [Command.set(image_ids)]
                rec.areas_image_attribute_selected_value_ids = [Command.set(value_ids)]

    @api.depends('overlay_attribute_value_ids')
    def _compute_overlay_attribute_value_id(self):
        for rec in self:
            if len(rec.overlay_attribute_value_ids) > 0:
                rec.overlay_attribute_value_id = rec.overlay_attribute_value_ids[0]
            else:
                rec.overlay_attribute_value_id = False

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
        res._create_overlay_attribute_value()
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
        return f'/web/image?model={self.product_template_id._name}&id={self.product_template_id.id}&field=image_512'

    def show_on_website(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': f'/shop/{slug(self)}',
        }
