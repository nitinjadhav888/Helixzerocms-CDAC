import pandas as pd
import pathlib
import os

def extract_tables(html_path, output_prefix):
    print(f"Processing {html_path}...")
    try:
        # Read the raw markdown file which contains HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract tables using pandas
        tables = pd.read_html(html_content)
        print(f"Found {len(tables)} tables.")
        
        # Save each table to a CSV
        for i, df in enumerate(tables):
            output_file = f"D:/Helixx/smepred/data/Patents/extracted/{output_prefix}_table_{i+1}.csv"
            # Basic cleanup: drop empty rows/columns
            df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
            
            # Save to CSV
            df.to_csv(output_file, index=False)
            
            # Print a quick preview of the columns if the table has data
            if not df.empty and len(df.columns) > 1:
                print(f"Table {i+1} saved: {df.shape} - Columns: {list(df.columns)[:5]}")
                
    except Exception as e:
        print(f"Error processing {html_path}: {e}")

# Paths to the fetched HTML content
alnylam_path = r"C:\Users\Nilesh\.gemini\antigravity\brain\7b12a96a-9f07-4ad4-ba09-1fa4b24c314c\.system_generated\steps\2322\content.md"
dicerna_path = r"C:\Users\Nilesh\.gemini\antigravity\brain\7b12a96a-9f07-4ad4-ba09-1fa4b24c314c\.system_generated\steps\2324\content.md"

extract_tables(alnylam_path, "Alnylam_US10240152")
print("-" * 40)
extract_tables(dicerna_path, "Dicerna_US11697812")
