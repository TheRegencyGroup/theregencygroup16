from odoo import fields, models, api


class PortalLinkWizard(models.TransientModel):
    _name = 'portal.link.wizard'
    _description = "Generate Portal Link"

    name = fields.Char()