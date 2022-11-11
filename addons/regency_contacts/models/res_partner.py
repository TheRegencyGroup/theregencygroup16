from odoo import api, fields, models, Command

from .const import ENTITY_SELECTION, HOTEL


class ResPartner(models.Model):
    _inherit = 'res.partner'

    association_ids = fields.Many2many('customer.association', relation="customer_association_res_partner_rel",
                                       column1='res_partner_id', column2='customer_association_id')
    association_partner_ids = fields.One2many('res.partner', compute='_compute_association_partner_ids',
                                              compute_sudo=True)
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
    hotel_ids = fields.Many2many('res.partner', compute="_compute_hotel_ids", compute_sudo=True)
    entity_type = fields.Selection(selection=ENTITY_SELECTION)

    @api.depends('association_partner_ids')
    def _compute_hotel_ids(self):
        for entry in self:
            entry.hotel_ids = [
                Command.set(entry.association_partner_ids.filtered(lambda x: x.entity_type == HOTEL).ids),
            ]

    @api.depends('association_ids')
    def _compute_association_partner_ids(self):
        for partner in self:
            partner.association_partner_ids = partner.association_ids.mapped('partner_ids')

    def write(self, vals):
        prev_association_ids = self.association_ids
        res = super().write(vals)
        prev_association_ids._delete_incomplete()
        return res
