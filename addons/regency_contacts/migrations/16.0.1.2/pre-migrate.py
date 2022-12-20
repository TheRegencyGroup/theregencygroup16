import logging
from odoo import api, SUPERUSER_ID

logger = logging.getLogger(__name__)


def migrate(cr, version):
    logger.info("Creating columns is_customer and is_vendor")
    cr.execute("ALTER TABLE res_partner ADD IF NOT EXISTS is_customer boolean;")
    cr.execute("ALTER TABLE res_partner ADD IF NOT EXISTS is_vendor boolean;")
    logger.info("Trying to get contact_type field")
    env = api.Environment(cr, SUPERUSER_ID, {})
    field_contact_type_exists = False
    try:
        env['res.partner'].contact_type
        field_contact_type_exists = True
    except Exception as e:
        logger.error(e)
    if field_contact_type_exists:
        cr.execute("UPDATE res_partner SET is_customer=true WHERE contact_type='customer';")
        cr.execute("UPDATE res_partner SET is_vendor=true WHERE contact_type='vendor';")
