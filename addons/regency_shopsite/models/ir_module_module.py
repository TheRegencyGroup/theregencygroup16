from json import dumps

from markupsafe import Markup
from odoo import models, api


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.model
    def _fe_template_versions(self):
        fe = self.sudo().search([('name', '=', 'fe_owl_base')], limit=1)
        dependencies = self.env['ir.module.module.dependency'].sudo().search([('depend_id', "in", [fe.id])]).mapped(
            'module_id')
        return Markup(dumps({x.name: x.latest_version for x in dependencies}))
