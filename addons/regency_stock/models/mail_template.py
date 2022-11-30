import base64

from odoo import models


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    def generate_email(self, res_ids, fields):
        results = super().generate_email(res_ids, fields)
        for k, v in results.items():
            if v['model'] == 'purchase.order':
                po_id = [v['res_id']]
                report = self.env.ref('regency_stock.action_report_purchase_order_barcode')
                result, report_format = self.env['ir.actions.report']._render_qweb_pdf(report, po_id)
                result = base64.b64encode(result)
                report_name = f'Barcode - {self.env["purchase.order"].browse(po_id).name}'
                v['attachments'].append((report_name, result))
        return results
