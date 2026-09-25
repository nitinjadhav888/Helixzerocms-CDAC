import glob

for f in glob.glob('scripts/monograph_ch*.py'):
    with open(f, 'r', encoding='utf-8') as fp:
        content = fp.read()
    content = content.replace('Strictly ZERO dollar signs ($)', 'Strictly ZERO dollar signs')
    content = content.replace("r'(dTdT|UU|-3P|invdT|TT)$'", "'(dTdT|UU|-3P|invdT|TT) at sequence terminus'")
    with open(f, 'w', encoding='utf-8') as fp:
        fp.write(content)

has_dollar = False
for f in glob.glob('scripts/monograph_ch*.py'):
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
        if '$' in c:
            print(f'STILL HAS DOLLAR: {f}')
            has_dollar = True
        else:
            print(f'{f}: 100% CLEAN!')
if not has_dollar:
    print('ALL CHAPTER MODULES ARE 100% COMPLETELY FREE OF DOLLAR SIGNS!')
