from typing import Tuple, List

from odoo import api, fields, models


class CustomerAssociation(models.Model):
    _name = 'customer.association'
    _description = 'Customer association'

    association_name = fields.Selection(selection=lambda x: x.env['association.type']._association_types_selection(),
                                        string='Name', required=True)

    association_type_id = fields.Many2one('association.type', compute='_compute_association_type', store=True,
                                          compute_sudo=True)
    left_partner_id = fields.Many2one('res.partner')
    right_partner_id = fields.Many2one('res.partner', required=True)

    @api.depends('association_name')
    def _compute_association_type(self):
        for customer_asc in self:
            customer_asc.association_type_id = self.env['association.type'].search(
                ['|', ('left_tech_name', '=', customer_asc.association_name),
                 ('right_tech_name', '=', customer_asc.association_name)])


class AssociationType(models.Model):
    _name = 'association.type'
    _description = 'Association type'

    left_tech_name = fields.Char()
    right_tech_name = fields.Char()
    left_to_right_name = fields.Char()
    right_to_left_name = fields.Char()

    @api.model
    def _association_types_selection(self) -> List[Tuple[str, str]]:
        association_names = self.search([])
        data = []
        for asc_type in association_names:
            data.append((asc_type.left_tech_name, asc_type.left_to_right_name))
            data.append((asc_type.right_tech_name, asc_type.right_to_left_name))
        return data
