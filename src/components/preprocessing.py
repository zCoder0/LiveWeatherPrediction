import requests 
import os
import sys
from src.exception.custom_exception import ProjectException
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
class Preprocessing:
    
    def __init__(self):
        try:
            path = os.path.join('src\data_set', os.listdir('src/data_set')[0])
            self.weather_data = pd.read_csv(path,encoding='latin1')
            
        except Exception as e:
            ProjectException(e,sys)
    
    def get_columns_name(self,df):
        object_columns=[]
        numeric_col=[]
        date_col=[]
        category_col=[]
        
        for i in df.columns:
            if df[i].dtype=='object':
                object_columns.append(i)
            elif df[i].dtype=='category':
                category_col.append(i)
            elif df[i].dtype=='datetime64[ns]':
                date_col.append(i)
            else:
                numeric_col.append(i)
                
        return object_columns,numeric_col,date_col,category_col
        
    def featureEngineering(self):
        try:
            # Convert to DateTime
            df=self.weather_data.copy()
            
            df['DateTime'] = pd.to_datetime(df['DateTime'])
            df['Month'] =df['DateTime'].dt.month
            df['Day'] =df['DateTime'].dt.day
            df['WeekDay'] =df['DateTime'].dt.day_of_week
            df['Hour'] =df['DateTime'].dt.hour
            df['Feels_Muggy'] = ((df['Humidity'] > 65) & (df['Temperature (F)'] > 75)).astype(int)
            return df
        
        except Exception as e:
            ProjectException(e,sys)
            
            
    def select_features(self,df,features:list):
        try:
            
            df_features = df.loc[: ,features ]
            return df_features
        except Exception as e:
            ProjectException(e,sys)
        
    def scalling_feature(self,df_features):
        min_max_scale = MinMaxScaler()
        scaled_features = min_max_scale.fit_transform(df_features)
        return scaled_features , min_max_scale
     
    def split_X_y(self,scaled_features,time_step=10):
        X, y = [], []
        X, y = [], []

        for i in range(time_step, len(scaled_features)):
            X.append(scaled_features[i-time_step:i])  # n days of 7 features
            y.append(scaled_features[i][0])  # Temperature is at index 0

        X, y = np.array(X), np.array(y)

        return X, y