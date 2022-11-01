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
            rec_id = partner.id if partner[image_field] else self.env['ir.config_parameter'].sudo().get_param('regency.fallback_partner_id')
            model = partner._name
            partner.logo_url = f'/web/image?model={model}&id={rec_id}&field={image_field}'

    def _compute_background_url(self):
        for partner in self:
            image_field = 'background_image'
            rec_id = partner.id if partner[image_field] else self.env['ir.config_parameter'].sudo().get_param('regency.fallback_partner_id')
            model = partner._name
            background_url = f'/web/image?model={model}&id={rec_id}&field={image_field}'
            has_background_img = bool(self.browse(rec_id)[image_field])
            partner.background_url = background_url if has_background_img else ''

