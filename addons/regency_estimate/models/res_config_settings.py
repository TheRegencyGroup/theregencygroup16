from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    estimate_manager_id = fields.Many2one('res.users', string='Estimate manager',
                                          config_parameter='regency.estimate_manager_id',
                                          related='company_id.estimate_manager_id', readonly=False)
