from odoo import fields, models


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    manual_price = fields.Float(string='Manual Cost')

    def _get_shipment_rate(self):
        if self.delivery_type == 'other':
            return {}
        vals = self.carrier_id.rate_shipment(self.order_id)
        if vals.get('success'):
            self.delivery_message = vals.get('warning_message', False)
            self.delivery_price = vals['price']
            self.display_price = vals['carrier_price']
            return {}
        return {'error_message': vals['error_message']}
