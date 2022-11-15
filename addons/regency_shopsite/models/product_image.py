from odoo import models, fields
from odoo.exceptions import UserError


class ProductImage(models.Model):
    _inherit = 'product.image'

    is_fit_for_overlay = fields.Boolean(related='product_tmpl_id.is_fit_for_overlay')
    use_as_main = fields.Boolean(default=False)

    def _check_image_in_overlay_template(self):
        if self.env['overlay.template'].search([('areas_product_image_ids', 'in', self.ids)]):
            raise UserError('The image is used in the model "overlay.template"')

    def action_set_as_main_image(self):
        self.ensure_one()
        if self.product_tmpl_id.is_fit_for_overlay:
            self.product_tmpl_id.product_template_image_ids.use_as_main = False
            self.use_as_main = True
            self.product_tmpl_id.image_1920 = self.image_1920

    def write(self, vals):
        if 'image_1920' in vals:
            self._check_image_in_overlay_template()
        res = super(ProductImage, self).write(vals)
        return res

    def unlink(self):
        self._check_image_in_overlay_template()
        return super().unlink()
