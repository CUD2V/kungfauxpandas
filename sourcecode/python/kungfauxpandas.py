
import pandas as pd
import numpy as np
import scipy.stats as stats
import sys
import warnings
import datetime
import sqlite3

library_location = '../../plugins/DataSynthesizer'
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
    """ Constructs column-wise (i.e. ignore covariances) fake data based on input df. """

    def __init__(self, df_in=None,
            mode = 'correlated_attribute_mode',
            threshold_value = 20,
            categorical_attributes = {},
            candidate_keys = {},
            epsilon = 0.1,
            degree_of_bayesian_network = 2,
            num_tuples_to_generate = None,
            save_faux_data_to_file = False):

        PandaPlugin.__init__(self)

        self.mode = mode

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
            # It roughtly means that removing one tuple will change the probability of any output by  at most exp(epsilon).
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
                self.save_faux_data_to_file = vale
            else:
                if self.verbose:
                    warnings.warn('Keyword argument', key, 'not used')

        # for now, override tuples generated to be same as input dataframe
        self.num_tuples_to_generate = len(self.df_in)

        # Below copied from example file
        self.description_file = './out/{}/description.txt'.format(self.mode)
        self.synthetic_data = './out/{}/sythetic_data.csv'.format(self.mode)

        describer = KFP_DataDescriber(df_in=self.df_in, threshold_of_categorical_variable=self.threshold_value)
        generator = DataGenerator()

        # currently can't get correlated_attribute_mode to work, but leaving it here for now
        if self.mode == "correlated_attribute_mode":
            describer.describe_dataset_in_correlated_attribute_mode(
                 describer.input_dataset,
                 epsilon = self.epsilon,
                 k = self.degree_of_bayesian_network,
                 attribute_to_is_categorical = self.categorical_attributes,
                 attribute_to_is_candidate_key = self.candidate_keys)
            describer.save_dataset_description_to_file(self.description_file)
            generator.generate_dataset_in_correlated_attribute_mode(self.num_tuples_to_generate, self.description_file)
        elif self.mode == "independent_attribute_mode":
            describer.describe_dataset_in_independent_attribute_mode(
                    describer.input_dataset,
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
    """ Constructs column-wise (i.e. ignore covariances) fake data based on input df. """

    def __init__(self, verbose=True):
        self.verbose = verbose
        PandaPlugin.__init__(self)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def fauxify(self, df_in=None, *args, **kwargs):

        self.df_in = df_in

        self.factor_threshold = 0.15 # if > this % are unique, assume it's NOT a factor
        self.determine_factors = True

        for key, value in kwargs.items():

            if key == "factor_threshold":
                self.factor_threshold = value

            elif key == "determine_factors":
                self.determine_factors = True

            else:
                if self.verbose:
                    warnings.warn('Keyword argument', key, 'not used')

        # sets self.df_out
        self.column_kde()

        return self.df_out

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
                    print('Processing column ' + col + ' as a ' + str(thistype))
                kd = stats.gaussian_kde(self.df_in[col], bw_method='silverman')
                out_dict[col] = np.int64(kd.resample().ravel())

            elif thistype =='float64':
                if self.verbose:
                    print('Processing column ' + col + ' as a ' + str(thistype))
                kd = stats.gaussian_kde(self.df_in[col], bw_method='silverman')
                out_dict[col] = kd.resample().ravel()

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
                fakes = choice(elements,p=weights, replace=True, size=len(self.df_in))
                out_dict[col] = [colfact[1][xx] for xx in fakes]

        self.out_dict = out_dict
        self.df_out = pd.DataFrame(out_dict)

        return self.df_out

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
    Pandas data frame derived from any source (typically a RDMS)

    To use an already-loaded data set, set the df_in attribute on instantiation
      OR set df_in=theDataFrame after."""


    def __init__(self, *args, df_in = None, verbose=True, **kwargs):

        self.verbose = verbose
        self.df_in = df_in
        DataDescriber.__init__(self, *args, **kwargs)


    def read_dataset_from_csv(self, file_name=None):
        """Redirect this method to just populate self.input_dataset
        with the already-read data frame"""

        if self.df_in is not None:
            self.link_loaded_dataset()
        else:
            # This will call the parent-class read_dataset_from_csv
            # function wich populates self.input_dataset with a pandas
            # dataframe

            super(KFP_DataDescriber, self).read_dataset_from_csv(file_name)

    def link_loaded_dataset(self):

        if self.verbose:
            print('Skipping read from csv and returing the input data frame')

        self.input_dataset = self.df_in

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
