# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class ProductImages(models.Model):
    _inherit = 'product.image'

    def removeimages(self):
        images_id = self.sudo().search([('product_tmpl_id', '=', self.id)])
        for images in images_id:
            images.sudo().unlink()
        return True
