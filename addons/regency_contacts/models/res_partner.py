from odoo import api, fields, models

from .const import ENTITY_SELECTION


class ResPartner(models.Model):
    _inherit = 'res.partner'

    association_ids = fields.Many2many('customer.association', relation="customer_association_res_partner_rel",
                                       column1='res_partner_id', column2='customer_association_id')
    association_partner_ids = fields.One2many('res.partner', compute='_compute_association_partner_ids')
    contact_type = fields.Selection([
        ('customer', 'Customer'),
        ('vendor', 'Vendor')
    ])
    vendor_type = fields.Selection([('overseas', 'Overseas'), ('domestic', 'Domestic')])
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

    entity_type = fields.Selection(selection=ENTITY_SELECTION)

    def _compute_association_partner_ids(self):
        for partner in self:
            partner.association_partner_ids = partner.association_ids.mapped('right_partner_id')

    def write(self, vals):
        prev_association_ids = self.association_ids
        res = super().write(vals)
        prev_association_ids._delete_incomplete()
        return res
