from odoo import fields, models, api, _


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    estimate_ids = fields.One2many('sale.estimate', 'opportunity_id')
    estimates_count = fields.Integer(compute='_compute_estimates_data',
                                              string="Number of Estimates")

    @api.depends('estimate_ids')
    def _compute_estimates_data(self):
        for rec in self:
            rec.estimates_count = len(rec.estimate_ids)

    def write(self, vals):
        write_result = super(CRMLead, self).write(vals)
        # stage change: update date_last_stage_update
        if 'stage_id' in vals:
            stage_id = self.env['crm.stage'].browse(vals['stage_id'])
            if stage_id.generate_estimate:
                self.generate_estimate()
        return write_result

    def generate_estimate(self):
        for rec in self:
            estimate = rec.env['sale.estimate'].create({'name': rec.name,
                                                        'partner_id': rec.partner_id.id,
                                                        'contact_name': rec.contact_name,
                                                        'opportunity_id': rec.id,
                                                        'priority': rec.priority,
                                                        'tag_ids': rec.tag_ids.ids,
                                                        'company_id': rec.company_id.id,
                                                        'color': rec.color,
                                                        'stage_id': rec.env.ref('regency_estimate.sale_estimate_stage_new').id,
                                                        'user_id': rec.user_id.id,
                                                        'description': rec.description})
            rec.message_post(body=_("Estimate %s have been created", estimate.name))

    def action_view_estimates(self):
        action = self.env["ir.actions.actions"]._for_xml_id("regency_estimate.sale_estimate_all")
        action['context'] = {
            'default_opportunity_id': self.id
        }
        action['domain'] = [('opportunity_id', '=', self.id)]
        if len(self.estimate_ids) == 1:
            action['views'] = [(self.env.ref('regency_estimate.sale_estimate_view_form').id, 'form')]
            action['res_id'] = self.estimate_ids.id
        return action
