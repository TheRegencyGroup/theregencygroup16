from odoo import fields, models, api, _, tools


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    ext_state = fields.Char(string='Ext state', help='Temporary field for storing state info during the import')
    ext_country = fields.Char(string='Ext Country', help='Temporary field for storing country during the import')

    @api.model_create_multi
    def create(self, val_list):
        recs = super().create(val_list)
        recs.update_country_and_state()
        return recs

    def write(self, vals):
        res = super().write(vals)
        if 'ext_country' in vals or 'ext_state' in vals:
            self.update_country_and_state()
        return res

    def update_country_and_state(self):
        for rec in self:
            # find corresponding state during data import
            if rec.ext_country:
                rec.country_id = self.env['res.country'].search(['|', ('name', '=ilike', rec.ext_country),
                                                                 ('alternative_name', '=ilike', rec.ext_country)],
                                                                limit=1)
            if rec.ext_state and rec.country_id:
                rec.state_id = self.env['res.country.state'].search([('country_id', '=', rec.country_id.id),
                                                                     '|',
                                                                     ('name', '=ilike', rec.ext_state),
                                                                     '|',
                                                                     ('code', '=ilike', rec.ext_state),
                                                                     ('alternative_code', '=ilike', rec.ext_state)],
                                                                    limit=1)