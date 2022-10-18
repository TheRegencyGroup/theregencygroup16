from odoo import fields, models, api, _


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    contacted = fields.Boolean(compute="_compute_contacted", store=True)