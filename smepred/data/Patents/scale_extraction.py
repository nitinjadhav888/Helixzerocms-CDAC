import pandas as pd
import numpy as np
import glob
import os
import re

def translate_alnylam_notation(seq_str):
    if pd.isna(seq_str) or not isinstance(seq_str, str):
        return "", ""
    seq_str = seq_str.replace('dT', 'd').replace('dt', 'd')
    base_seq, mod_pattern = [], []
    i = 0
    while i < len(seq_str):
        char = seq_str[i]
        if char == 's':
            i += 1
            continue
        if char == 'd':
            base_seq.append('T')
            mod_pattern.append('D')
        elif char.islower():
            base_seq.append(char.upper())
            mod_pattern.append('M')
        elif char.isupper():
            base_seq.append(char.upper())
            mod_pattern.append('.')
        else:
            base_seq.append(char.upper())
            mod_pattern.append('.')
        i += 1
    return "".join(base_seq), "".join(mod_pattern)

def process_alnylam_tables():
    files = glob.glob(r'D:\Helixx\smepred\data\Patents\extracted\Alnylam_US10240152_table_*.csv')
    
    seq_dfs = []
    kd_dfs = []
    
    for f in files:
        df = pd.read_csv(f)
        if df.empty:
            continue
            
        first_rows = df.head(5).to_string().lower()
        cols_lower = [str(c).lower() for c in df.columns]
        
        # Detect sequence tables
        if 'duplex' in first_rows and 'seq' in first_rows and ('strand' in first_rows or 'sequence' in first_rows):
            # Attempt to extract Duplex ID, Strand, and Sequence
            try:
                # Find columns roughly by index or keyword
                duplex_col = next((c for c in df.columns if 'duplex' in str(c).lower()), df.columns[0])
                seq_col = next((c for c in df.columns if 'sequence' in str(c).lower()), None)
                strand_col = next((c for c in df.columns if 'strand' in str(c).lower()), None)
                
                if seq_col and strand_col:
                    temp_df = df[[duplex_col, strand_col, seq_col]].copy()
                    temp_df.columns = ['Duplex_ID', 'Strand', 'Sequence']
                    seq_dfs.append(temp_df)
            except Exception as e:
                pass
                
        # Detect Knockdown tables
        if 'ic50' in first_rows or 'remaining' in first_rows:
            try:
                duplex_col = next((c for c in df.columns if 'duplex' in str(c).lower()), df.columns[0])
                # Find first column with numeric data that looks like IC50 or remaining %
                ic50_col = None
                for c in df.columns[1:]:
                    if pd.to_numeric(df[c], errors='coerce').notnull().sum() > 2:
                        ic50_col = c
                        break
                
                if ic50_col:
                    temp_df = df[[duplex_col, ic50_col]].copy()
                    temp_df.columns = ['Duplex_ID', 'Efficacy_Metric']
                    kd_dfs.append(temp_df)
            except Exception as e:
                pass

    print(f"Found {len(seq_dfs)} sequence tables and {len(kd_dfs)} knockdown tables.")
    
    if not seq_dfs or not kd_dfs:
        print("Not enough tables parsed to merge.")
        return
        
    all_seq = pd.concat(seq_dfs, ignore_index=True)
    all_kd = pd.concat(kd_dfs, ignore_index=True)
    
    # Clean up Duplex IDs
    all_seq['Duplex_ID'] = all_seq['Duplex_ID'].replace({'Duplex\u2003#': np.nan, 'Duplex #': np.nan})
    all_seq['Duplex_ID'] = all_seq['Duplex_ID'].ffill()
    all_seq = all_seq.dropna(subset=['Sequence'])
    all_seq = all_seq[~all_seq['Sequence'].str.contains('Sequence', na=False, case=False)]
    
    all_kd['Duplex_ID'] = all_kd['Duplex_ID'].replace({'Duplex\u2003#': np.nan, 'Duplex #': np.nan})
    all_kd['Duplex_ID'] = all_kd['Duplex_ID'].ffill()
    all_kd = all_kd.dropna(subset=['Efficacy_Metric'])
    all_kd = all_kd[pd.to_numeric(all_kd['Efficacy_Metric'], errors='coerce').notnull()]
    
    # Standardize Strand
    all_seq['Strand'] = all_seq['Strand'].str.strip().str.lower()
    sense_seqs = all_seq[all_seq['Strand'] == 's'].rename(columns={'Sequence': 'Sense_Sequence'})
    anti_seqs = all_seq[all_seq['Strand'] == 'as'].rename(columns={'Sequence': 'Antisense_Sequence'})
    
    seq_pivot = pd.merge(sense_seqs[['Duplex_ID', 'Sense_Sequence']], 
                         anti_seqs[['Duplex_ID', 'Antisense_Sequence']], 
                         on='Duplex_ID', how='inner').drop_duplicates('Duplex_ID')
                         
    all_kd = all_kd.drop_duplicates('Duplex_ID')
    
    final_merged = pd.merge(seq_pivot, all_kd, on='Duplex_ID', how='inner')
    
    # Translate notation
    final_merged['Sense_Base'], final_merged['Sense_Mods'] = zip(*final_merged['Sense_Sequence'].apply(translate_alnylam_notation))
    final_merged['Antisense_Base'], final_merged['Antisense_Mods'] = zip(*final_merged['Antisense_Sequence'].apply(translate_alnylam_notation))
    
    output_path = r'D:\Helixx\smepred\data\Patents\Alnylam_TTR_Full_Validation_Set.csv'
    final_merged.to_csv(output_path, index=False)
    print(f"Processed {len(final_merged)} total matched duplexes into {output_path}")

if __name__ == '__main__':
    process_alnylam_tables()
