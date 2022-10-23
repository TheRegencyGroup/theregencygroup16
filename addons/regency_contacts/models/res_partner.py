from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    association_ids = fields.Many2many('customer.association', 'contact_association_rel', 'partner_id',
                                       'association_id', compute='_compute_association_ids',
                                       inverse='_inverse_association_ids',
                                       precompute=True, store=True)
    contact_type = fields.Selection([
        ('customer', 'Customer'),
        ('vendor', 'Vendor')
    ])
    cc_invoice = fields.Boolean(string='CC on Invoice')
    default_shipping_percent = fields.Float()
    on_hold = fields.Boolean()
    dba_name = fields.Char()
    phone_extra = fields.Char()
    mobile_extra = fields.Char()
    other_phone = fields.Char()
    other_phone_extra = fields.Char()
    hotel_contact_ids = fields.Many2many('res.partner', 'contact_hotel_rel', 'contact_id', 'hotel_id',
                                 domain=[('is_company', '=', False)])
    hotel_ids = fields.Many2many('res.partner', 'contact_hotel_rel', 'hotel_id', 'contact_id',
                                domain=[('is_company', '=', True), ('contact_type', '=', 'customer')])

    @api.depends('association_ids')
    def _compute_association_ids(self):
        for partner in self:
            partner.association_ids = partner.association_ids

    # @api.onchange('association_ids')
    def _inverse_association_ids(self):
        for partner in self:
            if self.env.context.get('stop_inverse'):
                break
            partner.association_ids = partner.association_ids
            right_asct_type = self.env['association.type'].search(
                [('right_to_left_name', '=', partner.association_ids.association_type.left_to_right_name)])
            partner.association_ids.right_partner_id.with_context({'stop_inverse': True}).association_ids = [
                (0, 0, {'left_partner_id': partner.association_ids.right_partner_id.id, 'right_partner_id': partner.id,
                        'association_type': right_asct_type.id})
            ]
