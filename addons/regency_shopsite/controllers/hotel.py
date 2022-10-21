from odoo import http
from odoo.http import request
from werkzeug.exceptions import NotFound


class Hotel(http.Controller):
    @http.route("/user/active_hotel", methods=["POST"], website=True, type="json")
    def _hotel_active(self, hotel):
        hotel_id = request.env['res.partner'].browse(hotel)
        if not hotel_id:
            raise NotFound
        request.session['selected_hotel'] = hotel
        return {
            'active_hotel_id': hotel,
        }
