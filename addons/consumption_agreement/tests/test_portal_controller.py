from odoo.tests import tagged
from odoo.tests.common import HttpCase
from odoo.addons.consumption_agreement.tests.common import TestConsumptionCommon
from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.http import root
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

import re
import json


@tagged('all_run', 'post_install')
class TestDownpayment(TestConsumptionCommon, HttpCase):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.Client = Client(root, BaseResponse, use_cookies=True)
        cls.headers = {'X_FORWARDED_FOR': '127.0.0.1', 'REFERER': '8.8.8.8'}
        cls.portal_user = mail_new_test_user(
            cls.env,
            name='ca_portal',
            login='ca_portal',
            email='ca@portal.com',
            groups='base.group_portal',
        )

    def setUp(self):
        super().setUp()
        self.authenticate(self.portal_user.login, self.portal_user.login)

    def call_http_route(self, route, data=False, query_string=False, method='POST'):
        headers = self.headers
        if not query_string:
            query_string = {}
        if not data:
            data = {}
        return self.Client.open(route, query_string=query_string,
                                data=json.dumps(data),
                                content_type='application/json',
                                headers=headers, method=method)


    # def test(self):
    #     self.assertTrue(self.consumption)
    #     response = self.url_open(url=f"/my/consumptions/{self.consumption.id}/create_sale_order/{self.consumption.access_token}",
    #                              data={'selected_line_ids': self.consumption.line_ids.ids})
    #     self.assertEqual(response.status_code, 200, 'The request should be successful.')

    def test_portal_consumption_create_sale_order(self):
        self.assertTrue(self.consumption)
        order_id = self.consumption.id
        self.consumption.get_portal_url()
        data = self.call_http_route(f'/my/consumptions/{ order_id }/create_sale_order',
                                    query_string={'access_token': self.consumption.access_token,
                                                  'session_id': self.session.sid},
                                    data={'params': {'selected_line_ids': self.consumption.line_ids.ids}})
        self.assertEqual(200, data.status_code)
        response = json.loads(data.data)
        redirect_url = response.get('result').get('redirect_url')
        so_id = re.search('\/my\/orders\/(.+?)\?', redirect_url).group(1)
        self.assertTrue(so_id)
        so = self.env['sale.order'].browse(int(so_id))
        self.assertEqual(100, so.order_line.price_subtotal)
