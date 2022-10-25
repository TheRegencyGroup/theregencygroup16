from odoo import fields, models, api, _


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('other', 'Other')], ondelete={
        'other': lambda records: records.write({'delivery_type': 'fixed', 'fixed_price': 0})})


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    def button_confirm(self):
        if self.manual_price:
            self.order_id.set_delivery_line(self.carrier_id, self.manual_price)
        else:
            self.order_id.set_delivery_line(self.carrier_id, self.delivery_price)
        self.order_id.write({
            'recompute_delivery_price': False,
            'delivery_message': self.delivery_message,
        })
