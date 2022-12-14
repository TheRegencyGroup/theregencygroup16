from odoo import models


class MailChammel(models.Model):
    _inherit = 'mail.channel'

    def send_notification(self, user_id, message=False):
        for user in user_id:
            ch_name = user.name + ', ' + self.env.user.name
            ch = self.sudo().search([('name', 'ilike', str(ch_name))]) or self.sudo().search(
                [('name', 'ilike', str(self.env.user.name + ', ' + user.name))])
            if not ch and user != self.env.user:
                ch = self.create({
                    'name': user.name + ', ' + self.env.user.name,
                    'channel_partner_ids': [(4, user.partner_id.id)],
                    # 'public': 'private',
                    'channel_type': 'chat',
                })
            if ch:
                ch.message_post(body=message, author_id=self.env.user.partner_id.id, message_type='comment')
