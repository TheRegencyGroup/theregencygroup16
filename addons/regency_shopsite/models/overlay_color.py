from odoo import fields, models, api
from odoo.exceptions import UserError


class OverlayColor(models.Model):
    _name = 'overlay.color'
    _description = 'Overlay color'

    name = fields.Char()
    color = fields.Char(help='Color in HEX format')

    @api.constrains('color')
    def _check_font(self):
        for rec in self:
            pass

    def _check_color_in_overlay_template(self):
        overlay_template_ids = self.env['overlay.template'].search([('areas_overlay_color_ids', 'in', self.ids)])
        if overlay_template_ids:
            raise UserError(
                f'Colors used in overlay templates with ID({", ".join([str(x) for x in overlay_template_ids.ids])})')

    def write(self, vals):
        self._check_color_in_overlay_template()
        return super().write(vals)

    def unlink(self):
        self._check_color_in_overlay_template()
        return super().unlink()
