### Bokeh Reactive Power Explorer Application
### Written By: Jacob Marsnik, Consulting Engineers Group
### Last Updated: 07/03/2019

#imports and initializations
import param
import panel as pn
import pandas as pd
import hvplot.pandas
import holoviews as hv
from holoviews.plotting.links import RangeToolLink
from holoviews.streams import Params, Pipe, Buffer
import datetime as dt
from bokeh.server.server import Server
hv.extension('bokeh')
pn.extension()

###-----------------------------------------------------------------------###
###------------------------PARAMETER DEFAULTS-----------------------------###
### This section contains defaults and ranges for the Bokeh controls and  ###
### may be modified without concern, if required. ("View" Part 1)         ###
###-----------------------------------------------------------------------###

default_start_date = dt.datetime(2017, 1, 1)
default_end_date = dt.datetime(2018, 1, 30)
bound_start_date = dt.datetime(2017, 1, 1)
bound_end_date = dt.datetime(2018, 1, 30)
default_inverter = 'INV 1A'
default_variable = 'Watts'
width = 600
line_width = 0.25
framewise = True

###-----------------------------------------------------------------------###
###----------------------GRAPHICAL USER INTERFACE-------------------------###
### This code defines the Bokeh controls that are used for the user       ###
### interface. All the defaults for the controls are above. This code     ###
### should not need to be modified. ("View" Part 2)                       ### 
###-----------------------------------------------------------------------###

#this is covered by our explorer class
idx = pd.IndexSlice
#bring the data in from the csv
combined_df = pd.read_csv('data/combined_reactive_data.csv')
combined_df['Timestamp'] = pd.to_datetime(combined_df['Timestamp'])
grouped_df = pd.DataFrame(combined_df.groupby(['Inverter', 'Timestamp']).sum())
class ReactiveExplorer(param.Parameterized):
    date_range = param.DateRange(
        default=(default_start_date, default_end_date), 
        bounds=(bound_start_date, bound_end_date))
    inverter = param.ObjectSelector(default=default_inverter, objects=['INV 1A', 'INV 1B', 'INV 2A', 'INV 2B'])
    variable = param.ObjectSelector(default=default_variable, objects=['Watts', 'VA', 'VAR'])
    
    @param.depends('date_range', 'inverter', 'variable')
    def load_inverter(self):
        df = grouped_df.loc[idx[self.inverter, self.date_range[0]:self.date_range[1]], :]
        curve = hv.Curve(df[self.variable], 'Timestamp').opts(width=600, line_width=0.25)
        return curve

###-----------------------------------------------------------------------###
###------------------DATA SOURCES AND INITIALIZATION----------------------###
### This section defines the data sources which will be used in the Bokeh ###
### plots. To update a Bokeh plot in the server, each of the sources will ###
### be modified in the CALLBACKS section. ("Model")                       ###
###-----------------------------------------------------------------------###

explorer = ReactiveExplorer()
dmap = hv.DynamicMap(explorer.load_inverter)
panel = pn.Row(explorer.param, dmap)
panel = panel.servable()



