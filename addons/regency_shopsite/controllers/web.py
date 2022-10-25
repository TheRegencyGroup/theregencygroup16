from odoo.addons.portal.controllers.web import Home
from odoo.addons.web.controllers.utils import is_user_internal
from odoo import http
from odoo.http import request


class RegencyHome(Home):

    @http.route()
    def index(self, *args, **kw):
        return request.redirect_query('/shop', query=request.params)

    def _login_redirect(self, uid, redirect=None):
        if not redirect and not is_user_internal(uid):
            redirect = '/shop'
        return super()._login_redirect(uid, redirect=redirect)
