from odoo import fields, models


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    manual_price = fields.Float(string='Manual Cost')

    def _get_shipment_rate(self):
        """
        overridden to correct work with new delivery_type - 'other'
        """
        # start customization
        if self.delivery_type == 'other':
            return {}
        # end customization
        vals = self.carrier_id.rate_shipment(self.order_id)
        if vals.get('success'):
            self.write({
                'delivery_message': vals.get('warning_message', False),
                'delivery_price': vals['price'],
                'display_price': vals['carrier_price']
            })
            return {}
        return {'error_message': vals['error_message']}

    def button_confirm(self):
        """
        overridden to set manually entered price
        """
        # "self.manual_price if self.manual_price else self.delivery_price" instead of "self.delivery_price":
        self.order_id.set_delivery_line(self.carrier_id,
                                        self.manual_price if self.manual_price else self.delivery_price)
        # end customization
        self.order_id.write({
            'recompute_delivery_price': False,
            'delivery_message': self.delivery_message,
        })
