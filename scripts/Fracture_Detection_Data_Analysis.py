import numpy as np
import pandas as pd

# 1 Fracture
frac1_train_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name="1_Fracture_Train")
frac1_test_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name="1_Fracture_Test")
frac1_val_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name="1_Fracture_Validation")

# 2 Fractures
frac2_train_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name="2_Fractures_Train")
frac2_test_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name="2_Fractures_Test")
frac2_val_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name="2_Fractures_Validation")

# 3 Fractures
frac3_train_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name="3_Fractures_Train")
frac3_test_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name="3_Fractures_Test")
frac3_val_df = pd.read_excel("WristFractureData_datasets.xlsx", sheet_name="3_Fractures_Validation")

# Function to analyze a dataframe
def analyze_split(df, split_name):
    print(f"\n{'='*50}")
    print(f"{split_name} Analysis")
    print(f"{'='*50}")
    
    # Total samples
    print(f"Total samples: {len(df)}")
    
    # Count identified vs non-identified (empty AO classification)
    identified = df['ao_classification'].notna().sum()
    non_identified = df['ao_classification'].isna().sum()
    
    print(f"\nIdentified fractures: {identified} ({identified/len(df)*100:.1f}%)")
    print(f"Non-identified: {non_identified} ({non_identified/len(df)*100:.1f}%)")
    
    # Count each AO classification type
    print(f"\nAO Classification breakdown:")
    ao_counts = df['ao_classification'].value_counts(dropna=False)
    print(ao_counts)
    
    return {
        'total': len(df),
        'identified': identified,
        'non_identified': non_identified,
        'ao_counts': ao_counts
    }

# ===== 1 FRACTURE ANALYSIS =====
print("\n" + "="*50)
print("1 FRACTURE DATASET")
print("="*50)

frac1_train_stats = analyze_split(frac1_train_df, "1 FRACTURE - TRAIN")
frac1_val_stats = analyze_split(frac1_val_df, "1 FRACTURE - VALIDATION")
frac1_test_stats = analyze_split(frac1_test_df, "1 FRACTURE - TEST")

# Summary comparison
print(f"\n{'='*50}")
print("SUMMARY COMPARISON FOR 1 FRACTURE")
print(f"{'='*50}")
total_1 = frac1_train_stats['total'] + frac1_val_stats['total'] + frac1_test_stats['total']
print(f"Train:      {frac1_train_stats['total']} samples ({frac1_train_stats['total']/total_1*100:.1f}%)")
print(f"Validation: {frac1_val_stats['total']} samples ({frac1_val_stats['total']/total_1*100:.1f}%)")
print(f"Test:       {frac1_test_stats['total']} samples ({frac1_test_stats['total']/total_1*100:.1f}%)")

# ===== 2 FRACTURES ANALYSIS =====
print("\n" + "="*50)
print("2 FRACTURES DATASET")
print("="*50)

frac2_train_stats = analyze_split(frac2_train_df, "2 FRACTURES - TRAIN")
frac2_val_stats = analyze_split(frac2_val_df, "2 FRACTURES - VALIDATION")
frac2_test_stats = analyze_split(frac2_test_df, "2 FRACTURES - TEST")

# Summary comparison
print(f"\n{'='*50}")
print("SUMMARY COMPARISON FOR 2 FRACTURES")
print(f"{'='*50}")
total_2 = frac2_train_stats['total'] + frac2_val_stats['total'] + frac2_test_stats['total']
print(f"Train:      {frac2_train_stats['total']} samples ({frac2_train_stats['total']/total_2*100:.1f}%)")
print(f"Validation: {frac2_val_stats['total']} samples ({frac2_val_stats['total']/total_2*100:.1f}%)")
print(f"Test:       {frac2_test_stats['total']} samples ({frac2_test_stats['total']/total_2*100:.1f}%)")

# ===== 3 FRACTURES ANALYSIS =====
print("\n" + "="*50)
print("3 FRACTURES DATASET")
print("="*50)

frac3_train_stats = analyze_split(frac3_train_df, "3 FRACTURES - TRAIN")
frac3_val_stats = analyze_split(frac3_val_df, "3 FRACTURES - VALIDATION")
frac3_test_stats = analyze_split(frac3_test_df, "3 FRACTURES - TEST")

# Summary comparison
print(f"\n{'='*50}")
print("SUMMARY COMPARISON FOR 3 FRACTURES")
print(f"{'='*50}")
total_3 = frac3_train_stats['total'] + frac3_val_stats['total'] + frac3_test_stats['total']
print(f"Train:      {frac3_train_stats['total']} samples ({frac3_train_stats['total']/total_3*100:.1f}%)")
print(f"Validation: {frac3_val_stats['total']} samples ({frac3_val_stats['total']/total_3*100:.1f}%)")
print(f"Test:       {frac3_test_stats['total']} samples ({frac3_test_stats['total']/total_3*100:.1f}%)")

# ===== OVERALL SUMMARY =====
print(f"\n{'='*50}")
print("OVERALL SUMMARY ACROSS ALL DATASETS")
print(f"{'='*50}")
grand_total = total_1 + total_2 + total_3
print(f"1 Fracture total:  {total_1} samples ({total_1/grand_total*100:.1f}%)")
print(f"2 Fractures total: {total_2} samples ({total_2/grand_total*100:.1f}%)")
print(f"3 Fractures total: {total_3} samples ({total_3/grand_total*100:.1f}%)")
print(f"Grand total:       {grand_total} samples")

# ===== FRACTURE VS NON-FRACTURE BALANCE =====
print(f"\n{'='*50}")
print("FRACTURE VS NON-FRACTURE BALANCE")
print(f"{'='*50}")

print("\n1 FRACTURE DATASET:")
print(f"Train:      {frac1_train_stats['total']} ({frac1_train_stats['identified']} fractures + {frac1_train_stats['non_identified']} non-fractures) - {frac1_train_stats['non_identified']/frac1_train_stats['total']*100:.1f}% non-fractures")
print(f"Validation: {frac1_val_stats['total']} ({frac1_val_stats['identified']} fractures + {frac1_val_stats['non_identified']} non-fractures) - {frac1_val_stats['non_identified']/frac1_val_stats['total']*100:.1f}% non-fractures")
print(f"Test:       {frac1_test_stats['total']} ({frac1_test_stats['identified']} fractures + {frac1_test_stats['non_identified']} non-fractures) - {frac1_test_stats['non_identified']/frac1_test_stats['total']*100:.1f}% non-fractures")

print("\n2 FRACTURES DATASET:")
print(f"Train:      {frac2_train_stats['total']} ({frac2_train_stats['identified']} fractures + {frac2_train_stats['non_identified']} non-fractures) - {frac2_train_stats['non_identified']/frac2_train_stats['total']*100:.1f}% non-fractures")
print(f"Validation: {frac2_val_stats['total']} ({frac2_val_stats['identified']} fractures + {frac2_val_stats['non_identified']} non-fractures) - {frac2_val_stats['non_identified']/frac2_val_stats['total']*100:.1f}% non-fractures")
print(f"Test:       {frac2_test_stats['total']} ({frac2_test_stats['identified']} fractures + {frac2_test_stats['non_identified']} non-fractures) - {frac2_test_stats['non_identified']/frac2_test_stats['total']*100:.1f}% non-fractures")

print("\n3 FRACTURES DATASET:")
print(f"Train:      {frac3_train_stats['total']} ({frac3_train_stats['identified']} fractures + {frac3_train_stats['non_identified']} non-fractures) - {frac3_train_stats['non_identified']/frac3_train_stats['total']*100:.1f}% non-fractures")
print(f"Validation: {frac3_val_stats['total']} ({frac3_val_stats['identified']} fractures + {frac3_val_stats['non_identified']} non-fractures) - {frac3_val_stats['non_identified']/frac3_val_stats['total']*100:.1f}% non-fractures")
print(f"Test:       {frac3_test_stats['total']} ({frac3_test_stats['identified']} fractures + {frac3_test_stats['non_identified']} non-fractures) - {frac3_test_stats['non_identified']/frac3_test_stats['total']*100:.1f}% non-fractures")
