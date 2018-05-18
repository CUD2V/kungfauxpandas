import hug
from fakelite3 import KungFauxPandas
import sqlite3

kfpd = KungFauxPandas()
dbname = '../../data/sepsis.db'
db_conn = sqlite3.connect(dbname)

@hug.response_middleware()
def process_data(request, response, resource):
      response.set_header('Access-Control-Allow-Origin', '*')

@hug.get(examples='query=select * from table&method=kde')
@hug.local()
def synthesize_data(query: hug.types.text, method: hug.types.text):
    """Does nothing right now"""
    response = 'No data found'
    df = kfpd.read_sql(query, db_conn, method)
    return {
        'message': 'need to provide message here',
        'query': '{0}'.format(query),
        'response': df.to_json()}

@hug.get()
@hug.local()
def synthesis_methods():
    return {
        'message': 'available data synthesis methods',
        'response': kfpd.synthesis_methods}
