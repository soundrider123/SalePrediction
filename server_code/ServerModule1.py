import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import pandas as pd
from itertools import product
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import datetime

@anvil.server.callable
def importcsv(file):
  my_string = file.get_bytes().decode(encoding='UTF-8')
  with open('/saletmp.csv', 'w+') as f:
    f.write(my_string)
  df = pd.read_csv('/saletmp.csv', delimiter=',')
  return df.to_dict(orient="records")
    

@anvil.server.callable
def loadcsv(filename):
  df = pd.read_csv(filename, delimiter=',')
  df = df[['date_str','item_id','item_cnt_day']]
  return df.to_dict(orient="records")

@anvil.server.callable
def infocsv(filename):
  df = pd.read_csv(filename, delimiter=',')
  df_info  = pd.DataFrame(columns = ['description', 'value'])
  df_info = df_info.append({'description':'Total row number','value':df.shape[0]},ignore_index=True)
  np_array = pd.unique(df['date_str'].str[0:7])
  df_info = df_info.append({'description':'Total months','value':np_array.size},ignore_index=True)
  np_array = pd.unique(df['item_id'])
  df_info = df_info.append({'description':'Total item_id','value':np_array.size},ignore_index=True)
  
  return df_info.to_dict(orient="records")

@anvil.server.background_task
def build_model_task(filename, method):
  anvil.server.task_state['n_complete'] = 1
  
  train = pd.read_csv(filename, delimiter=',')
  train['date_month'] = train['date_str'].str[0:7]
  dates = np.sort(train['date_month'].unique())
  df_dates = pd.DataFrame(dates, columns=['date_month'])
  df_dates['date_block_num'] = df_dates.index + 1
  train = pd.merge(train, df_dates,  how='inner', left_on=['date_month'], right_on = ['date_month'])
  
  anvil.server.task_state['n_complete'] = 2
  matrix = []
  cols = ['date_block_num','item_id']
  item_ids = train.item_id.unique()
  for i in range(1, df_dates.shape[0]+2):
      matrix.append(np.array(list(product([i], item_ids)), dtype='int16'))
      
  matrix = pd.DataFrame(np.vstack(matrix), columns=cols)
  #item_cnt_month
  group = train.groupby(['date_block_num','item_id']).agg({'item_cnt_day': ['sum']})
  group.columns = ['item_cnt_month']
  group.reset_index(inplace=True)
  matrix = pd.merge(matrix, group, on=cols, how='left')
  matrix['item_cnt_month'] = (matrix['item_cnt_month']
                                .fillna(0)
                                .astype(np.float16))
  
  matrix.fillna(0, inplace=True)
  
  def lag_feature(df, lags, col):
    tmp = df[['date_block_num','item_id',col]]
    for i in lags:
        shifted = tmp.copy()
        shifted.columns = ['date_block_num','item_id', col+'_lag_'+str(i)]
        shifted['date_block_num'] += i
        df = pd.merge(df, shifted, on=['date_block_num','item_id'], how='left')
    return df
  
  matrix = lag_feature(matrix, [1,2,3,6,12], 'item_cnt_month')
  
  anvil.server.task_state['n_complete'] = 3
  #window by three month
  matrix['item_cnt_mean'] = matrix.sort_values(['item_id', 'date_block_num'])['item_cnt_month'].rolling(3).mean()
  matrix['item_cnt_min'] = matrix.sort_values(['item_id', 'date_block_num'])['item_cnt_month'].rolling(3).min()
  matrix['item_cnt_max'] = matrix.sort_values(['item_id', 'date_block_num'])['item_cnt_month'].rolling(3).max()
  matrix['item_cnt_std'] = matrix.sort_values(['item_id', 'date_block_num'])['item_cnt_month'].rolling(3).std()
  
  #date_avg_item_cnt
  group = matrix.groupby(['date_block_num']).agg({'item_cnt_month': ['mean']})
  group.columns = [ 'date_avg_item_cnt' ]
  group.reset_index(inplace=True)
  
  matrix = pd.merge(matrix, group, on=['date_block_num'], how='left')
  matrix['date_avg_item_cnt'] = matrix['date_avg_item_cnt'].astype(np.float16)
  matrix = lag_feature(matrix, [1,2,3], 'date_avg_item_cnt')
  matrix.drop(['date_avg_item_cnt'], axis=1, inplace=True)
  
  def fill_na(df):
    for col in df.columns:
        if ('_lag_' in col) & (df[col].isnull().any()):
            if ('item_cnt' in col):
                df[col].fillna(0, inplace=True)         
    return df
  
  matrix = fill_na(matrix)
  
  
  anvil.server.task_state['n_complete'] = 4
  data = matrix[[
      'date_block_num',
      'item_id',
      'item_cnt_month',
      'item_cnt_month_lag_1',
      'item_cnt_month_lag_2',
      'item_cnt_month_lag_3',
      'item_cnt_month_lag_6',
      'item_cnt_month_lag_12',
      'item_cnt_min',             
      'item_cnt_mean',            
      'item_cnt_max',           
      'item_cnt_std',
      'date_avg_item_cnt_lag_1',
      'date_avg_item_cnt_lag_2',
      'date_avg_item_cnt_lag_3'
      ]]  

  data = data[data.date_block_num > 11]
  month_len = df_dates.shape[0]
  target_month = month_len + 1
  
  anvil.server.task_state['n_complete'] = 5
  X_train = data[data.date_block_num < month_len].drop(['item_cnt_month'], axis=1)
  Y_train = data[data.date_block_num < month_len]['item_cnt_month']
  X_valid = data[data.date_block_num == month_len].drop(['item_cnt_month'], axis=1)
  Y_valid = data[data.date_block_num == month_len]['item_cnt_month']
  X_test = data[data.date_block_num == target_month].drop(['item_cnt_month'], axis=1)
  
  anvil.server.task_state['n_complete'] = 6
  regr = RandomForestRegressor(n_estimators=1000, random_state=1)
  if method == "linear":
    regr = LinearRegression()
    
  anvil.server.task_state['n_complete'] = 7
  regr.fit(X_train, Y_train)  
 
  anvil.server.task_state['n_complete'] = 8
  y_pred_valid = regr.predict(X_valid)
  y_pred_valid_df = pd.DataFrame(y_pred_valid)
  rmse = np.sqrt(mean_squared_error(Y_valid, y_pred_valid_df[0]))  
  
  Y_test = regr.predict(X_test)
  
  anvil.server.task_state['n_complete'] = 9
  target = pd.DataFrame({
    "date_block_num": X_test.date_block_num, 
    "item_id": X_test.item_id, 
    "item_cnt_month": Y_test
  })
  
  data = data[data.date_block_num <= month_len]
  data = data[['date_block_num', 'item_id', 'item_cnt_month']]

  #####################################################################################
  ## preparing data for plotty chart as x:month, y:item_cnt_month with predicted month
  #####################################################################################
  anvil.server.task_state['n_complete'] = 10

  #date_month
  data = pd.merge(data, df_dates,  how='inner', left_on=['date_block_num'], right_on = ['date_block_num'])
  
  #target_month
  max_date = str(df_dates['date_month'].max()) + '-01'
  max_date_dt = datetime.datetime.strptime(max_date, '%Y-%m-%d')
  next_month = datetime.datetime(max_date_dt.year + int(max_date_dt.month / 12), ((max_date_dt.month % 12) + 1), 1)
  target_month = next_month.strftime('%Y-%m')
  target['date_month'] = target_month
  
  anvil.server.task_state['n_complete'] = 11
  
  target = target[['date_month', 'item_id', 'item_cnt_month']]
  data = data[['date_month', 'item_id', 'item_cnt_month']]
  
  data = pd.concat([data, target], ignore_index=True, sort=False, keys=cols)
  data = data.sort_values(['date_month', 'item_id'])
  
  data_lst = list()
  item_lst = list()
  for item_id in data.item_id.unique():
    item_lst.append(item_id) 
    data_lst.append(list(data.loc[data.item_id == item_id, 'item_cnt_month'].values))
  
  data['date_month'] = data['date_month'].str.replace('-', '_')
  x_month = list(np.unique(data['date_month'].values))
  return x_month, item_lst, data_lst, target.to_dict(orient="records"), rmse

@anvil.server.callable
def build_model(filename, method):
  task = anvil.server.launch_background_task('build_model_task', filename, method)
  return task

@anvil.server.callable
def kill_task(task):
  task.kill()
  
