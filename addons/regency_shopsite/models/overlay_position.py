from odoo import fields, models


class OverlayPosition(models.Model):
    _name = 'overlay.position'
    _description = "Overlay position"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Overlay position name must be unique'),
    ]

    name = fields.Char(required=True)
