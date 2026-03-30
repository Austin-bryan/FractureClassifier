"""
This script will sort the fractures based on their classification codes 
and save the sorted data in a new directory.
"""
import os
import pandas as pd

def sort_fractures(csv_path, output_dir):
    """Sort fractures based on their classification codes 
    and save the sorted data in a new directory.
    Args:
        csv_path (str): Path to the CSV file containing fracture data.
        output_dir (str): Directory where the sorted data will be saved.
    Returns: None
    """

