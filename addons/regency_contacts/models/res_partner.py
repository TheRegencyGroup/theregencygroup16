from odoo import fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_association_ids = fields.One2many('customer.association', 'related_partner_id')
    parent_ids = fields.One2many('res.partner', compute='_compute_parent_ids')
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

    def _compute_parent_ids(self):
        for partner in self:
            partner.parent_ids = partner.customer_association_ids.mapped('parent_partner_id')
            
    def unlink(self):
        customer_association_ids = self.env['customer.association'].search([('parent_partner_id', 'in', self.ids)])
        if bool(customer_association_ids):
            raise UserError("Restrict to delete. Contact(s): %s set as parent contact." % ', '.join(
                customer_association_ids.mapped('parent_partner_id.name')))

        return super(ResPartner, self).unlink()
