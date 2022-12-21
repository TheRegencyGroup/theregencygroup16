import logging

logger = logging.getLogger(__name__)


def migrate(cr, version):
    try:
        cr.execute("UPDATE res_partner SET is_customer = true WHERE tmp_contact_type = 'customer';")
        cr.execute("UPDATE res_partner SET is_vendor = true WHERE tmp_contact_type = 'vendor';")
        cr.execute("ALTER TABLE res_partner DROP COLUMN tmp_contact_type;")
    except Exception as e:
        logger.error(e)
        cr.rollback()
