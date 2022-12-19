from odoo import fields, models


class OverlayProductImage(models.Model):
    _name = 'overlay.product.image'
    _description = 'Overlay product image'

    image = fields.Image(required=True)
    overlay_position_id = fields.Many2one('overlay.position', required=True)
    overlay_product_id = fields.Many2one('overlay.product', ondelete='cascade', copy=False)

    def action_download_image(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': f'/web/content/{self._name}/{self.id}/image?download=True',
        }
