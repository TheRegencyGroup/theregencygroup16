from odoo import fields, models, api, Command, _, SUPERUSER_ID
from odoo.tools.misc import get_lang

PARTNER_ADDRESS_FIELDS_TO_SYNC = [
    'street',
    'street2',
    'city',
    'zip',
    'state_id',
    'country_id',
]


AVAILABLE_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Very High'),
]


class SaleEstimate(models.Model):
    _name = 'sale.estimate'
    _description = "Estimate"
    _order = "id desc"
    _inherit = ['mail.thread']

    # Description
    name = fields.Char(
        'Estimate', index=True, required=True,
        compute='_compute_name', readonly=False, store=True)
    description = fields.Html('Notes')
    company_id = fields.Many2one(
        'res.company', string='Company', index=True,
        compute='_compute_company_id', readonly=False, store=True)
    user_id = fields.Many2one(
        'res.users', string='Salesperson', default=lambda self: self.env.user,
        domain="[('share', '=', False)]",
        check_company=True, index=True, tracking=True)
    priority = fields.Selection(
        AVAILABLE_PRIORITIES, string='Priority', index=True,
        default=AVAILABLE_PRIORITIES[0][0])
    stage_id = fields.Many2one(
        'sale.estimate.stage', string='Stage', index=True, tracking=True,
        group_expand='_read_group_stage_ids',
        readonly=False, copy=False, ondelete='restrict')
    tag_ids = fields.Many2many(
        'crm.tag', 'estimate_tag_rel', 'estimate_id', 'tag_id', string='Tags',
        help="Classify and analyze your estimates categories like: Training, Service")
    color = fields.Integer('Color Index', default=0)
    # Customer / contact
    partner_id = fields.Many2one(
        'res.partner', string='Customer', check_company=True, index=True, tracking=10,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")
    contact_name = fields.Char(
        'Contact Name', tracking=30,
        compute='_compute_contact_name', readonly=False, store=True)
    # Address fields
    street = fields.Char('Street', compute='_compute_partner_address_values', readonly=False, store=True)
    street2 = fields.Char('Street2', compute='_compute_partner_address_values', readonly=False, store=True)
    zip = fields.Char('Zip', change_default=True, compute='_compute_partner_address_values', readonly=False,
                      store=True)
    city = fields.Char('City', compute='_compute_partner_address_values', readonly=False, store=True)
    state_id = fields.Many2one(
        "res.country.state", string='State',
        compute='_compute_partner_address_values', readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country',
        compute='_compute_partner_address_values', readonly=False, store=True)

    opportunity_id = fields.Many2one('crm.lead')
    product_lines = fields.One2many('sale.estimate.line', 'estimate_id')
    purchase_agreement_count = fields.Integer(compute='_compute_purchase_agreement_data', string="Number of Purchase Agreements")
    purchase_agreement_ids = fields.One2many('purchase.requisition', 'estimate_id', string='Purchase Agreements')
    price_sheet_count = fields.Integer(compute='_compute_price_sheet_data',
                                              string="Number of Price Sheets")
    price_sheet_ids = fields.One2many('product.price.sheet', 'estimate_id', string='Price Sheets')
    is_selected = fields.Boolean(compute="_compute_is_selected")
    sale_order_ids = fields.One2many('sale.order', 'estimate_id', string='Sale Orders')
    sale_order_count = fields.Integer(compute='_compute_sale_order_count')
    # the field is used for product configuration widget at product lines
    order_line = fields.One2many('sale.estimate.line', compute='_compute_order_line')
    sold_product_ids = fields.Many2many('product.template', 'sold_templ_rel', compute='_compute_sold_product_ids',
                                        store=True, index=True)

    @api.depends('partner_id', 'partner_id.sale_order_ids')
    def _compute_sold_product_ids(self):
        for rec in self:
            rec.sold_product_ids = rec.partner_id.sale_order_ids.order_line.mapped('product_template_id')

    def _compute_order_line(self):
        for rec in self:
            rec.order_line = rec.product_lines

    def _compute_sale_order_count(self):
        for rec in self:
            rec.sale_order_count = len(rec.sale_order_ids)

    @api.depends('user_id')
    def _compute_company_id(self):
        """ Compute company_id coherency. """
        for rec in self:
            proposal = rec.company_id

            # invalidate wrong configuration
            if proposal:
                # company not in responsible companies
                if rec.user_id and proposal not in rec.user_id.company_ids:
                    proposal = False

            # propose a new company based on responsible
            if not proposal:
                if rec.user_id:
                    proposal = rec.user_id.company_id & self.env.companies
                else:
                    proposal = False

            # set a new company
            if rec.company_id != proposal:
                rec.company_id = proposal

    @api.depends('partner_id')
    def _compute_name(self):
        for rec in self:
            if not rec.name and rec.partner_id and rec.partner_id.name:
                rec.name = _("%s's estimate") % rec.partner_id.name

    @api.depends('partner_id')
    def _compute_contact_name(self):
        """ compute the new values when partner_id has changed """
        for rec in self:
            rec.update(rec._prepare_contact_name_from_partner(rec.partner_id))

    def _prepare_contact_name_from_partner(self, partner):
        contact_name = False if partner.is_company else partner.name
        return {'contact_name': contact_name or self.contact_name}

    @api.depends('partner_id')
    def _compute_partner_address_values(self):
        """ Sync all or none of address fields """
        for rec in self:
            rec.update(rec._prepare_address_values_from_partner(rec.partner_id))

    def _prepare_address_values_from_partner(self, partner):
        # Sync all address fields from partner, or none, to avoid mixing them.
        if any(partner[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC):
            values = {f: partner[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC}
        else:
            values = {f: self[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC}
        return values

    @api.depends('product_lines', 'product_lines.selected')
    def _compute_is_selected(self):
        for rec in self:
            rec.is_selected = all(rec.mapped('product_lines.selected'))

    @api.depends('purchase_agreement_ids.state', 'purchase_agreement_ids')
    def _compute_purchase_agreement_data(self):
        for rec in self:
            rec.purchase_agreement_count = len(rec.purchase_agreement_ids)

    @api.depends('price_sheet_ids')
    def _compute_price_sheet_data(self):
        for rec in self:
            rec.price_sheet_count = len(rec.price_sheet_ids)

    def acton_select_all(self):
        for rec in self:
            rec.product_lines.write({'selected': True})
            rec._compute_is_selected()

    def acton_unselect_all(self):
        for rec in self:
            rec.product_lines.write({'selected': False})
            rec._compute_is_selected()

    def action_new_purchase_agreement(self):
        action = self.env["ir.actions.actions"]._for_xml_id("regency_estimate.action_purchase_requisition_new")
        selected_lines = self.product_lines.filtered(lambda l: l.selected)
        action['context'] = {
            'search_default_estimate_id': self.id,
            'default_estimate_id': self.id,
            'default_type_id': self.env.ref('regency_estimate.type_multi').id,
            'default_estimate_line_ids': [
                Command.link(l.id) for l in selected_lines
            ],
            'default_line_ids': [
                Command.create({
                    'product_description_variants': p.name,
                    'product_id': p.product_id.id,
                    'product_qty': p.product_uom_qty,
                    'product_uom_id': p.product_id.uom_id.id
                }) for p in selected_lines]
        }
        selected_lines.write({'selected': False})
        return action

    def action_new_sale_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        action['target'] = 'new'
        selected_lines = self.product_lines.filtered(lambda l: l.selected)
        action['context'] = {
            'default_partner_id': self.partner_id.id,
            'default_estimate_id': self.id,
            'default_order_line': [
                Command.create({
                    'name': p.product_id.name,
                    'product_uom_qty': p.product_uom_qty,
                    'product_id': p.product_id.id,
                    'price_unit': p.product_id.list_price,
                }) for p in selected_lines]
        }
        selected_lines.write({'selected': False})
        return action

    def action_view_purchase_agreement(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase_requisition.action_purchase_requisition")
        action['context'] = {
            'default_estimate_id': self.id
        }
        action['domain'] = [('estimate_id', '=', self.id)]
        if len(self.purchase_agreement_ids) == 1:
            action['views'] = [(self.env.ref('purchase_requisition.view_purchase_requisition_form').id, 'form')]
            action['res_id'] = self.purchase_agreement_ids.id
        return action

    def action_view_sale_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action['context'] = {
            'default_estimate_id': self.id
        }
        action['domain'] = [('estimate_id', '=', self.id)]
        if len(self.sale_order_ids) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = self.sale_order_ids.id
        return action

    def action_new_price_sheet(self):
        confirmed_requisition_lines = self.purchase_agreement_ids.mapped('line_ids').filtered(lambda a: a.state == 'done')
        products_to_estimate = self.product_lines.mapped(lambda x: (x.product_id, x.product_uom_qty))
        new_requisition_lines = confirmed_requisition_lines.filtered(lambda x: (x.product_id, x.product_qty) not in products_to_estimate)
        sheet_lines = []
        for p in self.product_lines.filtered('selected').sorted('sequence'):
            seq = p.sequence
            if p.display_type:
                sheet_lines.append(Command.create({
                    'name': p.name,
                    'sequence': seq,
                    'display_type': p.display_type
                }))
            else:
                matched_lines = confirmed_requisition_lines.filtered(lambda x: x.product_id == p.product_id
                                                           and x.product_qty == p.product_uom_qty).sorted('product_qty')
                if matched_lines:
                    for line in matched_lines:
                        sheet_lines.append(Command.create({
                                'name': p.name,
                                'sequence': seq,
                                'product_id': p.product_id.id,
                                'partner_id': line.partner_id.id,
                                'min_quantity': line.product_qty,
                                'vendor_price': line.price_unit,
                                'price': line.price_unit * 1.6,
                                'total': line.price_unit * 1.6 * line.product_qty,
                                'display_type': p.display_type,
                                'produced_overseas': line.produced_overseas,
                                'sale_estimate_line_ids': [(6, 0, [p.id])]
                            }))
                        seq += 1
                else:
                    # create new line for the product that is in estimate, but not in purchase requisition
                    sheet_lines.append(Command.create({
                        'name': p.name,
                        'sequence': seq,
                        'product_id': p.product_id.id,
                        'partner_id': False,
                        'min_quantity': p.product_uom_qty,
                        'vendor_price': p.product_id.standard_price,
                        'price': p.product_id.list_price,
                        'total': p.product_id.list_price * p.product_uom_qty,
                        'display_type': p.display_type,
                        'sale_estimate_line_ids': [(6, 0, [p.id])]
                    }))
                    seq += 1

        # add new lines(not in estimate) from confirmed purchase requisitions
        seq = self.product_lines.sorted('sequence')[-1].sequence
        for x in new_requisition_lines:
            sheet_lines.append(Command.create({
                'name': x.product_description_variants,
                'sequence': seq,
                'product_id': x.product_id.id,
                'partner_id': x.partner_id.id,
                'min_quantity': x.product_qty,
                'vendor_price': x.price_unit,
                'price': x.price_unit * 1.6,
                'total': x.price_unit * 1.6 * x.product_qty,
                'produced_overseas': x.produced_overseas
            }))
            seq += 1
        existing_draft_pricesheets = self.price_sheet_ids.filtered(lambda x: x.state == 'draft')
        if existing_draft_pricesheets:
            pricesheet = existing_draft_pricesheets[0]
            pricesheet.update_lines(sheet_lines)
            action = self.action_view_price_sheet()
            action['views'] = [(self.env.ref('regency_estimate.product_price_sheet_view_inherit').id, 'form')]
            action['res_id'] = pricesheet.id
        else:
            action = self.env["ir.actions.actions"]._for_xml_id("regency_estimate.action_product_price_sheet_new")
            action['context'] = {
                'search_default_estimate_id': self.id,
                'default_estimate_id': self.id,
                'default_item_ids': sheet_lines
            }
        self.product_lines.filtered('selected').write({'selected': False})
        return action

    def action_view_price_sheet(self):
        action = self.env["ir.actions.actions"]._for_xml_id("regency_estimate.action_product_price_sheet")
        action['context'] = {
            'default_estimate_id': self.id
        }
        action['domain'] = [('estimate_id', '=', self.id)]
        if len(self.price_sheet_ids) == 1:
            action['views'] = [(self.env.ref('regency_estimate.product_price_sheet_view_inherit').id, 'form')]
            action['res_id'] = self.price_sheet_ids.id
        return action

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Read group customization in order to display all the stages in the
            kanban view, even if they are empty
        """
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)


class SaleEstimateLine(models.Model):
    _name = 'sale.estimate.line'

    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer("Sequence", default=10)
    estimate_id = fields.Many2one('sale.estimate')
    company_id = fields.Many2one(related='estimate_id.company_id')
    product_id = fields.Many2one(
        'product.product', string='Product', domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True, ondelete='restrict', check_company=True)  # Unrequired company
    product_template_id = fields.Many2one(
        'product.template', string='Product Template',
        related="product_id.product_tmpl_id", domain=[('sale_ok', '=', True)], readonly=False, store=True)
    product_custom_attribute_value_ids = fields.One2many('product.attribute.custom.value', 'estimate_product_line_id',
                                                         string="Custom Values", copy=True)

    # M2M holding the values of product.attribute with create_variant field set to 'no_variant'
    # It allows keeping track of the extra_price associated to those attribute values and add them to the SO line description
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value', string="Extra Values",
                                                              ondelete='restrict')
    is_configurable_product = fields.Boolean('Is the product configurable?',
                                             related="product_template_id.has_configurable_attributes")
    product_template_attribute_value_ids = fields.Many2many(related='product_id.product_template_attribute_value_ids',
                                                            readonly=True)

    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    selected = fields.Boolean(default=False)
    purchase_agreement_ids = fields.Many2many('purchase.requisition', 'sale_estimate_line_purchase_agreements_rel',
                                     'estimate_line_id', 'purchase_agreement_id')
    purchase_requisition_line_ids = fields.Many2many('purchase.requisition.line',
                                                     'estimate_line_purchase_requisition_rel', 'estimate_line_id',
                                                     'requisition_line_id',
                                                     compute='_compute_purchase_requisition_line_ids', store=True)
    price_sheet_line_ids = fields.Many2many('product.price.sheet.line',
                                            'product_price_sheet_line_sale_estimate_line_relation',
                                            'sale_estimate_line_id', 'price_sheet_line_id')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    comment = fields.Text('Comment')

    # Fields below used for a widget
    virtual_available_at_date = fields.Float(compute='_compute_qty_at_date', digits='Product Unit of Measure')
    qty_available_today = fields.Float(compute='_compute_qty_at_date')
    free_qty_today = fields.Float(compute='_compute_qty_at_date')
    scheduled_date = fields.Datetime(compute='_compute_qty_at_date')  # Need to display widget as red
    qty_to_deliver = fields.Float(compute='_compute_qty_to_deliver', digits='Product Unit of Measure')
    forecast_expected_date = fields.Datetime(compute='_compute_qty_at_date')
    move_ids = fields.One2many('stock.move', 'sale_line_id', string='Stock Moves')
    is_mto = fields.Boolean(compute='_compute_is_mto')
    display_qty_widget = fields.Boolean(compute='_compute_qty_to_deliver')

    def _compute_qty_at_date(self):
        for sel in self:
            sel.virtual_available_at_date = sel.product_id.free_qty
            sel.qty_available_today = 0
            sel.free_qty_today = 0
            sel.scheduled_date = fields.Datetime.now()
            sel.forecast_expected_date = fields.Datetime.now()

    def _compute_is_mto(self):
        for sel in self:
            sel.is_mto = False  # If False, forecasted displayed

    def _compute_qty_to_deliver(self):
        for sel in self:
            sel.qty_to_deliver = sel.product_uom_qty # Red widget if qty_to_deliver less than virtual_available_at_date
            sel.display_qty_widget = True

    @api.onchange('product_id')
    def product_id_change(self):
        self._update_description()

    def _update_description(self):
        if not self.product_id:
            return
        valid_values = self.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.custom_product_template_attribute_value_id not in valid_values:
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav._origin not in valid_values:
                self.product_no_variant_attribute_value_ids -= ptav

        product = self.product_id.with_context(
            lang=get_lang(self.env, self.estimate_id.partner_id.lang).code,
        )

        self.update({'name': self.get_multiline_description_sale(product, self.product_template_attribute_value_ids)})

    def get_multiline_description_sale(self, product, picked_attrs):
        """ Compute a default multiline description for this product line.

        In most cases the product description is enough but sometimes we need to append information that only
        exists on the sale order line itself.
        e.g:
        - custom attributes and attributes that don't create variants, both introduced by the "product configurator"
        - in event_sale we need to know specifically the sales order line as well as the product to generate the name:
          the product is not sufficient because we also need to know the event_id and the event_ticket_id (both which belong to the sale order line).
        """
        # display the is_custom values
        attrs_name = ''
        for pacv in picked_attrs:
            attrs_name += "\n" + pacv.with_context(lang=self.estimate_id.partner_id.lang).display_name
        return product.get_product_multiline_description_sale() + attrs_name + self._get_multiline_description_variants()

    def _get_multiline_description_variants(self):
        """When using no_variant attributes or is_custom values, the product
        itself is not sufficient to create the description: we need to add
        information about those special attributes and values.

        :return: the description related to special variant attributes/values
        :rtype: string
        """
        if not self.product_custom_attribute_value_ids and not self.product_no_variant_attribute_value_ids:
            return ""

        name = "\n"

        custom_ptavs = self.product_custom_attribute_value_ids.custom_product_template_attribute_value_id
        no_variant_ptavs = self.product_no_variant_attribute_value_ids._origin

        # display the no_variant attributes, except those that are also
        # displayed by a custom (avoid duplicate description)
        for ptav in (no_variant_ptavs - custom_ptavs):
            name += "\n" + ptav.with_context(lang=self.estimate_id.partner_id.lang).display_name

        # Sort the values according to _order settings, because it doesn't work for virtual records in onchange
        custom_values = sorted(self.product_custom_attribute_value_ids,
                               key=lambda r: (r.custom_product_template_attribute_value_id.id, r.id))
        # display the is_custom values
        for pacv in custom_values:
            name += "\n" + pacv.with_context(lang=self.estimate_id.partner_id.lang).display_name

        return name

    @api.depends('estimate_id.purchase_agreement_ids.line_ids')
    def _compute_purchase_requisition_line_ids(self):
        for sel in self:
            prl_ids = sel.estimate_id.purchase_agreement_ids.mapped('line_ids')
            related_prl_ids = prl_ids.filtered(
                lambda f: f.product_id == sel.product_id and f.product_qty == sel.product_uom_qty)
            sel.purchase_requisition_line_ids = [(6, 0, related_prl_ids.ids)]
