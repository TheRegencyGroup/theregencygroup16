import io
import base64
from fontTools.ttLib import TTFont, TTLibError

from odoo import fields, models, api
from odoo.exceptions import UserError

INVALID_FONT_FORMAT_MESSAGE = 'Invalid font format!'


class OverlayFont(models.Model):
    _name = 'overlay.font'
    _description = 'Overlay font'

    font_name = fields.Char(compute='_compute_font_name', store=True)
    font = fields.Binary(required=True)

    @api.constrains('font')
    def _check_font(self):
        for rec in self:
            try:
                font_file = rec._get_font_file()
                TTFont(font_file)
            except TTLibError:
                raise UserError(INVALID_FONT_FORMAT_MESSAGE)

    @api.depends('font')
    def _compute_font_name(self):
        for rec in self:
            font_file = rec._get_font_file()
            if font_file:
                try:
                    font = TTFont(font_file)
                    rec.font_name = font['name'].getDebugName(1)
                except TTLibError:
                    rec.font_name = INVALID_FONT_FORMAT_MESSAGE
            else:
                rec.font_name = False

    def _get_font_file(self):
        self.ensure_one()
        if self.font:
            return io.BytesIO(base64.b64decode(self.font))
        return False

    def _check_font_in_overlay_template(self):
        overlay_template_ids = self.env['overlay.template'].search([('areas_overlay_font_ids', 'in', self.ids)])
        if overlay_template_ids:
            raise UserError(
                f'Fonts used in overlay templates with ID({", ".join([str(x) for x in overlay_template_ids.ids])})')

    def write(self, vals):
        self._check_font_in_overlay_template()
        return super().write(vals)

    def unlink(self):
        self._check_font_in_overlay_template()
        return super().unlink()
