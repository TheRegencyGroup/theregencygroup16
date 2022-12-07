from odoo import api, fields, models, _, Command



class Invoice(models.Model):
    _inherit = 'account.move'

    consumption_agreement_id = fields.Many2one('consumption.agreement')