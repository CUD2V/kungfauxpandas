
####################################################################################################################################
####################################################################################################################################

class PandaPlugin(object):

    def __init__(self, df_in = None):
        self.df_in = df_in

    def fauxify(self, df_in=None):
        """All plugins need to overload this fauxify method which takes a pandas data frame
        and returns a faux-data data frame."""

        print('This is a template--use it to make a plugin')


####################################################################################################################################
