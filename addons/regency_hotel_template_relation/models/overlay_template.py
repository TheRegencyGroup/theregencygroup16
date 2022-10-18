from odoo import fields, models


class OverlayTemplate(models.Model):
    _inherit = 'overlay.template'

    hotel_ids = fields.Many2many('res.partner', 'hotel_template_rel', 'template_id', 'hotel_id', string='Hotels',
                                 domain=[('company_type', '=', 'company'), ('contact_type', '=', 'customer')])
