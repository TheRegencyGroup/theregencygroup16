import base64

from odoo import models


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    def generate_email(self, res_ids, fields):
        results = super().generate_email(res_ids, fields)
        for k, v in results.items():
            if v['model'] == 'purchase.order':
                po = self.env["purchase.order"].browse(v['res_id'])
                if po.state == 'purchase':
                    report = self.env.ref('regency_stock.action_report_purchase_order_barcode')
                    result, report_format = self.env['ir.actions.report']._render_qweb_pdf(report, po.order_line.ids)
                    result = base64.b64encode(result)
                    report_name = f'Barcode - {po.name}'
                    v['attachments'].append((report_name, result))
        return results
