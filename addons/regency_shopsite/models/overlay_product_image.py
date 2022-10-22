from odoo import fields, models


class OverlayProductImage(models.Model):
    _name = 'overlay.product.image'
    _description = 'Overlay product image'

    image = fields.Image(required=True)
    overlay_position_id = fields.Many2one('overlay.position', required=True)
    overlay_product_id = fields.Many2one('overlay.product', required=True)
