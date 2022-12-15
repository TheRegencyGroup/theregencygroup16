from odoo import fields, models
from odoo.addons.regency_tools.system_messages import accept_format_string, SystemMessages


class ConsumptionAgreement(models.Model):
    _inherit = 'consumption.agreement'

    from_pricesheet_id = fields.Many2one('product.price.sheet', help='From what Pricesheet created')

    def action_confirm(self):
        super().action_confirm()
        for rec in self:
            if rec.from_pricesheet_id and rec.from_pricesheet_id.estimate_id:
                partners_to_inform = self.env['res.partner']
                if rec.from_pricesheet_id.estimate_id.estimate_manager_id:
                    partners_to_inform += rec.from_pricesheet_id.estimate_id.estimate_manager_id.partner_id
                if rec.from_pricesheet_id.estimate_id.purchase_agreement_ids:
                    for partner in rec.from_pricesheet_id.estimate_id.purchase_agreement_ids.mapped('user_id.partner_id'):
                        partners_to_inform += partner
                for partner in partners_to_inform:
                    msg = accept_format_string(SystemMessages.get('M-011'), partner.name, rec.name)
                    rec.message_post(body=msg, partner_ids=partner.ids)
