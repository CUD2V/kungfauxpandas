# TO DO:
#  * check bad queries
#  * check update queries (insert, update, delete, drop, create, alter)
#  * check too few results. What is too few? 30? 100?
#  * test each synthesis method
#  * REST calls


import hug
import pytest
import sys

sys.path.insert(1, '.')
import web_service

@pytest.fixture
def sample_basic_sql():
    return """
        select * from admission
    """

@pytest.fixture
def sample_basic_sql2():
    return "select * from admission;"

@pytest.fixture
def sample_bad_sql():
    return """
        delete from admission
    """

@pytest.fixture
def sample_method():
    # should we test other methods here?
    return 'Trivial'

@pytest.fixture
def sample_bad_method():
    # should we test other methods here?
    return 'laivirT'

# the "process_data" function isn't actually an exposed part of the REST
# service, but sets the access control origin header
# don't want to call directly as we don't have the required inputs
def test_process_data():
    response = hug.test.get(web_service, 'process_data')
    found_header = False
    for r in response.headers:
        if r[0] == 'access-control-allow-origin':
            found_header = True
    assert(found_header)

def test_synthesize_data(sample_basic_sql, sample_basic_sql2, sample_bad_sql, sample_method, sample_bad_method):
    # pass nothing
    response = hug.test.get(web_service, 'synthesize_data')
    assert(response.status == '400 Bad Request')
    assert(response.data is not None)

    # pass just query
    response = hug.test.get(web_service, 'synthesize_data', {'query': sample_basic_sql})
    assert(response.status == '400 Bad Request')
    assert(response.data is not None)

    # pass just method
    response = hug.test.get(web_service, 'synthesize_data', {'method': sample_method})
    assert(response.status == '400 Bad Request')
    assert(response.data is not None)

    # pass both required parameters
    response = hug.test.get(web_service, 'synthesize_data', {
        'method': sample_method,
        'query' : sample_basic_sql})
    assert(response.status == '200 OK')
    assert(response.data is not None)
    assert(response.data['message'] == 'success')
    assert(response.data['query'] == sample_basic_sql)
    assert(response.data['executed_query'] is not None)
    assert(response.data['response'] is not None)

    # pass both required parameters, test with semicolon
    response = hug.test.get(web_service, 'synthesize_data', {
        'method': sample_method,
        'query' : sample_basic_sql2})
    assert(response.status == '200 OK')
    assert(response.data is not None)
    assert(response.data['message'] == 'success')
    assert(response.data['query'] == sample_basic_sql2)
    s = sample_basic_sql2.replace(';', '')
    assert(response.data['executed_query'] == s + '\norder by random();')
    assert(response.data['response'] is not None)

    # invalid query and invalid method
    response = hug.test.get(web_service, 'synthesize_data', {
    'method': sample_bad_method,
    'query' : sample_bad_sql})
    assert(response.status == '200 OK')
    assert(response.data['message'] == 'error')

    # extra parameters should be ignored
    response = hug.test.get(web_service, 'synthesize_data', {
        'method': sample_method,
        'query' : sample_basic_sql,
        'foo'   : 'bar' })
    assert(response.status == '200 OK')
    assert(response.data is not None)

def test_synthesis_methods():
    response = hug.test.get(web_service, 'synthesis_methods')
    assert(response.status == '200 OK')
    assert(response.data['message'] == 'available data synthesis methods')
    assert(response.data['response'] is not None)

    # extra parameters should be ignored
    response = hug.test.get(web_service, 'synthesis_methods', {'foo':'bar'})
    assert(response.status == '200 OK')
    assert(response.data['message'] == 'available data synthesis methods')
    assert(response.data['response'] is not None)

def test_metadata():
    response = hug.test.get(web_service, 'metadata')
    assert(response.data['message'] == 'success')
    assert(response.data['response'] is not None)

    # extra parameters should be ignored
    response = hug.test.get(web_service, 'metadata', {'foo':'bar'})
    assert(response.data['message'] == 'success')
    assert(response.data['response'] is not None)

def test_query_ok(sample_basic_sql, sample_bad_sql):
    assert(web_service.query_ok(sample_basic_sql))
    assert(web_service.query_ok(sample_bad_sql) == False)

def test_upload_data():
    # test uploading nothing
    response = hug.test.post(web_service, 'upload_data')
    assert(response.data['message'] == 'error')

    # test uploading something other than a csv
    with open('kungfauxpandas.py', 'rb') as inputfile:
        # because of the way hug.test passes files, pandas does its best to treat
        # file like a csv and throws some warnings but eventually fails
        import warnings
        warnings.filterwarnings('ignore')

        lines = inputfile.read()
        response = hug.test.post(web_service, 'upload_data', {'kungfauxpandas.py': lines})
        assert(response.data['message'] == 'error')

    # test uploading a csv
    with open('../../data/fake_sepsis_data/flowsheet.csv', 'rb') as inputfile:
        lines = inputfile.read()
        response = hug.test.post(web_service, 'upload_data', {'flowsheet.csv': lines})
        assert(response.data['message'] == 'success')
