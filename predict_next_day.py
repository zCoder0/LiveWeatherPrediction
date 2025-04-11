import sys
from src.exception.custom_exception import ProjectException
from src.components.data_integstion  import  DataIntegstion
from src.components.preprocessing import Preprocessing
from src.components.model import BuildModel

try:
    
    p = Preprocessing()
    df = p.featureEngineering()
    
    features = ['Temperature (C)','Humidity','Wind (kph)','Pressure (mb)','Month','Hour','Feels_Muggy']
    df_features = p.select_features(df,features)
    
    scaled_features , min_max_scale = p.scalling_feature(df_features)
    X,y = p.split_X_y(scaled_features)
    
    model = BuildModel(X,y ,input_shape=(X.shape[1] ,X.shape[2]))
    test_df = model.test_data(df)
    morning,afternoon,evening,night = model.split_test_data(test_df)
    day ={
    'Morning':model.predict_next_day(morning,name="Morning",min_max_scale= min_max_scale,features=features),
    'AfterNoon':model.predict_next_day(afternoon,name="AfterNoon",min_max_scale= min_max_scale,features=features),
    'Evening':model.predict_next_day(evening,name="Evening",min_max_scale= min_max_scale,features=features),
    "night":model.predict_next_day(night,name="night",min_max_scale= min_max_scale,features=features)
    }
    print(day)
    
except Exception as e:
    print("An error occurred: " + str(e))
    ProjectException(e,sys)