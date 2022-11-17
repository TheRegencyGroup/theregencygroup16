from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _post(self, soft=True):
        for invoice in self.filtered(lambda move: move.is_invoice(include_receipts=True)):
            if invoice.is_purchase_document(include_receipts=True):
                invoice.invoice_date = fields.Date.context_today(self)
        return super()._post()
