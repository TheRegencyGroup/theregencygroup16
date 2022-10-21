from odoo import fields, models, api, _, tools


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    contacted = fields.Boolean(compute="_compute_contacted", store=True)
    representative_name = fields.Many2one('res.partner')
    email_from = fields.Char()
    no_open_actions = fields.Integer(string='No. Open Actions')
    no_spend_issues = fields.Boolean(sting="No. Spend Issues")
    management_group = fields.Char(string="Management Group")
    avendra_id = fields.Char(string="Avendra ID")
    account_number = fields.Char(string="Account Number")
    customer_supplier_status = fields.Char(string="Customer Supplier Status")
    customer_status = fields.Char(string="Customer Status")
    market_segment = fields.Char(string="Market Segment")
    brand = fields.Char(string="Brand")
    date_acknowledged = fields.Date(string="Date Acknowledged No Longer a Customer")
    date_de_enrollment = fields.Date(string="De-Enrollment Date")
    avendra_account_name = fields.Char(string="Account Name")
    avendra_account_address1 = fields.Char(string="Account Address 1")
    avendra_account_address2 = fields.Char(string="Account Address 2")
    avendra_account_date_setup = fields.Date(string="Account Setup Date")
    avendra_account_punchout_user_name = fields.Char(string="Account Punchout User Name")
    number_of_keys = fields.Integer()

    @api.depends('message_ids')
    def _compute_contacted(self):
        for rec in self:
            rec.contacted = rec.message_ids.filtered(lambda l: l.body)

    @api.depends('representative_name.email')
    def _compute_email_from(self):
        """
        Overridden to propagate email from representative_name instead of partner_id
        """
        for lead in self:
            if lead.representative_name.email and lead._get_partner_email_update():
                lead.email_from = lead.representative_name.email

    def _inverse_email_from(self):
        """
        Overridden to propagate email from representative_name instead of partner_id
        """
        for lead in self:
            if lead._get_partner_email_update():
                lead.representative_name.email = lead.email_from

    def _get_partner_email_update(self):
        """
        Overridden to propagate email from representative_name instead of partner_id
        """
        """
        Calculate if we should write the email on the related representative. When
        the email of the lead / representative is an empty string, we force it to False
        to not propagate a False on an empty string.
        Done in a separate method so it can be used in both ribbon and inverse
        and compute of email update methods.
        """
        self.ensure_one()
        if self.representative_name and self.email_from != self.representative_name.email:
            lead_email_normalized = tools.email_normalize(self.email_from) or self.email_from or False
            partner_email_normalized = tools.email_normalize(self.representative_name.email) or self.representative_name.email or False
            return lead_email_normalized != partner_email_normalized
        return False

    @api.depends('email_from', 'representative_name')
    def _compute_partner_email_update(self):
        """
        Overridden to propagate email from representative_name instead of partner_id
        """
        for lead in self:
            lead.partner_email_update = lead._get_partner_email_update()

    @api.depends('phone', 'representative_name')
    def _compute_partner_phone_update(self):
        """
        Overridden to propagate phone from representative_name instead of partner_id
        """
        for lead in self:
            lead.partner_phone_update = lead._get_partner_phone_update()

    @api.depends('representative_name.phone')
    def _compute_phone(self):
        """
        Overridden to propagate phone from representative_name instead of partner_id
        """
        for lead in self:
            if lead.representative_name.phone and lead._get_partner_phone_update():
                lead.phone = lead.representative_name.phone

    def _inverse_phone(self):
        """
        Overridden to propagate phone from representative_name instead of partner_id
        """
        for lead in self:
            if lead._get_partner_phone_update():
                lead.representative_name.phone = lead.phone

    def _get_partner_phone_update(self):
        """
        Overridden to propagate phone from representative_name instead of partner_id
        """
        """Calculate if we should write the phone on the related representative. When
        the phone of the lead / representative is an empty string, we force it to False
        to not propagate a False on an empty string.
        Done in a separate method so it can be used in both ribbon and inverse
        and compute of phone update methods.
        """
        self.ensure_one()
        if self.representative_name and self.phone != self.representative_name.phone:
            lead_phone_formatted = self.phone_get_sanitized_number(number_fname='phone') or self.phone or False
            partner_phone_formatted = self.representative_name.phone_get_sanitized_number(number_fname='phone') or self.representative_name.phone or False
            return lead_phone_formatted != partner_phone_formatted
        return False

    def _message_post_after_hook(self, message, msg_vals):
        res = super(CRMLead, self)._message_post_after_hook(message, msg_vals)
        self._compute_contacted()
        return res
