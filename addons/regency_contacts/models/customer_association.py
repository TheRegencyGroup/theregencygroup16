from odoo import fields, models, api, Command

from .const import ENTITY_SELECTION


class CustomerAssociation(models.Model):
    _name = 'customer.association'
    _description = 'Customer association'

    association_type_id = fields.Many2one('association.type')
    partner_ids = fields.Many2many('res.partner', relation="customer_association_res_partner_rel",
                                   column1='customer_association_id', column2='res_partner_id')
    left_partner_id = fields.Many2one('res.partner', store=True, compute_sudo=True, compute="_compute_partners",
                                      inverse="_inverse_left")
    right_partner_id = fields.Many2one('res.partner', store=True, compute_sudo=True, compute="_compute_partners",
                                       inverse="_inverse_right")
    display_partner_id = fields.Many2one('res.partner', compute="_compute_display_values")
    display_assoc_title = fields.Char(compute="_compute_display_values")

    @api.depends('right_partner_id', 'association_type_id', 'partner_ids')
    @api.depends_context('default_left_partner_id')
    def _compute_display_values(self):
        current_partner_id = self.env.context.get('default_left_partner_id', self.left_partner_id)
        for entry in self:
            show_partner_id = entry.partner_ids.filtered(lambda x: x.id != current_partner_id)
            entry.display_partner_id = show_partner_id[0] if show_partner_id else False
            if entry.association_type_id and show_partner_id:
                entry.display_assoc_title = entry.association_type_id.left_to_right_name if \
                    show_partner_id[0] != entry.left_partner_id else entry.association_type_id.right_to_left_name
            else:
                entry.display_assoc_title = ""

    @api.onchange('left_partner_id')
    def _onchange_left_partner_id(self):
        return {
            'domain': {
                'association_type_id': [
                    "|",
                    ('left_tech_name', "=", self.left_partner_id.entity_type if self.left_partner_id else False),
                    ('right_tech_name', "=", self.left_partner_id.entity_type if self.left_partner_id else False),
                ]
            }
        }

    @api.onchange('association_type_id')
    def _onchange_association_type_id(self):
        if not self.left_partner_id:
            return {}
        assoc_id = self.association_type_id
        opposite_name = assoc_id.right_tech_name if assoc_id.left_tech_name == self.left_partner_id.entity_type else \
            assoc_id.left_tech_name
        return {
            'domain': {
                'right_partner_id': [('entity_type', "=", opposite_name)],
            }
        }

    def _inverse_left(self):
        for entry in self:
            new_ids = set([])
            if entry.left_partner_id:
                new_ids.add(entry.left_partner_id.id)
            right_ids = entry.partner_ids.filtered(lambda x: x.entity_type == entry.association_type_id.right_tech_name)
            if right_ids:
                new_ids.add(right_ids[0].id)
            elif entry.right_partner_id:
                new_ids.add(entry.right_partner_id.id)
            entry.partner_ids = [Command.set(list(new_ids))]

    def _inverse_right(self):
        for entry in self:
            new_ids = set([])
            left_ids = entry.partner_ids.filtered(lambda x: x.entity_type == entry.association_type_id.left_tech_name)
            if left_ids:
                new_ids.add(left_ids[0].id)
            elif entry.left_partner_id:
                new_ids.add(entry.left_partner_id.id)
            if entry.right_partner_id:
                new_ids.add(entry.right_partner_id.id)
            entry.partner_ids = [Command.set(list(new_ids))]

    @api.depends('partner_ids')
    def _compute_partners(self):
        for entry in self:
            left_ids = entry.partner_ids.filtered(lambda x: x.entity_type == entry.association_type_id.left_tech_name)
            entry.left_partner_id = left_ids[0] if left_ids else False
            right_ids = entry.partner_ids.filtered(lambda x: x.entity_type == entry.association_type_id.right_tech_name)
            entry.right_partner_id = right_ids[0] if right_ids else False

    def _delete_incomplete(self):
        to_delete = self.env[self._name]
        for entry in self:
            if len(entry.partner_ids.ids) < 2:
                to_delete += entry
        to_delete.unlink()


class AssociationType(models.Model):
    _name = 'association.type'
    _description = 'Association type'

    name = fields.Char(compute="_compute_name")
    left_tech_name = fields.Selection(selection=ENTITY_SELECTION)
    right_tech_name = fields.Selection(selection=ENTITY_SELECTION)
    left_to_right_name = fields.Char()
    right_to_left_name = fields.Char()

    @api.depends_context('current_partner_id')
    def _compute_name(self):
        current_partner_id = self.env.context.get('current_partner_id')
        current_partner_id = self.env['res.partner'].browse(current_partner_id)
        for entry in self:
            if not current_partner_id:
                current_type = entry.left_tech_name
            else:
                current_type = current_partner_id.entity_type
            entry.name = entry.left_to_right_name if current_type == entry.left_tech_name else entry.right_to_left_name
