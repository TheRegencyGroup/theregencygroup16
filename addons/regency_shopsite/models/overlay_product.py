from odoo import api, Command, fields, models


class OverlayProduct(models.Model):
    _name = 'overlay.product'
    _description = 'Overlay product'

    overlay_template_id = fields.Many2one('overlay.template')
    product_tmpl_id = fields.Many2one(string="Product template", related='overlay_template_id.product_template_id',
                                      store=True)
    hotel_ids = fields.Many2many(related='overlay_template_id.hotel_ids')
    name = fields.Char()
    product_id = fields.Many2one('product.product')
    customize_attribute_value_id = fields.Many2one('product.attribute.value',
                                                   compute='_compute_customize_attribute_value_id',
                                                   compute_sudo=True)
    customize_attribute_value_ids = fields.One2many('product.attribute.value', 'overlay_product_id')
    product_template_attribute_value_ids = fields.Many2many('product.template.attribute.value')
    overlay_product_image_ids = fields.One2many('overlay.product.image', 'overlay_product_id', readonly=True)
    overlay_product_area_image_ids = fields.One2many('overlay.product.area.image', 'overlay_product_id', readonly=True)
    area_list_json = fields.Char(readonly=True)
    last_updated_date = fields.Datetime(readonly=True, default=lambda self: self._compute_last_update_date())
    updated_by = fields.Many2one('res.partner', readonly=True, default=lambda self: self._compute_updated_by())

    @api.depends('customize_attribute_value_ids')
    def _compute_customize_attribute_value_id(self):
        for rec in self:
            if len(rec.customize_attribute_value_ids) > 0:
                rec.customize_attribute_value_id = rec.customize_attribute_value_ids[0]
            else:
                rec.customize_attribute_value_id = False

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        res._create_attribute_value()
        return res

    def write(self, vals):
        vals.update({'updated_by': self._compute_updated_by(),
                     'last_updated_date': self._compute_last_update_date()})
        res = super(OverlayProduct, self).write(vals)
        return res

    def _create_attribute_value(self):
        customization_attr = self.env.ref('regency_shopsite.customization_attribute')
        attr_value_model = self.env['product.attribute.value']
        attr_line_model = self.env['product.template.attribute.line']
        for entry in self:
            pav = attr_value_model.create({
                'name': f"{entry.id}",
                'attribute_id': customization_attr.id,
                'overlay_product_id': entry.id,
                'sequence': 1,
            })
            ptal = entry.product_tmpl_id.attribute_line_ids.filtered(lambda f: f.attribute_id == customization_attr)
            if ptal:
                ptal.write({'value_ids': [Command.link(pav.id)]})
            else:
                attr_line_model.create({
                    'product_tmpl_id': entry.product_tmpl_id.id,
                    'attribute_id': customization_attr.id,
                    'value_ids': [Command.link(pav.id)]
                })

    def _preview_image_url(self):
        self.ensure_one()
        if self.overlay_product_image_ids:
            image_model = self.overlay_product_image_ids._name
            image_id = self.overlay_product_image_ids[0].id
            image_field = 'image'
        else:
            image_id = self.product_tmpl_id.id
            image_model = self.product_tmpl_id._name
            image_field = 'image_512'
        return f'/web/image?model={image_model}&id={image_id}&field={image_field}'

    def _get_last_updated_str(self) -> str:
        self.ensure_one()
        date = self.last_updated_date
        user_name = self.updated_by.name
        if date or user_name:
            date_str = fields.Datetime.context_timestamp(self, date).strftime(' %b %d, %Y,') if date else ''
            name_str = f'by {user_name}' if user_name else ''
            return f'Updated{date_str} {name_str}'.strip(' ,')
        else:
            return ''
        
    def _compute_last_update_date(self):
        is_updated_by_partner = self._compute_updated_by()
        if is_updated_by_partner:
            return self.write_date or fields.Datetime.now()  # 'Datetime.now' used for default on creation
        else:
            return False

    @api.model
    def _compute_updated_by(self) -> object:
        user = self.env['res.users'].browse(self._context.get('uid'))
        return user.partner_id if user else self.env['res.partner']
