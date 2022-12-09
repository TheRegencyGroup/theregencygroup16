from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    estimate_manager_id = fields.Many2one('res.users', string='Estimate manager',
                                          related='company_id.estimate_manager_id', readonly=False)
