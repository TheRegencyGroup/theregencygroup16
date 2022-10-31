from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    overlay_template_ids = fields.Many2many('overlay.template', 'hotel_template_rel', 'hotel_id', 'template_id')
    background_image = fields.Image('Website Background Image', help='Background image for website header')
