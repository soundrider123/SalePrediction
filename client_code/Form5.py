from ._anvil_designer import Form5Template
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
import anvil.server
from SalePrediction import Globals

class Form5(Form5Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.


  def form_show(self, **event_args):
    """This method is called when the column panel is shown on the screen"""
    target = Globals.target
    self.repeating_panel_1.items = target      
    pass





