from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('other', 'Other')], ondelete={
        'other': lambda records: records.write({'delivery_type': 'fixed', 'fixed_price': 0})})
    fixed_margin = fields.Float(string='Fixed Margin', default=0.0)

    def rate_shipment(self, order):
        res = super(DeliveryCarrier, self).rate_shipment(order)
        # apply fixed margin on computed price
        res['price'] = res['price'] + self.fixed_margin
        res['carrier_price'] = res['price']
        return res

    def other_rate_shipment(self, order):
        price = self.env.context.get('manual_price', 0)
        return {'success': True,
                'price': price,
                'error_message': False,
                'warning_message': False}
