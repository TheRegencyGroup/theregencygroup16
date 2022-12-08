from odoo import fields, models, _


class PreviousPricesWizard(models.TransientModel):
    _name = 'purchase.order.cancel.wizard'
    _description = 'Cancel PO Wizard'

    text = fields.Text(readonly=True, default='Are you sure you want to cancel the Purchase order?'
                                              'If yes, please, provide your reason for cancellation:')
    cancellation_reason = fields.Char(required=True)

    def cancel(self):
        order = self.env['purchase.order'].browse(self.env.context.get('active_id'))
        order.write({'cancellation_reason': self.cancellation_reason})
        order.button_cancel()
        order.message_post(body=_('PO was cancelled due to the reason: %s' % order.cancellation_reason))

