"""
This script will sort the fractures based on their fracture type
and save the sorted data in a new directory.
"""
import ast
import os
import pandas as pd  # Import pandas for data manipulation


INPUT_CSV = "./data/split_data/split_manifest.csv"
OUTPUT_DIR = "sorted_fractures"  # Directory to save the sorted data


def convert_to_int(class_id_value):
    """Convert a value to an integer, handling exceptions."""
    if pd.isna(class_id_value):  # Check if the value is NaN
        return []

    if isinstance(class_id_value, list):  # If the value is already a list, return it as is
        return class_id_value  # Return the list as is if it's already a list

    try:  # Try to parse the value as a list using ast.literal_eval
        parsed = ast.literal_eval(class_id_value)

        # If the parsed value is a list, convert each element to an integer and return the list
        if isinstance(parsed, list):
            return [int(x) for x in parsed]

        return [int(parsed)]
    # Try to convert the value directly to an integer if it's not a list
    # Handles if a value can't be parsed as a list or converted to an integer
    except (ValueError, SyntaxError, TypeError):
        return []


def main():

    # Load CSV
    df = pd.read_csv(INPUT_CSV)
    
    # make sure the file loads correctly and values look like ints
    print(df.columns.tolist())
    print(df.head())

    # make new ouput directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Parse class_id column into list of ints
    df['converted_class_ids'] = df['class_ids'].apply(convert_to_int)

    # Find all unique int class ids
    unique_ids = sorted({
        class_id
        for row_ids in df['converted_class_ids']
        for class_id in row_ids
    })

    print(f"Found class ids: {unique_ids}")

    # Saves a csv per class id
    for class_id in unique_ids:  # Iterate over each unique class id
        # Filters the dataframe to include only rows where the
        # 'converted_class_ids' column contains the current class_id
        class_id_df = df[df['converted_class_ids'].apply(
            lambda ids: class_id in ids)].copy()

        output_path = os.path.join(OUTPUT_DIR, f"class_{class_id}.csv")  # Create the output file path for the current class_id
        class_id_df.to_csv(output_path, index=False)  # Save the filtered dataframe to a new CSV file named after the class_id
        print(f"Saved {len(class_id_df)} rows to {output_path}")

    print("\nSorting complete.")


if __name__ == "__main__":
    main()
