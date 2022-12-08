from odoo import fields, models, api

from odoo.addons.regency_shopsite.image_tools import check_if_image_is_vector


class OverlayProductAreaImage(models.Model):
    _name = 'overlay.product.area.image'
    _description = 'Overlay product area image'

    image = fields.Binary(required=True)
    image_type = fields.Char()
    image_extension = fields.Char()
    image_name = fields.Char(compute='_compute_image_name')
    image_filename = fields.Char()
    is_vector_image = fields.Boolean(compute='_compute_is_vector_image', store=True)
    area_index = fields.Integer()
    area_object_index = fields.Integer()
    overlay_product_id = fields.Many2one('overlay.product', ondelete='cascade', copy=False)
    overlay_position_ids = fields.Many2many(related='overlay_product_id.overlay_template_id.overlay_position_ids')
    hotel_ids = fields.Many2many(related='overlay_product_id.hotel_ids')
    overlay_position_id = fields.Many2one('overlay.position', domain="[('id', 'in', overlay_position_ids)]", required=True)
    added_on_website = fields.Boolean(readonly=True)

    @api.depends('overlay_product_id', 'overlay_position_id', 'area_index', 'area_object_index')
    def _compute_image_name(self):
        for rec in self:
            if rec.added_on_website:
                rec.image_name = f'{rec.overlay_product_id.name}__{rec.overlay_position_id.name}_' \
                                          f'{rec.area_index}_{rec.area_object_index}.{rec.image_extension}'
            else:
                rec.image_name = rec.image_filename

    @api.depends('image', 'image_type')
    def _compute_is_vector_image(self):
        for rec in self:
            rec.is_vector_image = check_if_image_is_vector(rec.image.decode(), rec.image_type) if rec.image else False
