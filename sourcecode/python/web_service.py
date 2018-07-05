import hug
from kungfauxpandas import KungFauxPandas, TrivialPlugin, DataSynthesizerPlugin, KDEPlugin
import sqlite3
import sys
import re
import sqlparse
import pandas as pd
import chardet
from io import StringIO

kfpd = KungFauxPandas()
dbname = 'file:../../data/sample_data.db?mode=ro'
db_conn = sqlite3.connect(dbname, uri=True)
cursor = db_conn.cursor()
# for allowing inserting new data
writeable_dbname = 'file:../../data/sample_data.db'
writable_db_conn = sqlite3.connect(writeable_dbname, uri=True)

@hug.response_middleware()
def process_data(request, response, resource):
      response.set_header('Access-Control-Allow-Origin', '*')
      response.set_header('Access-Control-Allow-Methods', 'GET, POST')

@hug.get(examples='query=select * from table&method=kde')
@hug.local()
def synthesize_data(query: hug.types.text, method: hug.types.text):
    if query_ok(query):

        parsed = sqlparse.parse(query)[0]

        order_found = False
        order_clauses = []
        limit_found = False
        if parsed.get_type() == 'SELECT':
            for t in parsed.tokens:
                if(t.is_whitespace):
                    continue
                if (t.is_keyword and t.normalized == 'ORDER'):
                    order_found = True
                    continue
                if order_found:
                    if t.is_keyword and t.normalized != 'BY':
                        break
                    elif isinstance(t, (sqlparse.sql.Identifier, sqlparse.sql.IdentifierList)):
                        order_clauses.append(str(t))
            for t in parsed.tokens:
                if (t.is_keyword and t.normalized == 'LIMIT'):
                    limit_found = True

        # replace order by clauses with random()
        # as order by doesn't do anything once synthesis occurs
        fixed_query = query
        if order_found:
            i = query.rfind(order_clauses[0])
            fixed_query = fixed_query[:i] + "random()" + fixed_query[i + len(order_clauses[0]):]

            for o in order_clauses[1:]:
                i = fixed_query.rfind(o)
                fixed_query = fixed_query[:i] + fixed_query[i + len(o):]

            # some cleanup
            fixed_query = re.sub('random\(\),', 'random()', fixed_query, flags=re.M)
            fixed_query = re.sub('^\s+,', '', fixed_query, flags=re.M)
        # if no order by statement present, add it
        else:
            if limit_found:
                i = fixed_query.lower().rfind('limit')
                fixed_query = fixed_query[:i] + "\norder by random()\n" + fixed_query[i:]
            else:
                fixed_query += '\norder by random()'

        try:
            if method is not None:
                for m in kfpd.synthesis_methods:
                    if method.lower() == m.lower():
                        kfpd.plugin = globals()[m + 'Plugin']()
            df = kfpd.read_sql(fixed_query, db_conn)

            # if any order by clauses were present, re-apply them
            if len(order_clauses) > 0:
                sort_by = []
                asc_flags = []
                orig_columns = df.columns
                df.columns = df.columns.str.lower()

                for o in order_clauses:
                    sub_o = o.split(',')

                    # If you don’t specify the ASC or DESC keyword, SQLite uses ASC or ascending order by default.
                    for s in sub_o:
                        if s.lower().find(' desc') != -1:
                            asc_flags.append(False)
                        else:
                            asc_flags.append(True)
                        sort_by.append(re.sub('\s+asc|\s+desc', '', s, flags=re.IGNORECASE).strip().lower())

                df.sort_values(sort_by, ascending=asc_flags, inplace=True)
                df.columns = orig_columns

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
              'executed_query': fixed_query,
              'response': df_html,
              'csv': df.to_csv(index=False)}
        except Exception as e:
            print('web-service.synthesize_data() caught exception', str(e))
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

@hug.post()
@hug.local()
def upload_data(body):
    filename = list(body.keys())[0]
    file = body[filename]
    # attempt to automatically detect character encoding and read into dataframe
    try:
        chardet.detect(file)['encoding']
        data = file.decode(chardet.detect(file)['encoding'])
        df = pd.read_csv(StringIO(data))
    except Exception as e:
        print('web-service.upload_data() caught exception reading csv', str(e))
        return {
            'message': 'error',
            'filename': filename,
            'response': str(e)
        }
    # attempt to save file to database
    try:
        df.to_sql(filename, writable_db_conn, if_exists='replace', index=False)
    except Exception as e:
        print('web-service.upload_data() caught exception saving file to database', str(e))
        return {
            'message': 'error',
            'filename': filename,
            'response': str(e)
        }

    return {
        'message': 'success',
        'response' : {
            'filename': list(body.keys()).pop(),
            'filesize': len(list(body.values()).pop())
        }
    }

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
