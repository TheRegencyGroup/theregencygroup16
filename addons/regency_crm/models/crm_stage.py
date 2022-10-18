from odoo import fields, models, api


class CRMStage(models.Model):
    _inherit = 'crm.stage'

    generate_estimate = fields.Boolean(default=False)