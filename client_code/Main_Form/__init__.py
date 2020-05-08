from ._anvil_designer import Main_FormTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import plotly.graph_objects as go
import anvil.server
from SalePrediction.Form1 import Form1
from SalePrediction.Form2 import Form2
from SalePrediction.Form3 import Form3
from SalePrediction.Form4 import Form4
from SalePrediction.Form5 import Form5

class Main_Form(Main_FormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    
    form1_instance = Form1(param='an_argument')
    self.flow_panel_1.clear()
    self.flow_panel_1.add_component(form1_instance)
    self.button_1.tag = form1_instance

    form2_instance = Form2(param='an_argument')
    self.button_2.tag = form2_instance
    
    form3_instance = Form3(param='an_argument')
    self.button_3.tag = form3_instance
    
    form4_instance = Form4(param='an_argument')
    self.button_4.tag = form4_instance

    form5_instance = Form5(param='an_argument')
    self.button_5.tag = form5_instance
    

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    form1 = get_open_form().button_1.tag
    get_open_form().flow_panel_1.clear()
    get_open_form().flow_panel_1.add_component(form1)    
    pass

  def button_2_click(self, **event_args):
    """This method is called when the button is clicked"""
    form2 = get_open_form().button_2.tag
    get_open_form().flow_panel_1.clear()
    get_open_form().flow_panel_1.add_component(form2)    
    pass

  def button_3_click(self, **event_args):
    """This method is called when the button is clicked"""
    form3 = get_open_form().button_3.tag
    get_open_form().flow_panel_1.clear()
    get_open_form().flow_panel_1.add_component(form3)    
    pass

  def button_4_click(self, **event_args):
    """This method is called when the button is clicked"""
    form4 = get_open_form().button_4.tag
    get_open_form().flow_panel_1.clear()
    get_open_form().flow_panel_1.add_component(form4)    
    pass
  
  def button_5_click(self, **event_args):
    """This method is called when the button is clicked"""
    form5 = get_open_form().button_5.tag
    get_open_form().flow_panel_1.clear()
    get_open_form().flow_panel_1.add_component(form5)    
    pass



