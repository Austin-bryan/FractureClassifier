import pandas as pd
import os
import shutil
import random

BASE_DIR = r'C:\git_repos\FractureClassifier-jbcopy' # <---- CHANGE FOR YOUR MACHINE

# CONFIGURATION
CSV_PATH   = os.path.join(BASE_DIR, 'data', 'dataset.csv')
SRC_IMAGES = os.path.join(BASE_DIR, 'data', 'images')
SRC_LABELS = os.path.join(BASE_DIR, 'data', 'labels')
DST_BASE   = os.path.join(BASE_DIR, 'data', 'split_data')

#C:\Users\nbeli\FracDetectYolo\
#    ├── GRAZPEDWRI-DX
#    │      └──dataset.csv
#    ├── source\
#    │     ├── images\   
#    │     └── labels\  
#    └── GRAZPEDWRI-DX_7class_DataSplit\
#          └── data\     

TRAIN_SIZE    = 2000
VALID_SIZE    = int(TRAIN_SIZE * (20/70))
TEST_SIZE     = int(TRAIN_SIZE * (10/70))
NO_FRAC_RATIO = 0.20
RANDOM_SEED   = 42

# Top 7 AO codes → class IDs
TOP7 = {
    '23r-M/3.1': 0,
    '23r-M/2.1': 1,
    '23u-E/7':   2,
    '23u-M/2.1': 3,
    '23-M/3.1':  4,
    '23-M/2.1':  5,
    '23r-E/2.1': 6,
}

# Post-inference grouping
INFERENCE_GROUPS = {
    'FRM': [0, 1, 4, 5],
    'FUE': [2],
    'FUM': [3],
    'FRE': [6],
}

ORIG_FRACTURE_ID = 3

# Load and filter
print("Loading CSV...")
df = pd.read_csv(CSV_PATH)
df = df[df['diagnosis_uncertain'] != 1.0]
df = df[df['metal'] != 1.0]

def get_class_ids(ao_val):
    if pd.isna(ao_val):
        return []
    codes = [c.strip() for c in str(ao_val).split(';')]
    return [TOP7[c] for c in codes if c in TOP7]

# Group 1 — visible fractures matching top 7
df_fracture = df[
    (df['fracture_visible'] == 1.0) &
    (df['ao_classification'].apply(lambda x: len(get_class_ids(x)) > 0))
].copy()

# Group 2 — confirmed no fracture
df_no_fracture = df[df['ao_classification'].isna()].copy()

print(f"Group 1 (fracture):    {len(df_fracture)} images ({df_fracture['patient_id'].nunique()} patients)")
print(f"Group 2 (no fracture): {len(df_no_fracture)} images ({df_no_fracture['patient_id'].nunique()} patients)")

# Verify source folders exist
print("\nChecking source folders...")
print(f"Images folder exists: {os.path.exists(SRC_IMAGES)}")
print(f"Labels folder exists: {os.path.exists(SRC_LABELS)}")

# Check if images are directly in folder or in subfolders
img_files = os.listdir(SRC_IMAGES) if os.path.exists(SRC_IMAGES) else []
print(f"Items in images folder: {len(img_files)}")
if img_files:
    print(f"First 3 items: {img_files[:3]}")
    # Check if they're subfolders or direct files
    first_item = os.path.join(SRC_IMAGES, img_files[0])
    print(f"First item is folder: {os.path.isdir(first_item)}")

lbl_files = os.listdir(SRC_LABELS) if os.path.exists(SRC_LABELS) else []
print(f"Items in labels folder: {len(lbl_files)}")
if lbl_files:
    print(f"First 3 items: {lbl_files[:3]}")
    first_item = os.path.join(SRC_LABELS, lbl_files[0])
    print(f"First item is folder: {os.path.isdir(first_item)}")

# Patient level split
random.seed(RANDOM_SEED)

def split_patients(df_group):
    patients = df_group['patient_id'].unique().tolist()
    random.shuffle(patients)
    n = len(patients)
    return (
        set(patients[:int(n * 0.70)]),
        set(patients[int(n * 0.70):int(n * 0.90)]),
        set(patients[int(n * 0.90):])
    )

frac_train_p,   frac_valid_p,   frac_test_p   = split_patients(df_fracture)
nofrac_train_p, nofrac_valid_p, nofrac_test_p = split_patients(df_no_fracture)

def get_images(df_group, patient_set):
    imgs = df_group[df_group['patient_id'].isin(patient_set)]['filestem'].tolist()
    random.shuffle(imgs)
    return imgs

frac_train   = get_images(df_fracture,    frac_train_p)
frac_valid   = get_images(df_fracture,    frac_valid_p)
frac_test    = get_images(df_fracture,    frac_test_p)
nofrac_train = get_images(df_no_fracture, nofrac_train_p)
nofrac_valid = get_images(df_no_fracture, nofrac_valid_p)
nofrac_test  = get_images(df_no_fracture, nofrac_test_p)

nofrac_train_n = int(TRAIN_SIZE * NO_FRAC_RATIO)
nofrac_valid_n = int(VALID_SIZE * NO_FRAC_RATIO)
nofrac_test_n  = int(TEST_SIZE  * NO_FRAC_RATIO)
frac_train_n   = TRAIN_SIZE - nofrac_train_n
frac_valid_n   = VALID_SIZE - nofrac_valid_n
frac_test_n    = TEST_SIZE  - nofrac_test_n

splits = {
    'train': frac_train[:frac_train_n]   + nofrac_train[:nofrac_train_n],
    'valid': frac_valid[:frac_valid_n]   + nofrac_valid[:nofrac_valid_n],
    'test':  frac_test[:frac_test_n]     + nofrac_test[:nofrac_test_n],
}

fracture_filestems = set(df_fracture['filestem'].tolist())
ao_lookup = dict(zip(df['filestem'], df['ao_classification']))

print(f"\nSplit sizes:")
for split, files in splits.items():
    frac_n   = sum(1 for f in files if f in fracture_filestems)
    nofrac_n = len(files) - frac_n
    print(f"  {split}: {len(files)} total ({frac_n} fracture + {nofrac_n} no-fracture)")

# Remap labels

def find_image(filestem):
    """Find image in source folder — handles both flat and subfolder structure"""
    # Try direct in folder first
    direct = os.path.join(SRC_IMAGES, f"{filestem}.png")
    if os.path.exists(direct):
        return direct
    # Try subfolders
    for sub in ['train', 'valid', 'test']:
        path = os.path.join(SRC_IMAGES, sub, f"{filestem}.png")
        if os.path.exists(path):
            return path
    return None

def find_label(filestem):
    """Find label in source folder — handles both flat and subfolder structure"""
    direct = os.path.join(SRC_LABELS, f"{filestem}.txt")
    if os.path.exists(direct):
        return direct
    for sub in ['train', 'valid', 'test']:
        path = os.path.join(SRC_LABELS, sub, f"{filestem}.txt")
        if os.path.exists(path):
            return path
    return None

def remap_label(src_path, dst_path, filestem):
    is_fracture = filestem in fracture_filestems
    class_ids = get_class_ids(ao_lookup.get(filestem, None))

    if not is_fracture or not class_ids:
        open(dst_path, 'w').close()
        return

    if src_path is None or not os.path.exists(src_path):
        open(dst_path, 'w').close()
        return

    with open(src_path, 'r') as f:
        lines = f.readlines()

    fracture_boxes = [
        line.strip().split()[1:]
        for line in lines
        if len(line.strip().split()) == 5
        and int(line.strip().split()[0]) == ORIG_FRACTURE_ID
    ]

    if not fracture_boxes:
        open(dst_path, 'w').close()
        return

    new_lines = []
    for i, cls_id in enumerate(class_ids):
        box = fracture_boxes[i] if i < len(fracture_boxes) else fracture_boxes[-1]
        new_lines.append(f"{cls_id} {box[0]} {box[1]} {box[2]} {box[3]}\n")

    with open(dst_path, 'w') as f:
        f.writelines(new_lines)

# Copy files

def copy_split(filestems, split_name):
    img_dst = os.path.join(DST_BASE, 'images', split_name)
    lbl_dst = os.path.join(DST_BASE, 'labels', split_name)
    os.makedirs(img_dst, exist_ok=True)
    os.makedirs(lbl_dst, exist_ok=True)

    copied = 0
    missing = 0

    for filestem in filestems:
        img_src = find_image(filestem)
        lbl_src = find_label(filestem)
        img_dst_file = os.path.join(img_dst, f"{filestem}.png")
        lbl_dst_file = os.path.join(lbl_dst, f"{filestem}.txt")

        if img_src:
            shutil.copy2(img_src, img_dst_file)
            remap_label(lbl_src, lbl_dst_file, filestem)
            copied += 1
        else:
            missing += 1

        if copied % 200 == 0 and copied > 0:
            print(f"    → {copied}/{len(filestems)} copied...")

    print(f"    ✓ {copied} copied, {missing} missing")

print("\nCopying files...")
for split_name, filestems in splits.items():
    print(f"\n  {split_name}:")
    copy_split(filestems, split_name)


# Verify
print("\nVerifying label distribution...")
from collections import Counter

CLASS_NAMES = {
    0: '23r-M/3.1 (FRM)',
    1: '23r-M/2.1 (FRM)',
    2: '23u-E/7   (FUE)',
    3: '23u-M/2.1 (FUM)',
    4: '23-M/3.1  (FRM)',
    5: '23-M/2.1  (FRM)',
    6: '23r-E/2.1 (FRE)',
}

for split_name in ['train', 'valid', 'test']:
    lbl_dir = os.path.join(DST_BASE, 'labels', split_name)
    class_counter = Counter()
    empty = 0
    for fname in os.listdir(lbl_dir):
        fpath = os.path.join(lbl_dir, fname)
        with open(fpath, 'r') as f:
            lines = f.readlines()
        if not lines:
            empty += 1
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 5:
                class_counter[int(parts[0])] += 1
    total = sum(class_counter.values())
    print(f"\n  {split_name}:")
    for cls_id, cls_name in CLASS_NAMES.items():
        n = class_counter.get(cls_id, 0)
        pct = n/total*100 if total > 0 else 0
        print(f"    Class {cls_id} {cls_name}: {n} boxes ({pct:.1f}%)")
    print(f"    Empty (no fracture): {empty} images")

# Save manifest for tracking and inference grouping
rows = []
for split_name, filestems in splits.items():
    for f in filestems:
        is_frac = f in fracture_filestems
        class_ids = get_class_ids(ao_lookup.get(f, None))
        rows.append({
            'filestem':          f,
            'split':             split_name,
            'group':             'fracture' if is_frac else 'no_fracture',
            'ao_classification': ao_lookup.get(f, None),
            'class_ids':         str(class_ids)
        })

manifest = pd.DataFrame(rows)
manifest.to_csv(os.path.join(DST_BASE, 'split_manifest.csv'), index=False)

print("\nInference group mapping:")
for group, ids in INFERENCE_GROUPS.items():
    codes = [k for k,v in TOP7.items() if v in ids]
    print(f"  {group}: classes {ids} → {codes}")

print("\nAll done!")
