
####################################################################################################################################
####################################################################################################################################

from KungFauxPandas.PandaPlugin import PandaPlugin as PandaPlug 

class TrivialPlugin(PandaPlug):
    """ Returns the input as output. 
	
	Shows a basic example to build your own plugin"""

    def __init__(self):
        #PandaPlugin.__init__(self)
        super(PandaPlugin,self).__init__()


    def fauxify(self, df_in=None):
        if df_in is not None:
            self.df_in = df_in


	# To make this non-trivial, do something cool and save the results as self.df_out
	#
	# self.df_out = coolstuff.something_cool(df_in)

        self.df_out = self.df_in

        return self.df_out

####################################################################################################################################
