import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

# Read the different fracture groups and non-fractures
frac_1_df = pd.read_excel("WristFractureData.xlsx", sheet_name='1_Fractures')
frac_2_df = pd.read_excel("WristFractureData.xlsx", sheet_name='2_Fractures')
frac_3_df = pd.read_excel("WristFractureData.xlsx", sheet_name='3_Fractures')
non_frac_df = pd.read_excel("WristFractureData.xlsx", sheet_name='NoFracture')

print(f"1 Fracture: {len(frac_1_df)} samples")
print(f"2 Fractures: {len(frac_2_df)} samples")
print(f"3 Fractures: {len(frac_3_df)} samples")
print(f"No Fractures: {len(non_frac_df)} samples")

# Calculate proportional distribution of non-fractures
total_fractures = len(frac_1_df) + len(frac_2_df) + len(frac_3_df)
frac_1_ratio = len(frac_1_df) / total_fractures
frac_2_ratio = len(frac_2_df) / total_fractures
frac_3_ratio = len(frac_3_df) / total_fractures

print(f"\nProportional distribution:")
print(f"1 Fracture gets: {frac_1_ratio*100:.1f}% of non-fractures")
print(f"2 Fractures get: {frac_2_ratio*100:.1f}% of non-fractures")
print(f"3 Fractures get: {frac_3_ratio*100:.1f}% of non-fractures")

# Function to split a dataframe
def split_dataframe(df, random_state=152):
    # First split: 75% train, 25% temp
    gss = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=random_state)
    train_idx, temp_idx = next(gss.split(df, groups=df['patient_id']))
    
    train = df.iloc[train_idx]
    temp = df.iloc[temp_idx]
    
    # Second split: split temp into validation and test
    gss2 = GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=random_state)
    val_idx, test_idx = next(gss2.split(temp, groups=temp['patient_id']))
    
    val = temp.iloc[val_idx]
    test = temp.iloc[test_idx]
    
    return train, val, test

# Split each fracture group
frac_1_train, frac_1_val, frac_1_test = split_dataframe(frac_1_df)
frac_2_train, frac_2_val, frac_2_test = split_dataframe(frac_2_df)
frac_3_train, frac_3_val, frac_3_test = split_dataframe(frac_3_df)

# Split non-fractures proportionally based on fracture counts
non_frac_shuffled = non_frac_df.sample(frac=1, random_state=152).reset_index(drop=True)

# Calculate how many non-fractures each group should get
non_frac_1_size = int(len(non_frac_shuffled) * frac_1_ratio)
non_frac_2_size = int(len(non_frac_shuffled) * frac_2_ratio)
# Remainder goes to group 3 to ensure we use all non-fractures

non_frac_for_1 = non_frac_shuffled.iloc[:non_frac_1_size]
non_frac_for_2 = non_frac_shuffled.iloc[non_frac_1_size:non_frac_1_size+non_frac_2_size]
non_frac_for_3 = non_frac_shuffled.iloc[non_frac_1_size+non_frac_2_size:]

print(f"\nNon-fracture distribution:")
print(f"1 Fracture: {len(non_frac_for_1)} non-fractures")
print(f"2 Fractures: {len(non_frac_for_2)} non-fractures")
print(f"3 Fractures: {len(non_frac_for_3)} non-fractures")

# Split each portion of non-fractures
non_frac_1_train, non_frac_1_val, non_frac_1_test = split_dataframe(non_frac_for_1)
non_frac_2_train, non_frac_2_val, non_frac_2_test = split_dataframe(non_frac_for_2)
non_frac_3_train, non_frac_3_val, non_frac_3_test = split_dataframe(non_frac_for_3)

# Combine fractures with their corresponding non-fractures
frac_1_train_final = pd.concat([frac_1_train, non_frac_1_train], ignore_index=True)
frac_1_val_final = pd.concat([frac_1_val, non_frac_1_val], ignore_index=True)
frac_1_test_final = pd.concat([frac_1_test, non_frac_1_test], ignore_index=True)

frac_2_train_final = pd.concat([frac_2_train, non_frac_2_train], ignore_index=True)
frac_2_val_final = pd.concat([frac_2_val, non_frac_2_val], ignore_index=True)
frac_2_test_final = pd.concat([frac_2_test, non_frac_2_test], ignore_index=True)

frac_3_train_final = pd.concat([frac_3_train, non_frac_3_train], ignore_index=True)
frac_3_val_final = pd.concat([frac_3_val, non_frac_3_val], ignore_index=True)
frac_3_test_final = pd.concat([frac_3_test, non_frac_3_test], ignore_index=True)

# Shuffle each final dataset
frac_1_train_final = frac_1_train_final.sample(frac=1, random_state=152).reset_index(drop=True)
frac_1_val_final = frac_1_val_final.sample(frac=1, random_state=152).reset_index(drop=True)
frac_1_test_final = frac_1_test_final.sample(frac=1, random_state=152).reset_index(drop=True)

frac_2_train_final = frac_2_train_final.sample(frac=1, random_state=152).reset_index(drop=True)
frac_2_val_final = frac_2_val_final.sample(frac=1, random_state=152).reset_index(drop=True)
frac_2_test_final = frac_2_test_final.sample(frac=1, random_state=152).reset_index(drop=True)

frac_3_train_final = frac_3_train_final.sample(frac=1, random_state=152).reset_index(drop=True)
frac_3_val_final = frac_3_val_final.sample(frac=1, random_state=152).reset_index(drop=True)
frac_3_test_final = frac_3_test_final.sample(frac=1, random_state=152).reset_index(drop=True)

# Print statistics
print(f"\n{'='*50}")
print("1 FRACTURE DATASET")
print(f"{'='*50}")
print(f"Train: {len(frac_1_train_final)} ({len(frac_1_train)} fractures + {len(non_frac_1_train)} non-fractures) - {len(non_frac_1_train)/len(frac_1_train_final)*100:.1f}% non-fractures")
print(f"Validation: {len(frac_1_val_final)} ({len(frac_1_val)} fractures + {len(non_frac_1_val)} non-fractures) - {len(non_frac_1_val)/len(frac_1_val_final)*100:.1f}% non-fractures")
print(f"Test: {len(frac_1_test_final)} ({len(frac_1_test)} fractures + {len(non_frac_1_test)} non-fractures) - {len(non_frac_1_test)/len(frac_1_test_final)*100:.1f}% non-fractures")

print(f"\n{'='*50}")
print("2 FRACTURES DATASET")
print(f"{'='*50}")
print(f"Train: {len(frac_2_train_final)} ({len(frac_2_train)} fractures + {len(non_frac_2_train)} non-fractures) - {len(non_frac_2_train)/len(frac_2_train_final)*100:.1f}% non-fractures")
print(f"Validation: {len(frac_2_val_final)} ({len(frac_2_val)} fractures + {len(non_frac_2_val)} non-fractures) - {len(non_frac_2_val)/len(frac_2_val_final)*100:.1f}% non-fractures")
print(f"Test: {len(frac_2_test_final)} ({len(frac_2_test)} fractures + {len(non_frac_2_test)} non-fractures) - {len(non_frac_2_test)/len(frac_2_test_final)*100:.1f}% non-fractures")

print(f"\n{'='*50}")
print("3 FRACTURES DATASET")
print(f"{'='*50}")
print(f"Train: {len(frac_3_train_final)} ({len(frac_3_train)} fractures + {len(non_frac_3_train)} non-fractures) - {len(non_frac_3_train)/len(frac_3_train_final)*100:.1f}% non-fractures")
print(f"Validation: {len(frac_3_val_final)} ({len(frac_3_val)} fractures + {len(non_frac_3_val)} non-fractures) - {len(non_frac_3_val)/len(frac_3_val_final)*100:.1f}% non-fractures")
print(f"Test: {len(frac_3_test_final)} ({len(frac_3_test)} fractures + {len(non_frac_3_test)} non-fractures) - {len(non_frac_3_test)/len(frac_3_test_final)*100:.1f}% non-fractures")

# Write to Excel
with pd.ExcelWriter("WristFractureData_datasets.xlsx", engine='openpyxl') as writer:
    frac_1_train_final.to_excel(writer, sheet_name='1_Fracture_Train', index=False)
    frac_1_val_final.to_excel(writer, sheet_name='1_Fracture_Validation', index=False)
    frac_1_test_final.to_excel(writer, sheet_name='1_Fracture_Test', index=False)
    
    frac_2_train_final.to_excel(writer, sheet_name='2_Fractures_Train', index=False)
    frac_2_val_final.to_excel(writer, sheet_name='2_Fractures_Validation', index=False)
    frac_2_test_final.to_excel(writer, sheet_name='2_Fractures_Test', index=False)
    
    frac_3_train_final.to_excel(writer, sheet_name='3_Fractures_Train', index=False)
    frac_3_val_final.to_excel(writer, sheet_name='3_Fractures_Validation', index=False)
    frac_3_test_final.to_excel(writer, sheet_name='3_Fractures_Test', index=False)

print("\nSplits saved to WristFractureData_datasets.xlsx")
