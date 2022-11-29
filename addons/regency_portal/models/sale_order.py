from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _has_to_be_signed(self, include_draft=False):
        team_shopsite_department_id = self.env.ref('regency_shopsite.team_shopsite_department')
        return super()._has_to_be_signed(include_draft=include_draft) and \
            (self.state != 'sent' if self.team_id.id == team_shopsite_department_id.id else True)
