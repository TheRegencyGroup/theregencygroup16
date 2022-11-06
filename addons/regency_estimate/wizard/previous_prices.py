from odoo import fields, models


class PreviousPricesWizard(models.TransientModel):
    _name = 'previous.prices.wizard'
    _description = 'Previous Price Wizard'

    name = fields.Char()
    line_ids = fields.One2many('previous.price.line.wizard', 'price_wizard_id')

    def action_ok(self):
        """ close wizard"""
        return {'type': 'ir.actions.act_window_close'}


class PreviousPriceLineWizard(models.TransientModel):
    _name = 'previous.price.line.wizard'
    _description = 'Previous Price line Wizard'

    product_id = fields.Many2one('product.product')
    currency_id = fields.Many2one('res.currency')
    price = fields.Monetary('SO Price')
    po_price = fields.Monetary('PO Price')
    cost_price = fields.Monetary('Cost Price')
    ca_price = fields.Monetary('CA Price')
    price_wizard_id = fields.Many2one('previous.prices.wizard')
    date_order = fields.Datetime("SO date")
    ca_date_order = fields.Datetime("CA date")
    qty = fields.Float('SO Qty')
    po_qty = fields.Float('PO Qty')
    ca_qty = fields.Float('CA Qty')
    margin_percent = fields.Float("Margin (%)")
