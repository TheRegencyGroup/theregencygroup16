from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):

    def _prepare_orders_domain(self, partner):
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sent', 'sale', 'done'])
        ]
