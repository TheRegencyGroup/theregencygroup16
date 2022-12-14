# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if defaults.get('move_type') == 'in_invoice':
            defaults.update(invoice_date=fields.Datetime.now())
        return defaults

    @api.model_create_multi
    def create(self, vals_list):
        moves = super(AccountMove, self).create(vals_list)
        for move in moves:
            if move.move_type == 'in_invoice':
                sequence = 10
                for line in move.invoice_line_ids:
                    sequence += 1
                    line.sequence = sequence
                    fee_value_ids = line.purchase_line_id.fee_value_ids
                    if fee_value_ids:
                        sequence += 1
                        line.create({'display_type': 'line_note',
                                     'name': f'Additional Fees for {line.product_id.name}:',
                                     'move_id': line.move_id.id,
                                     'purchase_line_id': line.purchase_line_id.id,
                                     'sequence': sequence})
                        for fee in fee_value_ids:
                            sequence += 1
                            line.create({'product_id': fee.fee_type_id.product_id.id,
                                         'price_unit': fee.value,
                                         'move_id': line.move_id.id,
                                         'purchase_line_id': line.purchase_line_id.id,
                                         'sequence': sequence})
        return moves
