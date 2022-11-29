from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    overlay_template_ids = fields.Many2many('overlay.template', 'hotel_template_rel', 'hotel_id', 'template_id')
    background_image = fields.Image('Website Background', help='Background image for website header')
    logo_url = fields.Text(compute='_compute_logo_url')
    background_url = fields.Text(compute='_compute_background_url')

    def _get_delivery_address_str(self):
        self.ensure_one()
        data = [f'{self.street}', f'{self.street2}', f'{self.city}', f'{self.state_id.name}', f'{self.zip}',
                f'{self.country_id.name}']
        address = ", ".join(x for x in data if x)
        return address

    def _compute_logo_url(self):
        for partner in self:
            image_field = 'image_256'
            rec_id = partner._get_rec_id_with_image(image_field) or partner.id
            partner.logo_url = partner._prepare_image_link(rec_id, image_field)

    def _compute_background_url(self):
        for partner in self:
            image_field = 'background_image'
            rec_id_with_image = partner._get_rec_id_with_image(image_field)
            url = ''
            if rec_id_with_image:
                url = partner._prepare_image_link(rec_id_with_image, image_field)
            partner.background_url = url

    @api.model
    def _prepare_image_link(self, rec_id: int, image_field_name: str) -> str:
        """if rec_id has no image, oddo displays default "no image" pic"""
        self.ensure_one()
        if not isinstance(rec_id, int) or rec_id < 1:
            raise TypeError(f"rec_id should be int with value:{rec_id} > 0")
        return f'/web/image?model={self._name}&id={rec_id}&field={image_field_name}'

    def _get_rec_id_with_image(self, image_field_name: str) -> int or bool:
        """Default Logo and background image could be stored in the res.config.settings or css
        :returns: self.id or default id or False where image will be first found(if false css should be used)"""
        self.ensure_one()
        if self[image_field_name]:
            return self.id

        default_rec_id = self.env['ir.config_parameter'].sudo().get_param('regency.fallback_partner_id')
        if default_rec_id:
            default_rec_id = self.browse(int(default_rec_id))
            if default_rec_id[image_field_name]:
                return default_rec_id.id
        return False
