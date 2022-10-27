from odoo.http import Request, request
old_render = Request.render


def render(self, template, qcontext=None, lazy=True, **kw):
    response = old_render(self, template, qcontext, lazy, **kw)
    if request.session.login and request.httprequest.path != '/web':
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response


Request.render = render
