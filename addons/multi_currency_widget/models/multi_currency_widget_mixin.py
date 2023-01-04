from odoo import api, fields, models, _
import markupsafe


class MultiCurrencyMixin(models.AbstractModel):
    _name = "multi.currency.mixin"
    _description = 'Multi-Currency Mixin'

    def get_currencies_values(self, value_field, currency_field, date_field):
        self.ensure_one()
        value = 0.0
        if hasattr(self, value_field):
           value = self[value_field]

        currency_field = currency_field or 'currency_id'
        currency_id = False
        if hasattr(self, currency_field):
            currency_id = self[currency_field]

        if hasattr(self, 'company_id'):
            company_id = self.company_id
        else:
            company_id = self.env.company

        if date_field and (self, date_field):
            date = self[date_field]
        else:
            date = fields.Date.today()

        currencies = self.env['res.currency'].search([('active', '=', True), ('id', '!=', currency_id.id)])
        result = []
        for cur in currencies:
            new_val = cur._convert(value, currency_id, company_id, date, round=True)
            result.append([round(new_val, 6), cur.symbol])
        return result