from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    overlay_template_ids = fields.Many2many('overlay.template', 'hotel_template_rel', 'hotel_id', 'template_id')
    background_image = fields.Image('Website Background Image', help='Background image for website header')
    logo_url = fields.Text(compute='_compute_logo_url')

    def _compute_logo_url(self):
        for partner in self:
            image_id = partner.id
            image_model = partner._name
            image_field = 'image_256'
            partner.logo_url = f'/web/image?model={image_model}&id={image_id}&field={image_field}'
