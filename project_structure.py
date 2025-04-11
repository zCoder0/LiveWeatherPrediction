import os 
from pathlib import Path 

dir='src'
file_path=[
    f"{dir}\__init__.py",
    f"{dir}\components\__init__.py",
    f"{dir}\components\data_integstion.py",
    f"{dir}\components\preprocessing.py",
    
    f"{dir}\data_set\__init__.py",
    f"{dir}\trained_model\__init__.py",
    
    f"{dir}\exception\__init__.py",
    f"{dir}\exception\custom_exception.py",
    
    f"{dir}\logs\__init__.py",
    f"{dir}\logs\log_config.py",
]

for path in file_path:
    filepath = Path(path)
    
    folder ,file = os.path.split(path)
    if folder != "":
        os.makedirs(folder,exist_ok=True)
        
    if (not os.path.exists(filepath)):
        with open(filepath, 'w') as f:
            pass