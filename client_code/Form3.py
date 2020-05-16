from ._anvil_designer import Form3Template
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
import anvil.server
from SalePrediction import Globals

class Form3(Form3Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    self.task = None
    # Any code you write here will run when the form opens.
    self.button_1.enabled = True  
    self.button_2.enabled = False  
    
    filename = "/sale1.csv"
    dic = anvil.server.call('infocsv',filename)
    self.repeating_panel_1.items = dic    

  def gridrefresh(self):
    """This method is called when the column panel is shown on the screen"""
    filename = "/saletmp.csv"
    if Globals.is_demo == True:
      filename = "/sale1.csv"
    dic = anvil.server.call('infocsv',filename)
    self.repeating_panel_1.items = dic
    pass    

  def predict_click(self, **event_args):
    """This method is called when the button is clicked"""
    #Globals.is_calced = False
    
    filename = "/saletmp.csv"
    if Globals.is_demo == True:
      filename = "/sale.csv"

    method = "randomforest"
    if self.radio_button_1.selected:
      method = "randomforest"
    else:
      method = "linear"
    self.task = anvil.server.call('build_model',filename, method)
    self.timer_1.interval = 0.5

    self.button_1.enabled = False
    self.button_2.enabled = True
    
    pass

  def stop_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.task == None:
      return
    else:
      anvil.server.call('kill_task', self.task)
    self.button_1.enabled = True  
    self.button_2.enabled = False  
    pass

  def timer_1_tick(self, **event_args):
    """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
    with anvil.server.no_loading_indicator:
      # Show progress
      state = self.task.get_state()
      n_complete = state.get('n_complete', 0)
      self.label_1.text = n_complete
  
      # Switch Timer off if process is complete
      if not self.task.is_running():
        self.timer_1.interval = 0  

        x_month, item_lst, data_lst, target, rmse = self.task.get_return_value()
        
        Globals.x_month = x_month
        Globals.item_lst = item_lst
        Globals.data_lst = data_lst
        Globals.target = target
        Globals.rmse = rmse
        Globals.is_calced = True
        
        self.button_1.enabled = True  
        self.button_2.enabled = False          
        get_open_form().button_4.raise_event('click')
            





