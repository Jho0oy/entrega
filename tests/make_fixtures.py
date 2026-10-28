import json, os, sys
root = sys.argv[1]

def w(path, obj):
    p = os.path.join(root, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)

MUNS = [("07242", "IMPERATRIZ"), ("08850", "SÃO LUÍS"), ("09999", "AÇAILÂNDIA")]

def cand(n, nmu, vap, e="n"):
    return {"n": n, "nmu": nmu, "vap": str(vap), "e": e, "nm": nmu}

def carg(cd, nmn, cands, grouped=False):
    if grouped:
        agr = [{"par": [{"cand": cands}]}]
        return {"carg": [{"cd": cd, "nmn": nmn, "agr": agr}]}
    return {"carg": [{"cd": cd, "nmn": nmn, "cand": cands}]}

# configuração de municípios (EA12), 1º e 2º turno
for e in (6257, 6258):
    w(f"ele2026/{e}/config/mun-e{e:06d}-cm.json",
      {"abr": [{"cd": "MA", "mu": [{"cd": c, "nm": n} for c, n in MUNS]},
               {"cd": "PI", "mu": [{"cd": "00019", "nm": "TERESINA"}]}]})

# cargo -> (nome, candidatos por abrangência, eleição 1º turno, eleição 2º turno)
def pres(e, win):
    return [cand("13", "CANDIDATO A", 500, "s" if win == "13" else "n"),
            cand("22", "CANDIDATO B", 400, "s" if win == "22" else "n"),
            cand("0", "LEGENDA SEM NOME", 1)]  # nmu vazio é ignorado

# 1º turno
for scope, mult in [("br", 1000), ("ma", 100), *[(f"ma{c}", 1) for c, _ in MUNS]]:
    pass

def put(turno, election, cd, nmn, cargo_n, scope, cands, grouped=False):
    prefix = scope
    d = "br" if scope == "br" else "ma"
    w(f"ele2026/{election}/dados/{d}/{prefix}-c{cargo_n:04d}-e{election:06d}-u.json",
      carg(cd, nmn, cands, grouped))

# Presidente (1): 1º turno sem eleito, 2º turno eleito 13
put(1, 6257, "1", "Presidente", 1, "br", [cand("13","CANDIDATO A",500),cand("22","CANDIDATO B",400),cand("99","","1")])
put(2, 6258, "1", "Presidente", 1, "br", [cand("13","CANDIDATO A",5000,"s"),cand("22","CANDIDATO B",4000)])
for c, _ in MUNS:
    put(1, 6257, "1", "Presidente", 1, f"ma{c}", [cand("13","CANDIDATO A",50),cand("22","CANDIDATO B",70)])
    put(2, 6258, "1", "Presidente", 1, f"ma{c}", [cand("13","CANDIDATO A",60),cand("22","CANDIDATO B",75)])

# Governador (3): eleito já no 1º turno -> 2º turno inexistente no MA (404)
gov = lambda m, e: [cand("11","GOVERNADOR X",300*m,e),cand("12","GOVERNADOR Y",100*m)]
put(1, 6259, "3", "Governador", 3, "ma", gov(10, "s"))
for c, _ in MUNS:
    put(1, 6259, "3", "Governador", 3, f"ma{c}", gov(1, "n"))

# Senador (5): duas vagas
sen = lambda m, es: [cand("111","SENADOR UM",300*m,"s" if es else "n"),
                     cand("222","SENADORA DOIS",200*m,"s" if es else "n"),
                     cand("333","SENADOR TRES",100*m)]
put(1, 6259, "5", "Senador", 5, "ma", sen(10, True))
for c, _ in MUNS:
    put(1, 6259, "5", "Senador", 5, f"ma{c}", sen(1, False))

# Deputado federal (6), agrupado por partido; estrutura aninhada
dep = lambda m, es: [cand("1010","DEP FEDERAL ÁGATA",90*m,"s" if es else "n"),
                     cand("2020","DEP FEDERAL BIA",80*m),
                     cand("3030","DEP FEDERAL CÉSAR",70*m,"s" if es else "n")]
put(1, 6259, "6", "Deputado Federal", 6, "ma", dep(10, True), grouped=True)
for c, _ in MUNS:
    put(1, 6259, "6", "Deputado Federal", 6, f"ma{c}", dep(1, False), grouped=True)

# Deputado estadual (7): um município sem arquivo (404) para testar tolerância
dest = lambda m, es: [cand("10100","DEP ESTADUAL DIDI",50*m,"s" if es else "n"),
                      cand("20200","DEP ESTADUAL EVA",40*m)]
put(1, 6259, "7", "Deputado Estadual", 7, "ma", dest(10, True), grouped=True)
for c, _ in MUNS[:2]:  # 09999 ausente de propósito
    put(1, 6259, "7", "Deputado Estadual", 7, f"ma{c}", dest(1, False), grouped=True)
