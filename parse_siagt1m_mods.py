"""Parse siAGT-1m modification positions from Molecular Therapy (2025) PDF Table 1."""
import re

def parse_positions(mixed_seq):
    seq = re.sub(r'(?i)(dT\s*dT|dT)\s*$', '', mixed_seq.strip()).strip()
    results = []
    i = 0
    pos = 0
    while i < len(seq):
        ch = seq[i]
        # 2'-Fluoro: Xf
        if (ch.upper() in 'ACGU') and (i + 1 < len(seq)) and seq[i+1] == 'f':
            pos += 1
            results.append({'pos': pos, 'base': ch.upper(), 'mod': "2F"})
            i += 2
            continue
        # 2'-OMe: lowercase
        if ch in 'acgu':
            pos += 1
            results.append({'pos': pos, 'base': ch.upper(), 'mod': "2OMe"})
            i += 1
            continue
        # Unmodified RNA
        if ch.upper() in 'ACGUT':
            pos += 1
            results.append({'pos': pos, 'base': ch.upper(), 'mod': 'RNA'})
            i += 1
            continue
        i += 1
    return results, seq

# PDF-verified sequences (page 3, Molecular Therapy 2025 Table 1)
sense_seq = 'ccugGfcUfGfCfaggugaccgadTdT'
anti_seq  = 'uCfgguCfaccugcaGfcCfaggdTdT'

s_results, s_core = parse_positions(sense_seq)
a_results, a_core = parse_positions(anti_seq)

print('=' * 60)
print('siAGT-1m — SENSE (Passenger) Strand')
print(f'Core (no dTdT): {s_core}  [{len(s_results)} nt]')
print('=' * 60)
print(f"{'Pos':>4} | {'Base':>4} | Modification")
print('-' * 30)
for r in s_results:
    label = "2'-O-Methyl" if r['mod'] == '2OMe' else ("2'-Fluoro" if r['mod'] == '2F' else "Unmodified RNA")
    print(f"  {r['pos']:2d} |    {r['base']}  | {label}")

print()
print('=' * 60)
print('siAGT-1m — ANTISENSE (Guide) Strand')
print(f'Core (no dTdT): {a_core}  [{len(a_results)} nt]')
print('=' * 60)
print(f"{'Pos':>4} | {'Base':>4} | Modification")
print('-' * 30)
for r in a_results:
    label = "2'-O-Methyl" if r['mod'] == '2OMe' else ("2'-Fluoro" if r['mod'] == '2F' else "Unmodified RNA")
    print(f"  {r['pos']:2d} |    {r['base']}  | {label}")

# Pastable dict
s_ome = [r['pos'] for r in s_results if r['mod'] == '2OMe']
s_2f  = [r['pos'] for r in s_results if r['mod'] == '2F']
a_ome = [r['pos'] for r in a_results if r['mod'] == '2OMe']
a_2f  = [r['pos'] for r in a_results if r['mod'] == '2F']

print()
print('=' * 60)
print('PASTABLE PYTHON DICT — siAGT-1m')
print('=' * 60)
print(f"""
SIAGT_1M = {{
    "candidate_id":    "siAGT-1m",
    "target_gene":     "AGT",
    # 19 nt core sequences — dTdT 3' overhang excluded (structural, not a mod)
    "naked_sense":     "CCUGGCUGCAGGUGACCGA",
    "naked_antisense": "UCGGUCACCUGCAGCCAGG",
    "sense_mods": {{
        "2OMe_positions": {s_ome},   # 2'-O-Methyl positions (1-based)
        "2F_positions":   {s_2f},    # 2'-Fluoro positions (1-based)
    }},
    "antisense_mods": {{
        "2OMe_positions": {a_ome},   # 2'-O-Methyl positions (1-based)
        "2F_positions":   {a_2f},    # 2'-Fluoro positions (1-based)
    }},
}}
""")
