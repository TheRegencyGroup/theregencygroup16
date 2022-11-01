from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fallback_partner_id = fields.Many2one('res.partner', string='Fallback Partner',
                                          config_parameter='regency.fallback_partner_id')