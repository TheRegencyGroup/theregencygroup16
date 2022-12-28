from odoo import _
from odoo.addons.delivery_dhl.models.dhl_request import DHLProvider


def new_check_required_value(self, carrier, recipient, shipper, order=False, picking=False):
    """Copied from DHLProvider class to add custom logic"""

    carrier = carrier.sudo()
    recipient_required_field = ['city', 'zip', 'country_id']
    if not carrier.dhl_SiteID:
        return _("DHL Site ID is missing, please modify your delivery method settings.")
    if not carrier.dhl_password:
        return _("DHL password is missing, please modify your delivery method settings.")
    if not carrier.dhl_account_number:
        return _("DHL account number is missing, please modify your delivery method settings.")

    # The street isn't required if we compute the rate with a partial delivery address in the
    # express checkout flow.
    if not recipient.street and not recipient.street2 and not recipient._context.get(
            'express_checkout_partial_delivery_address', False
    ):
        recipient_required_field.append('street')
    res = [field for field in recipient_required_field if not recipient[field]]
    if res:
        return _("The address of the customer is missing or wrong (Missing field(s) :\n %s)") % ", ".join(res).replace(
            "_id", "")

    shipper_required_field = ['city', 'zip', 'phone', 'country_id']
    if not shipper.street and not shipper.street2:
        shipper_required_field.append('street')

    res = [field for field in shipper_required_field if not shipper[field]]
    if res:
        return _("The address of your company warehouse is missing or wrong (Missing field(s) :\n %s)") % ", ".join(
            res).replace("_id", "")

    if order:
        if not order.order_line:
            return _("Please provide at least one item to ship.")
        # TODO: check if package has weight
        # error_lines = order.order_line.filtered(lambda
        #                                             line: not line.product_id.weight and not line.is_delivery and line.product_id.type != 'service' and not line.display_type)
        # if error_lines:
        #     return _(
        #         "The estimated shipping price cannot be computed because the weight is missing for the following product(s): \n %s") % ", ".join(
        #         error_lines.product_id.mapped('name'))
    return False

DHLProvider.check_required_value = new_check_required_value