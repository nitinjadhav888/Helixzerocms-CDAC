import pandas as pd
import re

def translate_alnylam_notation(seq_str):
    """
    Translates Alnylam patent notation (e.g. 'GGAuuucAuGuAAccAAGAdTdT', 'GsG')
    into HelixZero Base Sequence and Modification Pattern.
    """
    if pd.isna(seq_str):
        return "", ""
        
    seq_str = str(seq_str)
    
    # 1. Handle 'dT' which is 2 characters in Alnylam but represents 1 nucleotide (2'-Deoxy T)
    # We will temporarily replace 'dT' with 'd' to make it a single character mapping
    seq_str = seq_str.replace('dT', 'd')
    seq_str = seq_str.replace('dt', 'd')
    
    # 2. Handle Phosphorothioate 's' which is an inter-nucleotide linkage
    # For now, if we see 's', we'll mark the PRECEDING nucleotide as having a PS backbone
    # Example: Gs -> G with PS.
    # In HelixZero, PS is 'S'. Let's strip 's' for the base sequence, but note its presence.
    
    base_seq = []
    mod_pattern = []
    
    i = 0
    while i < len(seq_str):
        char = seq_str[i]
        
        # If the NEXT character is 's', it's a phosphorothioate linkage.
        # But for simplification in this basic translator, we will just treat 's' as a separate mod
        # or ignore it if we are only tracking sugar mods (M, F, D).
        if char == 's':
            i += 1
            continue
            
        if char == 'd':
            base_seq.append('T')
            mod_pattern.append('D') # 2'-Deoxy
        elif char.islower():
            # Lowercase in Alnylam usually means 2'-OMe
            base_seq.append(char.upper())
            mod_pattern.append('M') # 2'-OMe
        elif char.isupper():
            # Uppercase is canonical RNA
            base_seq.append(char.upper())
            mod_pattern.append('.') # Canonical
        else:
            base_seq.append(char.upper())
            mod_pattern.append('.')
            
        i += 1
        
    return "".join(base_seq), "".join(mod_pattern)

def standardize_dataset():
    df = pd.read_csv(r'D:\Helixx\smepred\data\Patents\Alnylam_TTR_Validation_Set.csv')
    
    # Apply translation
    df['Sense_Base'], df['Sense_Mods'] = zip(*df['Sense_Sequence'].apply(translate_alnylam_notation))
    df['Antisense_Base'], df['Antisense_Mods'] = zip(*df['Antisense_Sequence'].apply(translate_alnylam_notation))
    
    # Reorder columns
    cols = [
        'Duplex_ID', 
        'Sense_Sequence', 'Sense_Base', 'Sense_Mods',
        'Antisense_Sequence', 'Antisense_Base', 'Antisense_Mods',
        'IC50_qPCR_nM'
    ]
    df = df[cols]
    
    output_path = r'D:\Helixx\smepred\data\Patents\Alnylam_TTR_Validation_Standardized.csv'
    df.to_csv(output_path, index=False)
    
    print("--- Standardized Dataset Preview ---")
    print(df[['Duplex_ID', 'Sense_Mods', 'Antisense_Mods', 'IC50_qPCR_nM']].head())
    print(f"\nSaved standardized dataset to: {output_path}")

if __name__ == "__main__":
    standardize_dataset()
