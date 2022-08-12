
import pandas as pd
import numpy as np
import scipy.stats as stats
import sys
import warnings
import datetime
import sqlite3
import contextlib
import scipy.stats as stats
from numpy.random import choice

library_location = '../../plugins/DataSynthesizer'
sys.path.append(library_location)
library_location = '../../plugins/DataSynthesizer/DataSynthesizer/'
sys.path.append(library_location)

from DataSynthesizer.DataDescriber import DataDescriber

####################################################################################################################################
####################################################################################################################################

class PandaPlugin(object):

    def __init__(self, df_in = None):
        self.df_in = df_in

    def fauxify(self, df_in=None, **kwargs):
        """All plugins need to overload this fauxify method which takes a pandas data frame
        and returns a faux-data data frame."""

        print('This is a template--use it to make a plugin')


####################################################################################################################################
####################################################################################################################################

class TrivialPlugin(PandaPlugin):
    """ Returns the input as output. """

    def __init__(self):
        PandaPlugin.__init__(self)



    def fauxify(self, df_in=None):
        if df_in is not None:
            self.df_in = df_in

        self.df_out = self.df_in

        return self.df_out


class DataSynthesizerPlugin(PandaPlugin):
    """ Constructs fake data using using DataSynthesizer based on input df. 
        Can either create column-wise data (i.e. ignore covariances)  base
        on individual variable histogram or table-wise data (bayesian covariance
        of all columns)
    """

    def __init__(self, df_in=None,
            mode = 'correlated_attribute_mode',
            threshold_value = 20,
            categorical_attributes = {},
            candidate_keys = {},
            epsilon = 0.1,
            degree_of_bayesian_network = 2,
            num_tuples_to_generate = None,
            save_faux_data_to_file = False,
            verbose = True):

        PandaPlugin.__init__(self)

        # currently supported modes
        self.synthesis_modes = ('correlated_attribute_mode', 'independent_attribute_mode')
        self.mode = mode
        self.verbose = verbose

        # An attribute is categorical if its domain size is less than this threshold.
        #self.threshold_value = 20
        self.threshold_value = threshold_value

        # specify categorical attributes
        #self.categorical_attributes = {'education': True}
        self.categorical_attributes = categorical_attributes

        # specify which attributes are candidate keys (or not keys) for input dataset.
        #self.candidate_keys = {'ssn': True}
        #self.candidate_keys = {'age': False}
        self.candidate_keys = candidate_keys

        if mode == "correlated_attribute_mode":
            # A parameter in differential privacy.
            # It roughly means that removing one tuple will change the probability of any output by  at most exp(epsilon).
            # Set epsilon=0 to turn off differential privacy.
            self.epsilon = epsilon

            # The maximum number of parents in Bayesian network, i.e., the maximum number of incoming edges.
            # self.degree_of_bayesian_network = 2
            self.degree_of_bayesian_network = degree_of_bayesian_network

        # Number of tuples generated in synthetic dataset.
        # self.num_tuples_to_generate = 10000 # Can be set to any integer.
        self.num_tuples_to_generate = num_tuples_to_generate # Can be set to any integer.

        self.save_faux_data_to_file = save_faux_data_to_file

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def fauxify(self, df_in=None, *args, **kwargs):

        from DataSynthesizer.DataDescriber import DataDescriber
        from DataSynthesizer.DataGenerator import DataGenerator
        from DataSynthesizer.ModelInspector import ModelInspector
        from DataSynthesizer.lib.utils import read_json_file, display_bayesian_network

        if df_in is None:
            warn_text = 'Input data frame is None.  This will cause the data describer to roll back to the '
            warn_text += 'file name in input_dataset.'
            warnings.warn(warn_text)
        else:
            self.df_in = df_in

        for key, value in kwargs.items():
            if   key == "mode":
                self.mode = value
            elif key == "threshold_value":
                self.threshold_value = value
            elif key == "categorical_attributes":
                self.categorical_attributes = value
            elif key == "candidate_keys":
                self.candidate_keys = value
            elif key == "num_tuples_to_generate":
                self.num_tuples_to_generate = value
            elif key == "save_faux_data_to_file":
                self.save_faux_data_to_file = value
            else:
                if self.verbose:
                    warnings.warn('Keyword argument', key, 'not used')

        # number of tuples generated same as input dataframe size if no value provided
        if self.num_tuples_to_generate is None or self.num_tuples_to_generate == 0:
            self.num_tuples_to_generate = len(self.df_in)

        # Below copied from example file
        self.description_file = './out/{}/description.txt'.format(self.mode)
        self.synthetic_data = './out/{}/sythetic_data.csv'.format(self.mode)

        describer = KFP_DataDescriber(df_in=self.df_in, category_threshold=self.threshold_value)
        generator = DataGenerator()

        # currently can't get correlated_attribute_mode to work, but leaving it here for now
        if self.mode == "correlated_attribute_mode":
            # this block prints a lot to stdout, suppress in non-verbose mode
            if self.verbose:
                print('using correlated_attribute_mode')
                describer.describe_dataset_in_correlated_attribute_mode(
                     describer.df_input,
                     epsilon = self.epsilon,
                     k = self.degree_of_bayesian_network,
                     attribute_to_is_categorical = self.categorical_attributes,
                     attribute_to_is_candidate_key = self.candidate_keys)
            else:
                with nostdout():
                     describer.describe_dataset_in_correlated_attribute_mode(
                          describer.df_input,
                          epsilon = self.epsilon,
                          k = self.degree_of_bayesian_network,
                          attribute_to_is_categorical = self.categorical_attributes,
                          attribute_to_is_candidate_key = self.candidate_keys)
            describer.save_dataset_description_to_file(self.description_file)
            generator.generate_dataset_in_correlated_attribute_mode(self.num_tuples_to_generate, self.description_file)
        elif self.mode == "independent_attribute_mode":
            print('using independent_attribute_mode')
            describer.describe_dataset_in_independent_attribute_mode(
                    describer.df_input,
                    attribute_to_is_categorical = self.categorical_attributes,
                    attribute_to_is_candidate_key = self.candidate_keys)
            describer.save_dataset_description_to_file(self.description_file)
            generator.generate_dataset_in_independent_mode(self.num_tuples_to_generate, self.description_file)

        if self.save_faux_data_to_file:
            generator.save_synthetic_data(self.synthetic_data)

        return generator.synthetic_dataset


####################################################################################################################################
####################################################################################################################################

class KDEPlugin(PandaPlugin):
    """ Constructs fake data using kernel density estimator based on input df. 
        Can either create column-wise data (i.e. ignore covariances) or
        table-wise data (take covariance of all columns into account)
    """

    def __init__(
            self,
            mode='correlated_attribute_mode',
            determine_factors=True,
            verbose=True,
            factor_threshold = 0.15,
            num_tuples_to_generate = None,
            *args,
            **kwargs):

        self.mode = mode
        self.determine_factors = determine_factors
        self.verbose = verbose
        self.factor_threshold = factor_threshold # if > this % are unique, assume it's NOT a factor
        self.num_tuples_to_generate = num_tuples_to_generate

        # switch to mode to make API consistent with DataSynthesizerPlugin
        for key, value in kwargs.items():
            if key == 'capture_covariance':
                warnings.warn('capture_covariance has been deprecated in favor of mode')
        
        PandaPlugin.__init__(self)

        # currently supported modes
        self.synthesis_modes = ('correlated_attribute_mode', 'independent_attribute_mode')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def fauxify(self, df_in=None, *args, **kwargs):
        
        if df_in is None:
            raise Exception('Input data frame not provided')
        else:
            self.df_in = df_in
            #if self.verbose:
            #    print(df_in.sample(10))

        self.preprocess = None
        self.refactorize = True
        
        for key, value in kwargs.items():
            if key == "factor_threshold":
                self.factor_threshold = value
            elif key == "num_tuples_to_generate":
                self.num_tuples_to_generate = value
            if key == "preprocess":
                self.preprocess = value
            if key == "refactorize":
                self.refactorize = value
            else:
                if self.verbose:
                    warnings.warn('Keyword argument', key, 'not used')

        if self.verbose:
            print('Preprocess', self.preprocess)

        # number of tuples generated same as input dataframe size if no value provided
        if self.num_tuples_to_generate is None or self.num_tuples_to_generate == 0:
            self.num_tuples_to_generate = len(self.df_in)
        print('num_tuples_to_generate:', self.num_tuples_to_generate)
            
        if self.mode == 'correlated_attribute_mode':
            return self.covar_kde(preprocess=self.preprocess)

        else:
            return self.column_kde()
        
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def column_kde(self):

        from numpy.random import choice
        from collections import Counter

        out_dict = dict()

        for col in self.df_in.columns:
            thistype = self.df_in[col].dtype

            if len(set(self.df_in[col]))/len(self.df_in[col]) < self.factor_threshold and self.determine_factors:
                thistype = 'object'

            if thistype == 'int64':
                if self.verbose:
                    print('Processing column ' + col + ' as ' + str(thistype))
                kd = stats.gaussian_kde(self.df_in[col], bw_method='silverman')
                # by default resample() should get correct size based on input, but for some reason
                # need to manually specify size
                out_dict[col] = np.int64(kd.resample(size=self.num_tuples_to_generate).ravel())

            elif thistype =='float64':
                if self.verbose:
                    print('Processing column ' + col + ' as a ' + str(thistype))
                kd = stats.gaussian_kde(self.df_in[col], bw_method='silverman')
                # by default resample() should get correct size based on input, but for some reason
                # need to manually specify size
                out_dict[col] = kd.resample(size=self.num_tuples_to_generate).ravel()

            else:
                if self.verbose:
                    print('Processing column ' + col + ' as a ' + str(thistype))

                colfact = self.df_in[col].factorize()
                cc=Counter(colfact[0])

                # convert from counts to proportions
                for key in cc:
                    cc[key] = cc[key] / len(self.df_in)

                elements = list(cc.keys())
                weights = list(cc.values())
                fakes = choice(elements,p=weights, replace=True, size=self.num_tuples_to_generate)
                out_dict[col] = [colfact[1][xx] for xx in fakes]

        self.out_dict = out_dict
        self.df_out = pd.DataFrame(out_dict)

        return self.df_out

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
    def covar_kde(self, preprocess=None, use_factors=True, verbose = True):
        '''Captures covariance between numerical columns'''

        df_in = self.df_in
        if preprocess is not None:
            df_in = preprocess(df_in)

        out_df = pd.DataFrame()
        factor_indices = dict()
        const_cols = dict()
        const_pos = dict()
        
        for col in df_in.columns:
            thistype = df_in[col].dtype

            if thistype in ['int64','float64']:
                out_df[col]=df_in[col]
            else:
                # treat everything else as factor
                if use_factors:
                    factors = pd.factorize(df_in[col])
                    out_df[col]=factors[0]
                    factor_indices[col] = factors[1]
        
        # stats.gaussian_kde cannot handle constant columns
        # drop them and add back after synthetic generation
        uniques = df_in.nunique()
        for i, v in uniques.iteritems():
            if v <= 1:
                const_cols[i] = out_df[i].iloc[0]
                const_pos[i] = out_df.columns.get_loc(i)
        out_df.drop(const_cols.keys(), axis=1, inplace=True)

        self.factor_indices = factor_indices
        df_num = pd.DataFrame(out_df).dropna()

        # Build KDE & resample
        if self.verbose:
            print('Building KDE Covariate Model')

        # For unobvious reasons, inputs to the gaussian_kde
        # are assumed to have variables as rows and samples
        # as columns, which is opposite to the DataFrame convention
        # This is corrected with the transpose() methods
        df_out = pd.DataFrame()
        try:
            kd = stats.gaussian_kde(df_num.transpose(), bw_method=.01)
            df_out = pd.DataFrame(kd.resample(size=self.num_tuples_to_generate).transpose(),columns = df_num.columns)
            
            # add back constants in original position
            # and convert factors back to original values
            for k in factor_indices.keys():
                if k in const_cols.keys():
                    df_out.insert(df_in.columns.get_loc(k), k, 0)
                if self.refactorize:
                    # first change to int so can convert back to original factor values
                    df_out[k] = df_out[k].round().abs().astype('int64')
                    # now need to apply factor to each of these columns
                    lookupdict = dict(zip(np.arange(len(factor_indices[k])), factor_indices[k]))
                    df_out[k].replace(lookupdict, inplace=True)
            # need to round variables that originally were integers back to integers
            if self.refactorize:
                orig_int_cols = list(df_in.select_dtypes(include=[int]).columns.values)
                df_out[orig_int_cols] = df_out[orig_int_cols].round().astype('int64')
        except np.linalg.LinAlgError as e:
            warnings.warn('Caught np.linalg.LinAlgError - Likely cause is that input dataframe too small for number of variables.')
            raise
                    
        self.df_out = df_out
        return self.df_out

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @property
    def capture_covariance(self):
        return self.mode == 'correlated_attribute_mode'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    @capture_covariance.setter
    def capture_covariance(self, value):
        warnings.warn('capture_covariance has been deprecated in favor of mode')
        if value:
            self.mode = 'correlated_attribute_mode'
        else:
            self.mode = 'independent_attribute_mode'
    
####################################################################################################################################
####################################################################################################################################

class KungFauxPandas(object):

    # To do:  Check to see if a column is unique (i.e. index) and recreate with unique < maybe use sample without replacement?>
    # if enabling logging, make sure database and required log table has been
    #   properly created - see create_logging_db.py
    def __init__(self, plugin=TrivialPlugin(), verbose=True, logging=True, db_file=None):

        self.verbose = verbose
        self.seed = 10293510
        self.plugin = plugin
        self.synthesis_methods = ('Trivial', 'KDE', 'DataSynthesizer')
        if db_file is None:
            self.db_file = '../../data/kfp_log.db'
        else:
            self.db_file = db_file
        self.logging = logging

        if self.logging:
            self.logging_conn = sqlite3.connect(self.db_file)
            self.logging_cur = self.logging_conn.cursor()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def read_sql(self, sql, conn, **kwargs):

        self.sql = sql
        self.conn = conn

        if(self.logging):
            query_start = datetime.datetime.now()
        self.df_in = pd.read_sql(self.sql, self.conn, **kwargs)
        if(self.logging):
            query_end = datetime.datetime.now()
        try:
            self.df_out = self.plugin.fauxify(self.df_in)
        except Exception as e:
            print('kungfauxpandas.read_sql() exception while attempting to fauxify data:', e)
            raise
        if(self.logging):
            fauxify_end = datetime.datetime.now()

            try:
                sql = '''
                    INSERT INTO kfp_log(
                        query,
                        query_start,
                        query_end,
                        query_result,
                        faux_method,
                        fauxify_start,
                        fauxify_end,
                        faux_result
                        )
                    VALUES(?,?,?,?,?,?,?,?)
                    '''
                self.logging_cur.execute(sql, (
                    self.sql,
                    query_start,
                    query_end,
                    self.df_in.to_json(),
                    type(self.plugin).__name__,
                    query_end,
                    fauxify_end,
                    self.df_out.to_json()
                ))
                self.logging_conn.commit()
            except Exception as e:
                print('kungfauxpandas.py read_sql Exception:', e)

        return self.df_out

####################################################################################################################################
####################################################################################################################################

class KFP_DataDescriber(DataDescriber):
    """An extension of DataDescriber which bypasses reading the csv file and uses a
    Pandas data frame derived from any source (typically a RDBMS)

    To use an already-loaded data set, set the df_in attribute on instantiation
      OR set df_in=theDataFrame after."""


    def __init__(self, *args, df_in = None, verbose=True, **kwargs):

        self.verbose = verbose
        self.df_in = df_in
        DataDescriber.__init__(self, *args, **kwargs)


    def read_dataset_from_csv(self, file_name=None):
        """Redirect this method to just populate self.df_input
        with the already-read data frame"""

        if self.df_in is not None:
            self.link_loaded_dataset()
        else:
            # This will call the parent-class read_dataset_from_csv
            # function which populates self.df_input with a pandas
            # dataframe

            super(KFP_DataDescriber, self).read_dataset_from_csv(file_name)

    def link_loaded_dataset(self):

        if self.verbose:
            print('Skipping read from csv and returning the input data frame')

        self.df_input = self.df_in

####################################################################################################################################
####################################################################################################################################
# code courtesy of https://stackoverflow.com/questions/2828953/silence-the-stdout-of-a-function-in-python-without-trashing-sys-stdout-and-resto?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
class DummyFile(object):
    def write(self, x): pass

@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = DummyFile()
    yield
    sys.stdout = save_stdout

####################################################################################################################################
####################################################################################################################################
####################################################################################################################################


def main():

    dbname = '/opt/processed_data/sepsis.db'
    conn = fakelite.connect(dbname)

    sql = """
        SELECT "diag"."SubjectId",
                 "diag"."EncounterId",
                 MAX("diag"."SepsisDiagnosis") as Septic,
                 MAX("FlowsheetValue") AS MaxScore,
                 AVG("FlowsheetValue") AS MeanScore,
                 MIN("FlowsheetValue") AS MinScore,
                 COUNT("FlowsheetValue") AS NumLoggedScores

         FROM "diag"
         LEFT JOIN "flow_edss"
         ON "diag"."EncounterId"="flow_edss"."EncounterId"
         GROUP BY "flow_edss"."EncounterId"
         ORDER BY NumLoggedScores DESC
    """
