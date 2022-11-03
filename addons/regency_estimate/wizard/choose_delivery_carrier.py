from odoo import fields, models


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    manual_price = fields.Float(string='Manual Cost')

    def button_confirm(self):
        if self.delivery_type == 'other':
            self.with_context(manual_price=self.manual_price)._get_shipment_rate()
        super(ChooseDeliveryCarrier, self).button_confirm()