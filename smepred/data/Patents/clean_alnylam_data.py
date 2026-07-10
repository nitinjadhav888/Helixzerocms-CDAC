import pandas as pd
import numpy as np

def clean_alnylam_data():
    print("Loading extracted tables...")
    # Load sequence table (Table 47)
    seq_df = pd.read_csv(r'D:\Helixx\smepred\data\Patents\extracted\Alnylam_US10240152_table_47.csv')
    
    # Load knockdown table (Table 46)
    kd_df = pd.read_csv(r'D:\Helixx\smepred\data\Patents\extracted\Alnylam_US10240152_table_46.csv')
    
    # --- Clean Knockdown Data ---
    # The duplex ID is in column '0', IC50 (qPCR) is in column '1', IC50 (bDNA) is in column '2'
    # Drop rows where Duplex # is NaN or just header text
    kd_clean = kd_df.copy()
    kd_clean.columns = ['Duplex_ID', 'IC50_qPCR_nM', 'IC50_bDNA_nM', 'IFNa_TNFa', 'Mutations', 'Cross_Species']
    
    # Forward fill Duplex_ID because the table spans multiple rows per duplex due to wrapped text
    kd_clean['Duplex_ID'] = kd_clean['Duplex_ID'].replace({'Duplex #': np.nan})
    kd_clean['Duplex_ID'] = kd_clean['Duplex_ID'].ffill()
    
    # Filter to rows that actually contain IC50 numeric values
    kd_clean = kd_clean.dropna(subset=['IC50_qPCR_nM'])
    kd_clean = kd_clean[pd.to_numeric(kd_clean['IC50_qPCR_nM'], errors='coerce').notnull()]
    
    # Keep only the relevant columns and drop duplicates
    kd_clean = kd_clean[['Duplex_ID', 'IC50_qPCR_nM']].drop_duplicates()
    
    # --- Clean Sequence Data ---
    seq_clean = seq_df.copy()
    seq_clean.columns = ['Duplex_ID', 'Strand', 'Oligo_ID', 'Position', 'Sequence', 'SEQ_ID']
    seq_clean['Duplex_ID'] = seq_clean['Duplex_ID'].replace({'Duplex\u2003#': np.nan})
    seq_clean['Duplex_ID'] = seq_clean['Duplex_ID'].ffill()
    seq_clean = seq_clean.dropna(subset=['Sequence'])
    seq_clean = seq_clean[seq_clean['Sequence'] != 'Sequence\u20035\u2032 to\u20033\u2032']
    
    # Pivot so Sense and Antisense are in the same row
    seq_pivot = seq_clean.pivot(index='Duplex_ID', columns='Strand', values='Sequence').reset_index()
    if 's' in seq_pivot.columns and 'as' in seq_pivot.columns:
        seq_pivot = seq_pivot.rename(columns={'s': 'Sense_Sequence', 'as': 'Antisense_Sequence'})
    
    # --- Merge Data ---
    merged = pd.merge(seq_pivot, kd_clean, on='Duplex_ID', how='inner')
    
    print(f"Successfully merged {len(merged)} patented duplexes with IC50 knockdown data!")
    print(merged.head())
    
    # Save the final validation set
    output_path = r'D:\Helixx\smepred\data\Patents\Alnylam_TTR_Validation_Set.csv'
    merged.to_csv(output_path, index=False)
    print(f"Saved clean validation set to: {output_path}")

if __name__ == "__main__":
    clean_alnylam_data()
