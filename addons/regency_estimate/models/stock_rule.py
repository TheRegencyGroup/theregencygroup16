# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _make_po_get_domain(self, company_id, values, partner):
        """ If RFQ has assigned Purchase Requisition(requisition_id) it should not collect other demands. """
        domain = super(StockRule, self)._make_po_get_domain(company_id, values, partner)
        domain += (('requisition_id', '=', False),)
        return domain
