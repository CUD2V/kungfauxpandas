import hug
from seth_fakelite3 import KungFauxPandas
import sqlite3
import sys
import re


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
    if query_ok(query):

        # if limit statement exists, either:
        #   increase limit to minimum number
        #   remove limit statement for query, but only return limit

        try:
            df = kfpd.read_sql(query, db_conn, method)
            df_html = (
                df.style
                .hide_index()
                .set_table_attributes("class='table table-hover'")
                .set_uuid('_')
                .render()
            )
            # pandas generated html has a lot of stuff we don't want returned
            # chuck it!
            df_html = re.sub(' id="T__row\d+_col\d+"', '', df_html)
            df_html = re.sub(' class="data row\d+ col\d+" ', '', df_html)

            return {
              'message': 'success',
              'query': '{0}'.format(query),
              'response': df_html,
              'csv': df.to_csv(index=False)}
        except Exception as e:
            print('Caught exception', str(e))
            return {
                'message': 'error',
                'query': '{0}'.format(query),
                'response': str(e)}
    else:
        return {
            'message': 'error',
            'query': '{0}'.format(query),
            'response': 'Invalid query provided.'}

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


def query_ok(input):
    input = input.strip()
    return (
        len(input) > 14 and
        input != '-- Type SQL Code here' and
        'delete' not in input and
        'insert' not in input and
        'update' not in input and
        'drop'   not in input and
        'create' not in input and
        'alter'  not in input
    )
