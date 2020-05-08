from ._anvil_designer import Form2Template
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
import anvil.server
from SalePrediction import Globals

class Form2(Form2Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    dic = anvil.server.call('loadcsv',"/sale.csv")
    self.repeating_panel_1.items = dic

  def demo_click(self, **event_args):
    """This method is called when the button is clicked"""
    dic = anvil.server.call('loadcsv',"/sale.csv")
    self.repeating_panel_1.items = dic
    Globals.is_demo = True
    pass

  def file_loader_1_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    size = len(file.get_bytes())
    # alert(size)
    if size > 100000:
      alert("Size is bigger than 100kb !!!")
      return
    
    dic = anvil.server.call("importcsv", file)
    self.repeating_panel_1.items = dic
    Globals.is_demo = False
    
    pass



