from odoo import fields, models


class CustomerAssociation(models.Model):
    _name = 'customer.association'

    association_type = fields.Many2one('association.type')
    left_partner_id = fields.Many2one('res.partner')
    right_partner_id = fields.Many2one('res.partner')

    def unlink(self):
        """
        Find related customer association and unlink it.
        :return:
        """
        # TODO: find possibility trigger unlink from association tab
        res = super().unlink()
        return res


class AssociationType(models.Model):
    _name = 'association.type'

    name = fields.Char()
    left_to_right_name = fields.Char()
    right_to_left_name = fields.Char()


# res_partner m2m to association customer association