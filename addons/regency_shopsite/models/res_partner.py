from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    overlay_template_ids = fields.Many2many('overlay.template', 'hotel_template_rel', 'hotel_id', 'template_id')
    background_image = fields.Image('Website Background', help='Background image for website header')
    logo_url = fields.Text(compute='_compute_logo_url')
    background_url = fields.Text(compute='_compute_background_url')

    def _compute_logo_url(self):
        for partner in self:
            image_field = 'image_256'
            self.env['ir.config_parameter'].sudo().get_param('database.secret')
            if not partner[image_field]:
                a = 1
            image_id = partner.id
            image_model = partner._name
            partner.logo_url = f'/web/image?model={image_model}&id={image_id}&field={image_field}'

    def _compute_background_url(self):
        for partner in self:
            if partner.background_image:
                image_id = partner.id
                image_model = partner._name
                image_field = 'background_image'
                background_url = f'/web/image?model={image_model}&id={image_id}&field={image_field}'
            else:
                background_url = ''
            partner.background_url = background_url

