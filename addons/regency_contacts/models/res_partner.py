from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    association_ids = fields.Many2many('customer.association', 'contact_association_rel', 'partner_id',
                                       'association_id', compute='_compute_association_ids',
                                       inverse='_inverse_association_ids',
                                       precompute=True, store=True)
    association_partner_ids = fields.One2many('res.partner', compute='_compute_association_partner_ids')
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

    def _inverse_association_ids(self):
        for partner in self:
            if self.env.context.get('stop_inverse'):
                break
            partner.association_ids = partner.association_ids

            # Link left partner to right partner
            for association in partner.association_ids:
                asct_type = self.env['association.type'].search(
                    ['|', ('left_tech_name', '=', association.association_name),
                     ('right_tech_name', '=', association.association_name)])
                another_side = asct_type.right_tech_name if asct_type.left_tech_name == association.association_name else asct_type.left_tech_name
                right_partner_association = association.right_partner_id.association_ids.filtered(
                    lambda f: f.right_partner_id == partner)
                if right_partner_association:
                    if another_side != right_partner_association.association_name:
                        right_partner_association.association_name = another_side
                        continue
                association.right_partner_id.with_context({'stop_inverse': True}).association_ids = [
                    (0, 0, {'left_partner_id': association.right_partner_id.id, 'right_partner_id': partner.id,
                            'association_name': another_side})
                ]

    def _compute_association_partner_ids(self):
        for partner in self:
            partner.association_partner_ids = partner.association_ids.mapped('right_partner_id')

    def write(self, vals):
        prev_association_ids = self.association_ids
        res = super().write(vals)
        self._unlink_associations(prev_association_ids)
        return res

    def _unlink_associations(self, prev_association_ids):
        associations_to_delete = prev_association_ids - self.association_ids
        associations_from_right_side_to_delete = self.env['customer.association']
        for association in associations_to_delete:
            asct_type = self.env['association.type'].search(
                ['|', ('left_tech_name', '=', association.association_name),
                 ('right_tech_name', '=', association.association_name)])
            another_side = asct_type.right_tech_name if asct_type.left_tech_name == association.association_name else asct_type.left_tech_name
            related_association_id = self.env['customer.association'].search(
                [('right_partner_id', '=', self.id), ('association_name', '=', another_side)])
            if related_association_id:
                associations_from_right_side_to_delete += related_association_id
        (associations_to_delete + associations_from_right_side_to_delete).unlink()
