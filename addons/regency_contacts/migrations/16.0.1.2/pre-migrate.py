import logging

logger = logging.getLogger(__name__)


def migrate(cr, version):
    try:
        cr.execute("ALTER TABLE res_partner ADD tmp_contact_type varchar;")
        cr.execute("UPDATE res_partner SET tmp_contact_type = contact_type;")
    except Exception as e:
        logger.error(e)
        cr.rollback()
