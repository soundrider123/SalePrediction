from ._anvil_designer import Form4Template
from anvil import *
import plotly.graph_objects as go
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from plotly import graph_objs as go
from SalePrediction import Globals

class Form4(Form4Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def form_show(self, **event_args):
    """This method is called when the column panel is shown on the screen"""
    self.label_2.text = Globals.rmse
    
    x_month = Globals.x_month
    item_lst = Globals.item_lst
    data_lst = Globals.data_lst
      
    colors = ['Red', 'Green','Blue',  'Yellow', 'Brown']
    plot_data = list()
    
    for i in range(len(data_lst)):
        scatter = go.Scatter(
          x = x_month,
          y = data_lst[i],
          name=str(item_lst[i]),
          marker = go.Marker(
            color= colors[i]
          )
        )
        plot_data.append(scatter)
      
    self.plot_2.data = plot_data
    
    pass



