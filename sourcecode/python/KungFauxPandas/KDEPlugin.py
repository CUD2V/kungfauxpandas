
####################################################################################################################################
####################################################################################################################################

#from KungFauxPandas import *
from KungFauxPandas import PandaPlugin 

class KDEPlugin(PandaPlugin):
    """ Constructs column-wise (i.e. ignore covariances) fake data based on input df. """
    
    import pandas as pd
    import numpy as np
    import scipy.stats as stats
    import sys
    import warnings


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
