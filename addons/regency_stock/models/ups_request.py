from odoo import _
from odoo.addons.delivery_ups.models.ups_request import UPSRequest, UPS_ERROR_MAP


def new_check_required_value(self, shipper, ship_from, ship_to, order=False, picking=False):
    required_field = {'city': 'City', 'country_id': 'Country', 'phone': 'Phone'}
    # Check required field for shipper
    res = [required_field[field] for field in required_field if not shipper[field]]
    if shipper.country_id.code in ('US', 'CA', 'IE') and not shipper.state_id.code:
        res.append('State')
    if not shipper.street and not shipper.street2:
        res.append('Street')
    if shipper.country_id.code != 'HK' and not shipper.zip:
        res.append('ZIP code')
    if res:
        return _("The address of your company is missing or wrong.\n(Missing field(s) : %s)", ",".join(res))
    if len(self._clean_phone_number(shipper.phone)) < 10:
        return str(UPS_ERROR_MAP.get('120115'))
    # Check required field for warehouse address
    res = [required_field[field] for field in required_field if not ship_from[field]]
    if ship_from.country_id.code in ('US', 'CA', 'IE') and not ship_from.state_id.code:
        res.append('State')
    if not ship_from.street and not ship_from.street2:
        res.append('Street')
    if ship_from.country_id.code != 'HK' and not ship_from.zip:
        res.append('ZIP code')
    if res:
        return _("The address of your warehouse is missing or wrong.\n(Missing field(s) : %s)", ",".join(res))
    if len(self._clean_phone_number(ship_from.phone)) < 10:
        return str(UPS_ERROR_MAP.get('120313'))
    # Check required field for recipient address
    res = [required_field[field] for field in required_field if field != 'phone' and not ship_to[field]]
    if ship_to.country_id.code in ('US', 'CA', 'IE') and not ship_to.state_id.code:
        res.append('State')
    # The street isn't required if we compute the rate with a partial delivery address in the
    # express checkout flow.
    if not ship_to.street and not ship_to.street2 and not ship_to._context.get(
            'express_checkout_partial_delivery_address', False
    ):
        res.append('Street')
    if ship_to.country_id.code != 'HK' and not ship_to.zip:
        res.append('ZIP code')
    if len(ship_to.street or '') > 35 or len(ship_to.street2 or '') > 35:
        return _(
            "UPS address lines can only contain a maximum of 35 characters. You can split the contacts addresses on multiple lines to try to avoid this limitation.")
    if picking and not order:
        order = picking.sale_id
    phone = ship_to.mobile or ship_to.phone
    if order and not phone:
        phone = order.partner_id.mobile or order.partner_id.phone
    if order:
        if not order.order_line:
            return _("Please provide at least one item to ship.")
        #TODO: check if weight is set in package

        # error_lines = order.order_line.filtered(lambda
        #                                             line: not line.product_id.weight and not line.is_delivery and line.product_id.type != 'service' and not line.display_type)
        # if error_lines:
        #     return _(
        #         "The estimated shipping price cannot be computed because the weight is missing for the following product(s): \n %s") % ", ".join(
        #         error_lines.product_id.mapped('name'))
    if picking:
        for ml in picking.move_line_ids.filtered(lambda ml: not ml.result_package_id and not ml.product_id.weight):
            return _("The delivery cannot be done because the weight of your product is missing.")
        packages_without_weight = picking.move_line_ids.mapped('result_package_id').filtered(
            lambda p: not p.shipping_weight)
        if packages_without_weight:
            return _('Packages %s do not have a positive shipping weight.',
                     ', '.join(packages_without_weight.mapped('display_name')))
    # The phone isn't required if we compute the rate with a partial delivery address in the
    # express checkout flow.
    if not phone and not ship_to._context.get(
            'express_checkout_partial_delivery_address', False
    ):
        res.append('Phone')
    if res:
        return _("The recipient address is missing or wrong.\n(Missing field(s) : %s)", ",".join(res))
    # The phone isn't required if we compute the rate with a partial delivery address in the
    # express checkout flow.
    if not ship_to._context.get(
            'express_checkout_partial_delivery_address', False
    ) and len(self._clean_phone_number(phone)) < 10:
        return str(UPS_ERROR_MAP.get('120213'))
    return False


UPSRequest.check_required_value = new_check_required_value