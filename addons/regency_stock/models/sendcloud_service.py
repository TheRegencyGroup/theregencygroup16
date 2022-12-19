import math
from odoo import fields, _
from odoo.exceptions import UserError

from odoo.addons.delivery_sendcloud.models.sendcloud_service import SendCloud


class SendCloudExt(SendCloud):

    def get_shipping_rate(self, carrier, order=None, picking=None, parcel=None):
        """
        Overridden
        check for product weight removed
        """
        if order:
            to_country = order.partner_shipping_id.country_id.code
            from_country = order.warehouse_id.partner_id.country_id.code
            error_lines = order.order_line.filtered(lambda line: not line.is_delivery and line.product_id.type != 'service' and not line.display_type)
            if error_lines:
                raise UserError(_("The estimated shipping price cannot be computed because the weight is missing for the following product(s): \n %s") % ", ".join(error_lines.product_id.mapped('name')))
            packages = carrier._get_packages_from_order(order, carrier.sendcloud_default_package_type_id)
            total_weight = sum(pack.weight for pack in packages)
        elif picking:
            to_country = picking.destination_country_code
            from_country = picking.location_id.warehouse_id.partner_id.country_id.code
            total_weight = float(parcel['weight'])
        else:
            raise UserError(_('No picking or order provided'))
        if not to_country or not from_country:
            raise UserError(_('Make sure country codes are set in partner country and warehouse country'))
        # Get Shipping Id
        shipping_id = parcel.get('shipment', {}).get('id') if parcel else carrier.sendcloud_shipping_id.sendcloud_id
        if not shipping_id:
            carrier.raise_redirect_message()
        # if the weight is greater than max weight and source is order (initial estimate)
        # split the weight into packages instead of returning no price / offer
        packages_no = 0
        total_weight = float(carrier.sendcloud_convert_weight(total_weight))
        if total_weight > carrier.sendcloud_shipping_id.max_weight and order:
            packages_no = math.ceil(total_weight / carrier.sendcloud_shipping_id.max_weight)
            # max weight from sendcloud is 1 gram extra (eg. if max allowed weight = 3kg, sendcloud_shipping_id.max_weight = 3.001 kg)
            total_weight = carrier.sendcloud_shipping_id.max_weight - 0.001
        # Convert Weight to sendcloud weight (grams)
        # this endpoint expects integer for weight so to prevent loss in weight we use grams
        total_weight = int(carrier.sendcloud_convert_weight(total_weight, grams=True))
        params = {
            'shipping_method_id': shipping_id,
            'to_country': to_country,
            'from_country': from_country,
            'weight': total_weight,
            'weight_unit': 'gram'
        }
        price = self._send_request('shipping-price', params=params)

        if not price:
            raise UserError(_('The selected shipping method does not ship from %s to %s', from_country, to_country))
        # the API response is an Array of 1 dict with price and currency (usually EUR)
        price = price[0]
        currency = price.get('currency')
        price = price.get('price')
        # shipping id 8 is a test shipping and does not provide a price, but we still need the flow to continue
        # the check is done after the request since in the future if price is actually returned it will be passed correctly
        if shipping_id == 8 and price is None:
            return 0.0, 0
        if price is None:
            raise UserError(_('There is no rate available for this order with the selected shipping method'))
        price = float(price)
        if packages_no:
            price *= packages_no
        currency_id = carrier.env['res.currency'].with_context(active_test=False).search([('name', '=', currency)])
        if not currency_id:
            raise UserError(_('Could not find currency %s', currency))

        to_currency_id = order.currency_id if order else picking.sale_id.currency_id
        converted_price = currency_id._convert(price, to_currency_id, carrier.env.company, fields.Date.context_today(carrier))
        return converted_price, packages_no
