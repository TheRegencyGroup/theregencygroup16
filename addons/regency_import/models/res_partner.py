import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ext_code = fields.Char()
    ext_sales_tax_id = fields.Char()
    ext_billing_customer_contact_id = fields.Char()
    ext_shipping_customer_contact_id = fields.Char()
    ext_primary_customer_contact_id = fields.Char()
    ext_is_free_shiping = fields.Char()
    ext_account_on_hold = fields.Char()
    ext_salesrep_email = fields.Char()
    ext_phone_type = fields.Char()
    ext_state = fields.Char()
    ext_country = fields.Char()
    ext_is_regency_contact = fields.Char()

    @api.model_create_multi
    def create(self, val_list):
        recs = super().create(val_list)
        recs.update_country_and_state()
        recs.assign_sales_rep()
        recs.filtered(lambda f: f.type == 'contact').write({'entity_type': 'contact'})
        return recs

    def write(self, vals):
        res = super().write(vals)
        if 'ext_country' in vals or 'ext_state' in vals:
            self.update_country_and_state()
        if 'ext_salesrep_email' in vals:
            self.assign_sales_rep()
        return res

    def assign_sales_rep(self):
        for rec in self:
            if rec.ext_salesrep_email:
                user = self.env['res.users'].search([('login', 'ilike', rec.ext_salesrep_email)], limit=1)
                rec.user_id = user

    def set_contact_type(self):
        for rec in self:
            rec.child_ids.write({'type': 'contact', 'company_id': rec.company_id and rec.company_id.id or False})
            if rec.ext_billing_customer_contact_id:
                try:
                    billing_contact = self.env.ref('__import__.'+rec.ext_billing_customer_contact_id)
                    if billing_contact:
                        billing_contact.type = 'invoice'
                except ValueError as e:
                    _logger.info('Regency after import contacts update failed to find contact %s', str(rec.ext_billing_customer_contact_id))
            if rec.ext_shipping_customer_contact_id:
                try:
                    shipping_contact = self.env.ref('__import__.'+rec.ext_shipping_customer_contact_id)
                    if shipping_contact:
                        shipping_contact.type = 'delivery'
                except ValueError as e:
                    _logger.info('Regency after import contacts update failed to find contact %s', str(rec.ext_shipping_customer_contact_id))

    def set_cc_email(self):
        for rec in self.env['res.partner.email.ext'].search([]):
            contact = self.env.ref('__import__.' + rec.ext_customer_contact_id)
            cc_contact = contact.parent_id.child_ids.filtered(lambda l: l.email and l.email.lower() == rec.email.lower())
            if cc_contact:
                cc_contact.cc_invoice = True
            else:
                rec.env['res.partner'].create({'parent_id': contact.parent_id.id,
                                               'is_company': False,
                                               'email': rec.email,
                                               'name': rec.email,
                                               'cc_invoice': True
                            })

    def set_tags(self):
        all_matches = self.env['res.partner.tags.rel.ext'].search([])
        for m in all_matches:
            customer = self.env.ref('__import__.' + m.ext_customer_id)
            tag = self.env.ref('__import__.' + m.ext_tag_id)
            if customer and tag:
                customer.write({'category_id': [fields.Command.link(tag.id)]})

    def update_country_and_state(self):
        for rec in self:
            # find corresponding state during data import
            if rec.ext_country:
                rec.country_id = self.env['res.country'].search(['|', ('name', '=ilike', rec.ext_country),
                                                                 '|', ('code', '=ilike', rec.ext_country),
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

    def after_import_update(self):
        all = self.search([])
        all.set_tags()
        all.set_contact_type()
        all.set_cc_email()


class AdditionalEmails(models.Model):
    _name = 'res.partner.email.ext'

    email = fields.Char()
    ext_customer_contact_id = fields.Char()


class ContactTags(models.Model):
    _name = 'res.partner.tags.rel.ext'

    ext_customer_id = fields.Char()
    ext_tag_id = fields.Char()
