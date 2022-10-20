from odoo import fields, models, api


class PricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    applied_on = fields.Selection(selection_add=[('4_overlay_template', 'Shopsite Item Template')],
                                  ondelete={'4_overlay_template': 'cascade'})
    overlay_tmpl_id = fields.Many2one('overlay.template')

    @api.depends('applied_on', 'categ_id', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price',
                 'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge')
    def _compute_name_and_price(self):
        """
        Overridden to get name of added kind of price list item
        """
        super()._compute_name_and_price()
        for item in self:
            if item.overlay_tmpl_id and item.applied_on == '4_overlay_template':
                item.name = "Shopsite Item Template: {}".format(item.overlay_tmpl_id.display_name)
