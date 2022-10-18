import logging
from ast import literal_eval

import jwt

from odoo import http
from odoo.addons.web.controllers import main
from odoo.addons.web.controllers.main import ensure_db
from odoo.http import request
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound

DEFAULT_ALG = "HS512"

_logger = logging.getLogger(__name__)


class TokenLogin(main.Home):
    @http.route("/token_login", type='http', auth="none")
    def token_login(self, token, redirect="", db=""):
        ensure_db()
        get_param = request.env['ir.config_parameter'].sudo().get_param
        try:
            is_enabled = literal_eval(get_param('token_login.enable', "0"))
        except Exception:
            is_enabled = False
        if not is_enabled:
            raise NotFound()
        try:
            header = jwt.get_unverified_header(token)
        except Exception:
            _logger.warning(f"Token login: Invalid token, {token}")
            raise BadRequest("Invalid token")
        alg = get_param('token_login.algorithm', DEFAULT_ALG)
        if header.get('alg') != alg:
            _logger.warning(f"Token login: Invalid algorithm, {header}, {token}")
            raise BadRequest(f"Invalid algorithm, {alg} expected")
        secret = get_param('token_login.secret')
        if not secret:
            _logger.error("Token login: secret is not set")
            raise InternalServerError("Token login is misconfigured")
        try:
            payload = jwt.decode(
                token,
                algorithms=[alg],
                key=secret,
                options={
                    'require': ["exp", "login"],
                    'verify_exp': True,
                },
            )
        except Exception:
            _logger.warning(f"Token login: Invalid or expired token, {header}, {token}")
            raise BadRequest("Invalid or expired token")
        uid = self.authenticate(db or request.session.db, payload['login'])
        _logger.info(f"Token login: {payload['login']}")
        return request.redirect(self._login_redirect(uid, redirect=redirect))

    @classmethod
    def authenticate(cls, db, login):
        session = request.session
        uid = request.env['res.users']._auto_login(db, login)
        session.pre_uid = uid
        session.rotate = True
        session.db = db
        session.login = login
        request.disable_db = False
        user = request.env['res.users'].browse(uid)
        if not user._mfa_url():
            session.finalize()
        return uid
