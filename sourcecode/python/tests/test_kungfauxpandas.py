import sys
import pytest

sys.path.insert(1, '.')
from kungfauxpandas import KungFauxPandas, TrivialPlugin, DataSynthesizerPlugin, KDEPlugin, KFP_DataDescriber

@pytest.fixture
def sample_df():
    import pandas as pd
    return pd.DataFrame({'unique_id': [40552133, 83299697, 96360391, 43551783, 92110570, 87411981, 26772988, 87390284, 34538374, 13208258],
                         # DataSynthesizer doesnt work with dates so not using these for now
                         #'datetime': ['2017-11-09 02:26:13', '2017-07-20 20:35:41', '2017-12-23 22:48:30', '2017-10-04 05:19:36', '2017-10-15 04:03:31', '2017-08-12 11:35:34', '2017-08-07 12:57:29', '2017-09-20 12:17:48', '2017-08-23 12:39:54', '2017-06-29 07:59:25'],
                         'alpha_numeric_code': ['A4152', 'A414', 'A400', 'A392', 'A4151', 'A392', 'A4181', 'P369', 'B377', 'R6521'],
                         'constant': ['constant_value', 'constant_value', 'constant_value', 'constant_value', 'constant_value', 'constant_value', 'constant_value', 'constant_value', 'constant_value', 'constant_value'],
                         'categorical' : ['category1', 'category2', 'category1', 'category1', 'category2', 'category1', 'category2', 'category1', 'category2', 'category3'],
                         # DataSynthesizer doesnt always work with floating point values, so not using these for now
                         #'float_score': [30.80887770115334, 31.647178703213896, 33.23121156661242, 33.64713140102367, 33.07404123596502, 34.206309535666364, 34.90974444556692, 39.06948372169004, 35.94952085309618, 29.5140595543271],
                         'int_score': [294, 286, 278, 272, 256, 242, 216, 210, 208, 190]})

@pytest.fixture
def sample_conn():
    import sqlite3
    # use the sample database already provided
    return sqlite3.connect("../../data/sample_data.db")

@pytest.fixture
def sample_sql():
    return """
        select * from admission
    """

def test_KungFauxPandas(sample_sql, sample_conn, sample_df):
    kfp = KungFauxPandas()

    assert len(kfp.synthesis_methods) > 0

def test_PandaPlugin(sample_df):
    kfp = KungFauxPandas()

    for method in kfp.synthesis_methods:
        # Each synthesis method should accept and return a dataframe
        instance = globals()[method + 'Plugin']()
        print('++++instance: ', instance)
        assert(getattr(instance, "fauxify", None) is not None)
        fn = getattr(instance, "fauxify", None)
        print('++++function: ', fn)
        assert(callable(fn))
        assert(fn(sample_df) is not None)

def test_read_sql(sample_sql, sample_conn):
    kfp = KungFauxPandas()
    for method in kfp.synthesis_methods:
        # read_sql should call each synthesis method
        assert(kfp.read_sql(sample_sql, sample_conn) is not None)

def test_kfp_log(sample_sql, sample_conn):

    kfp = KungFauxPandas()

    count_sql = "select count(1) from kfp_log"

    kfp.logging_cur.execute(count_sql)
    begin_rows = kfp.logging_cur.fetchone()

    # by default KFP will use the "Trivial" plugin
    assert(kfp.read_sql(sample_sql, sample_conn) is not None)

    # now make sure there is at least 1 additional kfp_log record
    kfp.logging_cur.execute(count_sql)
    end_rows = kfp.logging_cur.fetchone()

    assert(begin_rows < end_rows)


def test_kfp_custom_log(sample_sql, sample_conn):

    kfp = KungFauxPandas(db_file='../../data/kfp_log.db')

    count_sql = "select count(1) from kfp_log"

    kfp.logging_cur.execute(count_sql)
    begin_rows = kfp.logging_cur.fetchone()

    # by default KFP will use the "Trivial" plugin
    assert(kfp.read_sql(sample_sql, sample_conn) is not None)

    # now make sure there is at least 1 additional kfp_log record
    kfp.logging_cur.execute(count_sql)
    end_rows = kfp.logging_cur.fetchone()

    assert(begin_rows < end_rows)

# this is a class that overrides some of of the base DataSynthesizer methods to
# allow dataframes to be used directly without having to write a CSV first
# test the two methods we override - ignore the rest
def test_KFP_DataDescriber(sample_df):
    dd = KFP_DataDescriber()

    # calling this function without passing either a file path or setting df_in should result in ValueError
    with pytest.raises(ValueError):
        dd.read_dataset_from_csv()

    # now set df_in
    dd = KFP_DataDescriber()
    dd.df_in = sample_df
    assert(dd.read_dataset_from_csv() is None)

    dd = KFP_DataDescriber()
    assert(dd.input_dataset is None)
    dd.df_in = sample_df
    dd.link_loaded_dataset()
    assert(dd.input_dataset.equals(sample_df))


# this synthesis method has a few different synthesis methods - verify they work
def test_DataSynthesizerPlugin(sample_df):
    kfp = KungFauxPandas()

    kfp.plugin = DataSynthesizerPlugin()
    assert(len(kfp.plugin.synthesis_modes) > 0)

    for mode in kfp.plugin.synthesis_modes:
        kfp.plugin = DataSynthesizerPlugin(mode=mode)
        assert(kfp.plugin.fauxify(sample_df) is not None)
