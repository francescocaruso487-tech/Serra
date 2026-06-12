#!/usr/bin/env python3
"""
🧠 CERVELLO NOTTURNO v5 — Mini-Serra Living Soil
=================================================
Legge i PDF dal FILESYSTEM LOCALE (scripts/testi_cache/)
+ integra le guide web (guide_web_database.json)
+ genera connessioni cross-dominio da testo reale

Ciclo rotante: 10 PDF + 2 sezioni guide ogni 6 ore
"""

import json, os, re, random
from datetime import datetime
from pathlib import Path

BASE       = Path(__file__).parent.parent
DB_PATH    = BASE / "manuali" / "esperimenti_database.json"
LOG_PATH   = BASE / "scripts" / "cervello_log.json"
LETTI_PATH = BASE / "scripts" / "pdf_letture.json"
CACHE_DIR  = BASE / "scripts" / "testi_cache"
GUIDE_PATH = BASE / "manuali" / "guide_web_database.json"

# ── Carica tutti i file TXT dalla cache ──
def carica_cache_locale():
    pdf_list = []
    if not CACHE_DIR.exists():
        return pdf_list
    for f in sorted(CACHE_DIR.glob("*.txt")):
        nome = f.stem
        # Determina categoria dal nome file
        cat = "elettrocoltura"
        nome_lower = nome.lower()
        if any(k in nome_lower for k in ["magick","grimorio","kybalion","crowley","agrippa","salomone","hermeticum","pimandro","tavole","cabala","liber","registri","clavicola","esoterismo","aradia"]):
            cat = "magia"
        elif any(k in nome_lower for k in ["rol ","vangelo","joseph","book of wisdom","activating"]):
            cat = "spirituale"
        elif any(k in nome_lower for k in ["corano","upanishad","kojiki","buddhism","wicca","bahai","religioni","angeli"]):
            cat = "libri_sacri"
        elif any(k in nome_lower for k in ["soil biology","agricultural testament","agricultura","restrepo","quinto accordo","tresoldi"]):
            cat = "coltivazione"
        
        # Autore dal nome file
        autore = "N/D"
        autori_map = {
            "ingham": "Elaine Ingham", "howard": "Albert Howard",
            "tesla": "Nikola Tesla", "ighina": "Pier Luigi Ighina",
            "christofleau": "Justin Christofleau", "nollet": "Jean Nollet",
            "arce": "César Arce", "ramos": "Errol Ramos",
            "tompkins": "Tompkins & Bird", "church": "Dawson Church",
            "guerzoni": "Tiziano Guerzoni", "crowley": "Aleister Crowley",
            "restrepo": "Jairo Restrepo Rivera", "cathie": "Bruce Cathie",
            "ruhlmann": "Renaud Ruhlmann", "ouspensky": "P.D. Ouspensky",
            "pizzuti": "Marco Pizzuti", "tresoldi": "Roberto Tresoldi",
            "rol ": "Gustavo ROL", "allegri": "Renzo Allegri",
            "joseph": "Harry B. Joseph", "agrippa": "Cornelio Agrippa",
        }
        for k, v in autori_map.items():
            if k in nome_lower:
                autore = v; break
        
        pdf_list.append({"file": f, "nome": nome[:50], "cat": cat, "autore": autore})
    return pdf_list

def leggi_testo(path, max_chars=2000):
    try:
        testo = path.read_text(encoding='utf-8', errors='ignore')
        # Pulisce testo PDF grezzo
        testo = re.sub(r'\s+', ' ', testo)
        return testo[:max_chars].strip()
    except:
        return ""

# ── Concetti per generare connessioni ──
CONCETTI = {
    "vibrazione":    ["vibrat","frequenz","risonan","oscillaz","onda","vibration","frequency","harmonics"],
    "energia":       ["energy","energia","forza","force","prana","chi","orgone","electricity","electric"],
    "luce":          ["light","luce","luminoso","photon","fotone","illuminazione"],
    "acqua":         ["water","acqua","liquid","flow","flusso","vortex","vortice"],
    "terra":         ["earth","terra","soil","ground","terreno","suolo","humus","radici","root"],
    "luna":          ["moon","luna","lunar","ciclo","cycle","tide","biodinam"],
    "rame":          ["copper","rame","cuivre","antenna","conduttore"],
    "spirale":       ["spiral","helix","vortex","coil","rotazione","golden","fibonacci"],
    "intenzione":    ["intent","intenzione","will","volonta","mind","mente","thought"],
    "trasformazione":["transform","trasform","alchim","trasmut","change","mutazione"],
    "armonia":       ["harmon","armonia","equilibrio","balance","ordine","coherence"],
    "natura":        ["natura","nature","natural","pianta","plant","grow","crescit","vegetale"],
    "magnetismo":    ["magnet","polarit","campo","field","magnetico","polar","electro"],
    "coscienza":     ["conscious","coscienza","awareness","mindful","brain","cervello"],
    "crescita":      ["growth","crescita","sviluppo","develop","bloom","fioritura","yield"],
}

TEMPLATE = [
    "{A} e {B} convergono sulla {concetto}: la {A_dom} la misura con strumenti fisici, la {B_dom} la descrive con il linguaggio dell'esperienza.",
    "Dal testo di {A} emerge il tema della {concetto}. {B} porta la stessa energia nel dominio della {B_dom}.",
    "La {concetto} è il filo invisibile tra {A} ({A_dom}) e {B} ({B_dom}). La mini-serra è il laboratorio dove questo si manifesta.",
    "{B} ({B_dom}): la {concetto} come principio ordinatore. {A} la dimostra empiricamente nell'ambito della {A_dom}.",
    "Connessione reale da testo estratto: {A} e {B} parlano della stessa {concetto} con linguaggi diversi — scienza e tradizione convergono.",
]

def concetti_nel_testo(testo):
    trovati = {}
    t = testo.lower()
    for c, parole in CONCETTI.items():
        score = sum(t.count(p) for p in parole)
        if score >= 1: trovati[c] = score
    return set(sorted(trovati, key=trovati.get, reverse=True)[:8])

def genera_conn(pa, ta, pb, tb):
    ca = concetti_nel_testo(ta); cb = concetti_nel_testo(tb)
    comuni = ca & cb
    if not comuni: return None
    concetto = max(comuni, key=lambda c: sum((ta+tb).lower().count(p) for p in CONCETTI.get(c,[])))
    nota = random.choice(TEMPLATE).format(
        A=pa["autore"], B=pb["autore"],
        A_dom=pa["cat"], B_dom=pb["cat"], concetto=concetto
    )
    snippet = ta[:100].strip().replace('\n',' ')
    if len(snippet) > 30:
        nota += ' [Fonte: «' + snippet + '...»]'
    return {
        "a": pa["autore"] + " — " + pa["nome"][:40],
        "b": pb["autore"] + " — " + pb["nome"][:40],
        "nota": nota, "tags": list(comuni)[:5],
        "generata": datetime.now().strftime("%Y-%m-%d"),
        "tipo": "sinergia_cache_locale_v5",
        "fonte": "filesystem_cache"
    }

# ── Guide web → connessioni ──
def genera_conn_guide(guide_db, pdf):
    """Genera connessioni tra le guide web e i PDF."""
    conns = []
    fasi = guide_db.get("fasi", {})
    for fase_key, fase in fasi.items():
        # Confronta concetti della fase con il testo PDF
        testo_fase = " ".join(fase.get("consigli", []) + [fase.get("integrazione_livingsoil","")]).lower()
        testo_pdf = leggi_testo(pdf["file"])
        ca = concetti_nel_testo(testo_fase)
        cb = concetti_nel_testo(testo_pdf)
        comuni = ca & cb
        if comuni and pdf["cat"] in ("elettrocoltura", "coltivazione"):
            concetto = list(comuni)[0]
            conn = {
                "a": "Guide Web (Zamnesia+RQS) — " + fase.get("titolo",""),
                "b": pdf["autore"] + " — " + pdf["nome"][:40],
                "nota": f"Le guide professionali sulla {fase.get('titolo','')} e {pdf['autore']} convergono sul concetto di {concetto}. Applicazione pratica: {fase.get('integrazione_livingsoil','integra con il sistema Living Soil.')[:200]}",
                "tags": list(comuni)[:4],
                "generata": datetime.now().strftime("%Y-%m-%d"),
                "tipo": "guida_web_x_pdf",
                "fonte": "Zamnesia+RQS × " + pdf["cat"]
            }
            conns.append(conn)
            if len(conns) >= 3: break
    return conns

def carica_letture():
    if LETTI_PATH.exists():
        try: return json.loads(LETTI_PATH.read_text(encoding='utf-8'))
        except: pass
    return {"letti": [], "cicli": 0}

def salva_letture(d): LETTI_PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
def carica_db(): return json.loads(DB_PATH.read_text(encoding='utf-8'))
def salva_db(db):
    db['ultimo_aggiornamento'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    try: db['versione'] = str(round(float(db.get('versione','1.0'))+0.1,1))
    except: db['versione'] = '5.0'
    DB_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding='utf-8')

def main():
    print("="*60)
    print("🧠 CERVELLO NOTTURNO v5 — PDF locali + Guide Web")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Carica PDF dal filesystem locale
    tutti_pdf = carica_cache_locale()
    print(f"📚 PDF cache locale: {len(tutti_pdf)}")
    
    # Carica guide web
    guide_db = {}
    if GUIDE_PATH.exists():
        try: guide_db = json.loads(GUIDE_PATH.read_text(encoding='utf-8'))
        except: pass
    print(f"🌐 Guide web caricate: {'✅' if guide_db else '❌'}")
    
    db = carica_db()
    letture = carica_letture()
    
    # Connessioni esistenti
    esistenti = set()
    for c in db.get('connessioni',[]):
        a = c.get('a','')[:20].lower(); b = c.get('b','')[:20].lower()
        esistenti.add((a,b)); esistenti.add((b,a))
    print(f"📊 Connessioni esistenti: {len(db['connessioni'])}")
    
    # Seleziona batch rotante (10 PDF)
    letti = set(letture.get("letti",[]))
    non_letti = [p for p in tutti_pdf if p["nome"] not in letti]
    if not non_letti:
        print("🔄 Ciclo completo! Ricomincio")
        letture["letti"] = []
        letture["cicli"] = letture.get("cicli",0)+1
        non_letti = list(tutti_pdf)
    
    prio = [p for p in non_letti if p["cat"] in ("elettrocoltura","coltivazione")]
    altri = [p for p in non_letti if p["cat"] not in ("elettrocoltura","coltivazione")]
    random.shuffle(prio); random.shuffle(altri)
    batch = (prio + altri)[:10]
    
    print(f"\n📖 Lettura batch ({len(batch)} PDF dal filesystem):")
    testi = {}
    for pdf in batch:
        testo = leggi_testo(pdf["file"])
        testi[pdf["nome"]] = testo
        stato = f"✅ {len(testo)}c" if testo else "⚠️ vuoto"
        print(f"  📄 {pdf['nome'][:45]}... {stato}")
        if pdf["nome"] not in letture["letti"]:
            letture["letti"].append(pdf["nome"])
    
    pct = round(len(letture['letti'])/max(len(tutti_pdf),1)*100)
    print(f"\n📊 Letti: {len(letture['letti'])}/{len(tutti_pdf)} ({pct}%)")
    
    # Genera connessioni PDF × PDF
    nuove = []
    elec = [p for p in batch if p["cat"]=="elettrocoltura"]
    alt  = [p for p in batch if p["cat"]!="elettrocoltura"]
    
    for pe in elec:
        for pa in alt:
            if len(nuove)>=5: break
            ka=pe["autore"][:18].lower(); kb=pa["autore"][:18].lower()
            if (ka,kb) in esistenti or ka==kb: continue
            conn = genera_conn(pe, testi.get(pe["nome"],""), pa, testi.get(pa["nome"],""))
            if conn:
                nuove.append(conn); esistenti.add((ka,kb))
                print(f"  ✅ PDF×PDF: {pe['autore'][:20]} ↔ {pa['autore'][:20]}")
    
    # Genera connessioni Guide × PDF
    if guide_db:
        for pdf in batch[:5]:
            if len(nuove)>=8: break
            guide_conns = genera_conn_guide(guide_db, pdf)
            for gc in guide_conns:
                kb = pdf["autore"][:18].lower()
                ka = "guide_web"
                if (ka,kb) not in esistenti:
                    nuove.append(gc); esistenti.add((ka,kb))
                    print(f"  ✅ Guide×PDF: Zamnesia+RQS ↔ {pdf['autore'][:20]}")
                    if len(nuove)>=8: break
    
    if nuove: db['connessioni'].extend(nuove)
    db['pdf_letti_134'] = len(letture['letti'])
    db['pdf_totali_134'] = len(tutti_pdf)
    db['pdf_percentuale'] = pct
    db['guide_web_integrate'] = True
    salva_db(db); salva_letture(letture)
    
    # Log
    log = []
    if LOG_PATH.exists():
        try: log = json.loads(LOG_PATH.read_text(encoding='utf-8'))
        except: pass
    log.append({
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "batch": [p["nome"][:30] for p in batch],
        "nuove": len(nuove), "tot_conn": len(db['connessioni']),
        "pdf_letti": len(letture['letti']), "tot_pdf": len(tutti_pdf), "pct": pct,
        "guide_web": bool(guide_db), "modo": "filesystem_v5"
    })
    LOG_PATH.write_text(json.dumps(log[-60:], ensure_ascii=False, indent=2), encoding='utf-8')
    
    print("="*60)
    print(f"✅ DONE — {len(nuove)} nuove | {len(db['connessioni'])} totali | {pct}% PDF | Guide: {'✅' if guide_db else '❌'}")
    print("="*60)

if __name__ == "__main__":
    main()
