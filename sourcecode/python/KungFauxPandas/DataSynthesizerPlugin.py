
import pandas as pd
import numpy as np
import scipy.stats as stats
import sys
import warnings

try:
    library_location = '../../plugins/DataSynthesizer'
    sys.path.append(library_location)
    from DataSynthesizer.DataDescriber import DataDescriber

except Exception as e:
    warnings.warn('DataSynthesizer source code appears to be absent.  This module will not function')


from KungFauxPandas import PandaPlugin


####################################################################################################################################
####################################################################################################################################

class DataSynthesizerPlugin(PandaPlugin):
    """ uses methods from <authors>'s Data Synthsizer to fauxify data """

    def __init__(self, df_in=None,
            mode = 'correlated_attribute_mode',
            threshold_value = 0.1,
            categorical_attributes = {},
            candidate_keys = {},
            epsilon = 0.1,
            degree_of_bayesian_network = 2,
            num_tuples_to_generate = 1000):

        PandaPlugin.__init__(self)

        self.mode = mode

        # An attribute is categorical if its domain size is less than this threshold.
        #self.threshold_value = 20
        self.threshold_value = threshold_value

        # specify categorical attributes
        #self.categorical_attributes = {'education': True}
        self.categorical_attributes = categorical_attributes

        # specify which attributes are candidate keys of input dataset.
        #self.candidate_keys = {'ssn': True}
        self.candidate_keys = candidate_keys

        # A parameter in differential privacy.
        # It roughtly means that removing one tuple will change the probability of any output by  at most exp(epsilon).
        # Set epsilon=0 to turn off differential privacy.
        self.epsilon = epsilon

        # The maximum number of parents in Bayesian network, i.e., the maximum number of incoming edges.
        # self.degree_of_bayesian_network = 2
        self.degree_of_bayesian_network = degree_of_bayesian_network

        # Number of tuples generated in synthetic dataset.
        # self.num_tuples_to_generate = 10000 # Can be set to any integer.
        self.num_tuples_to_generate = num_tuples_to_generate# Can be set to any integer.



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


        # Below copied from example file
        self.description_file = './out/{}/description.txt'.format(self.mode)
        self.synthetic_data = './out/{}/sythetic_data.csv'.format(self.mode)

        describer = KFP_DataDescriber(df_in=self.df_in, threshold_of_categorical_variable=self.threshold_value)

        describer.describe_dataset_in_correlated_attribute_mode(
                describer.input_dataset,
                epsilon = self.epsilon,
                k = self.degree_of_bayesian_network,
                attribute_to_is_categorical = self.categorical_attributes,
                attribute_to_is_candidate_key = self.candidate_keys)

        describer.save_dataset_description_to_file(self.description_file)

        generator = DataGenerator()
        generator.generate_dataset_in_correlated_attribute_mode(self.num_tuples_to_generate, self.description_file)

        if self.save_faux_data_to_file:
            generator.save_synthetic_data(self.synthetic_data)

        return self.synthetic_data


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
