from odoo import fields, models, api, _


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    contacted = fields.Boolean(compute="_compute_contacted", store=True)

    @api.depends('message_ids')
    def _compute_contacted(self):
        for rec in self:
            rec.contacted = rec.message_ids.filtered(lambda l: l.body)

    def _message_post_after_hook(self, message, msg_vals):
        res = super(CRMLead, self)._message_post_after_hook(message, msg_vals)
        self._compute_contacted()
        return res
