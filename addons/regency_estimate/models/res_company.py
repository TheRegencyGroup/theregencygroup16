from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    estimate_manager_id = fields.Many2one('res.users', string="Estimate manager")
