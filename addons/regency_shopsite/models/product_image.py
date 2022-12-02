from odoo import models, fields
from odoo.exceptions import UserError


class ProductImage(models.Model):
    _inherit = 'product.image'

    def _check_image_in_overlay_template(self):
        if self.env['overlay.template'].search([('areas_product_image_ids', 'in', self.ids)]):
            raise UserError('The image is used in the model "overlay.template"')

    def write(self, vals):
        if 'image_1920' in vals:
            self._check_image_in_overlay_template()
        res = super(ProductImage, self).write(vals)
        return res

    def unlink(self):
        self._check_image_in_overlay_template()
        return super().unlink()
