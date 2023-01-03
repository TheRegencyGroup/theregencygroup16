def migrate(cr, version):
    cr.execute("ALTER TABLE res_partner ADD tmp_contact_type varchar;")
    cr.execute("SELECT EXISTS (SELECT column_name FROM information_schema.columns WHERE table_name = 'res_partner' AND column_name = 'contact_type');")
    res = cr.fetchall()
    if True in res[0]:
        cr.execute("UPDATE res_partner SET tmp_contact_type = contact_type;")
