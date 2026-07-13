"""Gera JSON dos dados para a apresentação HTML"""
import pandas as pd, json
PASTA = "dados_limpos"
result = {}

for base in ['materno','fetal','infantil']:
    df = pd.read_csv(f'{PASTA}/{base}_limpo.csv', sep=';', encoding='utf-8-sig', low_memory=False)

    # Bairro residência
    bairros = {}
    for b, q in df['BAIRES'].value_counts().items():
        bairros[b] = int(q)

    # Local ocorrência
    locais = {}
    for l, q in df['LOCAL DE OCORRENCIA'].value_counts().items():
        locais[l] = int(q)

    # Sexo
    sexo = {}
    for s, q in df['SEXO'].value_counts().items():
        label = {'M':'Masculino','F':'Feminino'}.get(s, s)
        sexo[label] = int(q)

    # Idade mãe
    idades = pd.to_numeric(df['IDADEMAE'], errors='coerce').dropna()
    idade_info = {}
    if len(idades) > 0:
        idade_info = {"media": round(idades.mean(),1), "min": int(idades.min()), "max": int(idades.max()),
                       "faixas": {}}
        faixas = [("Adolescente <20", idades<20), ("Adulto 20-34", (idades>=20)&(idades<35)), ("35+", idades>=35)]
        for nome, mask in faixas:
            idade_info["faixas"][nome] = int(mask.sum())

    # Unidade referência
    ref_col = None
    for c in ['UNIDADE REFERENCIA','UNIDADE DE REFERENCIA']:
        if c in df.columns:
            ref_col = c; break
    refs = {}
    if ref_col:
        vals = df[ref_col].dropna()
        vals = vals[vals != 'Não informado']
        for v, q in vals.value_counts().items():
            refs[v] = int(q)

    # CID
    cid_col = None
    for c in ['CAUSABAS','CB PÓS INVEST','CB- PÓS INVESTIGAÇÃO']:
        if c in df.columns:
            cid_col = c; break
    cids = {}
    if cid_col:
        vals = df[cid_col].dropna()
        vals = vals[vals != 'Não informado']
        for v, q in vals.value_counts().items():
            cids[str(v)] = int(q)

    # Peso
    peso_info = {}
    pesos = pd.to_numeric(df['PESO'], errors='coerce').dropna()
    pesos = pesos[pesos > 0]
    if len(pesos) > 0:
        peso_info = {"media": round(pesos.mean(),0), "min": int(pesos.min()), "max": int(pesos.max())}

    result[base] = {
        "total": len(df),
        "bairros": bairros,
        "locais": locais,
        "sexo": sexo,
        "idade": idade_info,
        "refs": refs,
        "cids": cids,
        "peso": peso_info
    }

with open("dados_slide.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("OK - dados_slide.json criado")
print(json.dumps(result, ensure_ascii=False, indent=2))
