import sqlite3

db_file = '../../data/kfp_log.db'

sql_create_kfp_table = """
    CREATE TABLE IF NOT EXISTS kfp_log (
        query TEXT NOT NULL,
        query_start TEXT NOT NULL,
        query_end TEXT NOT NULL,
        query_result BLOB,
        faux_method TEXT NOT NULL,
        fauxify_start TEXT NOT NULL,
        fauxify_end TEXT NOT NULL,
        faux_result BLOB
    ); """

try:
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(sql_create_kfp_table)
    conn.commit()
except Exception as e:
    print('Exception encountered when creating table:', e)
