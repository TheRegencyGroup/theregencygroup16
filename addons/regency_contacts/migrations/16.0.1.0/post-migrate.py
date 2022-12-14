def migrate(cr, version):
    cr.execute("UPDATE res_partner SET entity_type='contact' WHERE type='contact' AND NOT is_company AND "
               "entity_type IS NULL;")
