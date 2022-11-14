# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        res.update({'pricesheet_vendor_id': self.sale_line_id.pricesheet_line_id.partner_id,
                    'pricesheet_vendor_price': self.sale_line_id.pricesheet_line_id.vendor_price,
                    'sale_line_id': self.sale_line_id.id})
        return res
