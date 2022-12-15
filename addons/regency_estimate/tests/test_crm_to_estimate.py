from odoo.tests import tagged
from odoo.addons.crm.tests import common as crm_common

@tagged('all_run')
class TestRun(crm_common.TestCrmCommon):

    @classmethod
    def setUpClass(cls):
        super(TestRun, cls).setUpClass()
        cls.stage_gen_won.generate_estimate = True

    def test_opportunity_to_estimate(self):
        self.lead_1.action_set_won()
        self.assertEqual(1, self.lead_1.estimates_count)
        self.assertEqual('draft', self.lead_1.estimate_ids.state)
