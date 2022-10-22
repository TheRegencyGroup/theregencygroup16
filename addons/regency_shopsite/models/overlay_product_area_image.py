from odoo import fields, models


class OverlayProductAreaImage(models.Model):
    _name = 'overlay.product.area.image'
    _description = 'Overlay product area image'

    image = fields.Image(required=True)
    overlay_position_id = fields.Many2one('overlay.position', required=True)
    area_index = fields.Integer(required=True)
    area_object_index = fields.Integer(required=True)
    overlay_product_id = fields.Many2one('overlay.product', required=True)