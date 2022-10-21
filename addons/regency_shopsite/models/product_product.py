from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def open_pricelist_rules(self):
        self.ensure_one()
        domain = ['|',
                  '&', ('product_tmpl_id', '=', self.product_tmpl_id.id), ('applied_on', '=', '1_product'),
                  '&', ('product_id', '=', self.id), ('applied_on', '=', '0_product_variant'),
                  '&', ('overlay_tmpl_id', '=', self.product_tmpl_id.overlay_tmpl_id.id), ('applied_on', '=', '4_overlay_template')]
        return {
            'name': _('Price Rules'),
            'view_mode': 'tree,form',
            'views': [(self.env.ref('product.product_pricelist_item_tree_view_from_product').id, 'tree'), (False, 'form')],
            'res_model': 'product.pricelist.item',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': domain,
            'context': {
                'default_product_id': self.id,
                'default_applied_on': '0_product_variant',
            }
        }
