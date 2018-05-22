import hug
from seth_fakelite3 import KungFauxPandas
import sqlite3
import sys


kfpd = KungFauxPandas()
dbname = 'file:../../data/sepsis.db?mode=ro'
db_conn = sqlite3.connect(dbname, uri=True)
cursor = db_conn.cursor()

@hug.response_middleware()
def process_data(request, response, resource):
      response.set_header('Access-Control-Allow-Origin', '*')

@hug.get(examples='query=select * from table&method=kde')
@hug.local()
def synthesize_data(query: hug.types.text, method: hug.types.text):
    try:
        print('line 20')
        df = kfpd.read_sql(query, db_conn, method)
        print('line 22')
        print(type(df))
        print(df)
        df.style.hide_index()
        return {
          'message': 'success',
          'query': '{0}'.format(query),
          'response': df.to_html(classes='table')}
    except Exception as e:
        print('Caught exception', str(e))
        return {
            'message': 'error',
            'query': '{0}'.format(query),
            'response': str(e)}

@hug.get()
@hug.local()
def synthesis_methods():
    return {
        'message': 'available data synthesis methods',
        'response': kfpd.synthesis_methods}

@hug.get()
@hug.local()
def metadata():
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    response = []
    for c in tables:
        cursor.execute("SELECT sql FROM sqlite_master WHERE name='" + c[0] + "'")
        response.append(cursor.fetchall()[0][0])

    return {
        'message': 'success',
        'response': response}
