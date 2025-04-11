from src.components.preprocessing import Preprocessing
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from  datetime import datetime as dtime
import sys
from src.exception.custom_exception import ProjectException
import numpy as np

class BuildModel:
    def __init__(self,X,y, input_shape:tuple, output_shape=1,num_units=64):
        
        self.lstm_model =Sequential()
        self.lstm_model.add(LSTM(units=num_units, return_sequences=True, input_shape=input_shape))
        self.lstm_model.add(LSTM(units=num_units,return_sequences=True))
        self.lstm_model.add(LSTM(num_units))
        self.lstm_model.add(Dense(output_shape))
        self.lstm_model.compile(optimizer='adam', loss='mse' ,metrics=['mae','mape'])
        history = self.lstm_model.fit(X, y, epochs=3, batch_size=16)
    
    
    def test_data(self,df):
        test = df.loc[: , ['DateTime','Temperature (C)','Humidity','Wind (kph)','Pressure (mb)','Month','Hour','Feels_Muggy']]
        test.set_index('DateTime',inplace=True)

        test = test.resample('h').mean().dropna()
        print(test)
        return test
    
    def split_test_data(self,test,date = dtime.now()):
        try:
            
            cur_date = date.strftime("%Y-%m-%d")
            
            test2= test.loc['2025-04-01' : f"{cur_date} 23:00:00"]
            
            # Morning: 5AM to 11AM
            morning = test2[(test2['Hour'] >= 5) & (test2['Hour'] < 12)]
            # Afternoon: 12PM to 3PM
            afternoon = test2[(test2['Hour'] >= 12) & (test2['Hour'] < 15)]
            # Evening: 4PM to 7PM
            evening = test2[(test2['Hour'] >= 16) & (test2['Hour'] < 19)]
            # Night: 8PM to 23 AM (split into two parts for proper logic)
            night = test2[(test2['Hour'] >= 20) | (test2['Hour'] < 5)]
            
            return morning,afternoon,evening,night
        except Exception as e:
            print(e)
            ProjectException(e,sys)
    
    def predict_next_day(self,test,name,min_max_scale,features):
        scaled_data = min_max_scale.transform(test)
        scaled = np.array(scaled_data).reshape(1, len(test), len(features))
        pred_scaled = self.lstm_model.predict(scaled)
        dummy_row = [pred_scaled[0][0]] + [0]*(len(features) - 1)
        pred_temp = min_max_scale.inverse_transform([dummy_row])[0][0]
        return pred_temp ,name
