
import sqlite3
import pandas as pd
import numpy as np
from numpy.random import choice
import scipy.stats as stats
from collections import Counter

class KungFauxPandas():

    # To do:  Check to see if a column is unique (i.e. index) and recreate with unique < maybe use sample without replacement?>

    def __init__(self, density_depth='column', verbose=True):

        self.verbose = verbose
        self.seed = 102935104
        self.density_depth = density_depth # ('column', 'table', 'join')
        # if # of unique values is small compared to number of records,
        # assume it's a factor
        self.determine_factors = True
        self.factor_threshold = 0.15
        self.synthesis_methods = ('sgf', 'kde', 'datasynthesizer')

    def read_sql(self, sql, conn, method_type):
        self.sql = sql
        self.conn = conn
        self.df = pd.read_sql(self.sql, self.conn)

        if self.density_depth == 'column':
            self.column_kde()
            return self.fdf

        elif self.type == 'KDE':
            #d0 = df.iloc[:,[0,1,2,3,4]].transpose()
            kd = stats.gaussian_kde(self.df, bw_method='silverman')
            dnew = dict(zip(self.df.columns, kd.resample()))


    def column_kde(self):
        out_dict = dict()

        for col in self.df.columns:
            thistype = self.df[col].dtype

            if len(set(self.df[col]))/len(self.df[col]) < self.factor_threshold and self.determine_factors:
                thistype = 'object'

            if thistype == 'int64':
                if self.verbose:
                    print('Processing column ' + col + ' as a ' + str(thistype))
                kd = stats.gaussian_kde(self.df[col], bw_method='silverman')
                out_dict[col] = np.int64(kd.resample().ravel())

            elif thistype =='float64':
                if self.verbose:
                    print('Processing column ' + col + ' as a ' + str(thistype))
                kd = stats.gaussian_kde(self.df[col], bw_method='silverman')
                out_dict[col] = kd.resample().ravel()

            else:
                if self.verbose:
                    print('Processing column ' + col + ' as a ' + str(thistype))

                colfact = self.df[col].factorize()
                cc=Counter(colfact[0])

                # convert from counts to proportions
                for key in cc:
                    cc[key] = cc[key] / len(self.df)

                elements = list(cc.keys())
                weights = list(cc.values())
                fakes = choice(elements,p=weights, replace=True, size=len(self.df))
                out_dict[col] = [colfact[1][xx] for xx in fakes]

        self.out_dict = out_dict
        self.fdf = pd.DataFrame(out_dict)

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
