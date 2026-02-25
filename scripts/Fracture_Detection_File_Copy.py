import numpy as np
import pandas as pd
import shutil
from pathlib import Path
import time

start_time = time.time()

Path("dataset/1_Fracture/train").mkdir(parents=True, exist_ok=True)
Path("dataset/1_Fracture/test").mkdir(parents=True, exist_ok=True)
Path("dataset/1_Fracture/validation").mkdir(parents=True, exist_ok=True)

Path("dataset/2_Fracture/train").mkdir(parents=True, exist_ok=True)
Path("dataset/2_Fracture/test").mkdir(parents=True, exist_ok=True)
Path("dataset/2_Fracture/validation").mkdir(parents=True, exist_ok=True)

Path("dataset/3_Fracture/train").mkdir(parents=True, exist_ok=True)
Path("dataset/3_Fracture/test").mkdir(parents=True, exist_ok=True)
Path("dataset/3_Fracture/validation").mkdir(parents=True, exist_ok=True)
#Path("dataset/validation").mkdir(parents=True, exist_ok=True)
#Path("dataset/test").mkdir(parents=True, exist_ok=True)

source_folder = r"C:\Users\nbeli\OneDrive\Desktop\FractureDetection\images"

#Data Frames
print('Loading Dataframes')

frac1_train_images_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name = "1_Fracture_Train")
frac2_train_images_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name = "2_Fractures_Train")
frac3_train_images_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name = "3_Fractures_Train")

frac1_test_images_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name = "1_Fracture_Test")
frac2_test_images_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name = "2_Fractures_Test")
frac3_test_images_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name = "3_Fractures_Test")

frac1_val_images_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name = "1_Fracture_Validation")
frac2_val_images_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name = "2_Fractures_Validation")
frac3_val_images_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name = "3_Fractures_Validation")
print('Data Frames Loaded!')


# Copy training images
print('==========================')
print('Loading 1 Fracture Images')
print('==========================')
for filename in frac1_train_images_df['filestem']:
    # Add the extension if it's not in your Excel file
    if not filename.endswith(('.jpg', '.png', '.dcm')):
        filename = filename + '.png' 
    
    source = Path(source_folder) / filename
    destination = Path("dataset/1_Fracture/train") / filename
    
    # Check if file exists before copying
    if source.exists():
        shutil.copy(source, destination)
        print(f"Copied {filename} to train")
    else:
        print(f"WARNING: {filename} not found at {source}")

for filename in frac1_test_images_df['filestem']:
    # Add the extension if it's not in your Excel file
    if not filename.endswith(('.jpg', '.png', '.dcm')):
        filename = filename + '.png' 
    
    source = Path(source_folder) / filename
    destination = Path("dataset/1_Fracture/test") / filename
    
    # Check if file exists before copying
    if source.exists():
        shutil.copy(source, destination)
        print(f"Copied {filename} to test")
    else:
        print(f"WARNING: {filename} not found at {source}")

for filename in frac1_val_images_df['filestem']:
    # Add the extension if it's not in your Excel file
    if not filename.endswith(('.jpg', '.png', '.dcm')):
        filename = filename + '.png' 
    
    source = Path(source_folder) / filename
    destination = Path("dataset/1_Fracture/validation") / filename
    
    # Check if file exists before copying
    if source.exists():
        shutil.copy(source, destination)
        print(f"Copied {filename} to validation")
    else:
        print(f"WARNING: {filename} not found at {source}")

print('==========================')
print('Loading 2 Fracture Images')
print('==========================')
for filename in frac2_train_images_df['filestem']:
    # Add the extension if it's not in your Excel file
    if not filename.endswith(('.jpg', '.png', '.dcm')):
        filename = filename + '.png'  # or whatever your extension is
    
    source = Path(source_folder) / filename
    destination = Path("dataset/2_Fracture/train") / filename
    
    # Check if file exists before copying
    if source.exists():
        shutil.copy(source, destination)
        print(f"Copied {filename} to train")
    else:
        print(f"WARNING: {filename} not found at {source}")

for filename in frac2_test_images_df['filestem']:
    # Add the extension if it's not in your Excel file
    if not filename.endswith(('.jpg', '.png', '.dcm')):
        filename = filename + '.png'  # or whatever your extension is
    
    source = Path(source_folder) / filename
    destination = Path("dataset/2_Fracture/test") / filename
    
    # Check if file exists before copying
    if source.exists():
        shutil.copy(source, destination)
        print(f"Copied {filename} to test")
    else:
        print(f"WARNING: {filename} not found at {source}")

for filename in frac2_val_images_df['filestem']:
    # Add the extension if it's not in your Excel file
    if not filename.endswith(('.jpg', '.png', '.dcm')):
        filename = filename + '.png'  # or whatever your extension is
    
    source = Path(source_folder) / filename
    destination = Path("dataset/2_Fracture/validation") / filename
    
    # Check if file exists before copying
    if source.exists():
        shutil.copy(source, destination)
        print(f"Copied {filename} to validation")
    else:
        print(f"WARNING: {filename} not found at {source}")
        
print('==========================')
print('Loading 3 Fracture Images')
print('==========================')
for filename in frac3_train_images_df['filestem']:
    # Add the extension if it's not in your Excel file
    if not filename.endswith(('.jpg', '.png', '.dcm')):
        filename = filename + '.png'  # or whatever your extension is
    
    source = Path(source_folder) / filename
    destination = Path("dataset/3_Fracture/train") / filename
    
    # Check if file exists before copying
    if source.exists():
        shutil.copy(source, destination)
        print(f"Copied {filename} to train")
    else:
        print(f"WARNING: {filename} not found at {source}")

for filename in frac3_test_images_df['filestem']:
    # Add the extension if it's not in your Excel file
    if not filename.endswith(('.jpg', '.png', '.dcm')):
        filename = filename + '.png'  # or whatever your extension is
    
    source = Path(source_folder) / filename
    destination = Path("dataset/3_Fracture/test") / filename
    
    # Check if file exists before copying
    if source.exists():
        shutil.copy(source, destination)
        print(f"Copied {filename} to test")
    else:
        print(f"WARNING: {filename} not found at {source}")

for filename in frac3_val_images_df['filestem']:
    # Add the extension if it's not in your Excel file
    if not filename.endswith(('.jpg', '.png', '.dcm')):
        filename = filename + '.png'  # or whatever your extension is
    
    source = Path(source_folder) / filename
    destination = Path("dataset/3_Fracture/validation") / filename
    
    # Check if file exists before copying
    if source.exists():
        shutil.copy(source, destination)
        print(f"Copied {filename} to validation")
    else:
        print(f"WARNING: {filename} not found at {source}")

print("Done! Files copied successfully.")
end_time = time.time()
elapsed_time = end_time - start_time

minutes = int((elapsed_time % 3600) // 60)
seconds = elapsed_time % 60

print(f"Total time: {minutes}m {seconds:.2f}s")
