#!/usr/bin/env python3
"""
🧠 CERVELLO NOTTURNO — Mini-Serra Living Soil
==============================================
Legge tutti i 58 PDF (elettrocoltura + magia),
estrae concetti chiave, trova connessioni inedite
tra i due domini, aggiorna il database JSON.

Gira ogni notte alle 00:00 UTC via GitHub Actions.
Completamente gratuito — nessuna API esterna.
"""

import json
import os
import re
import hashlib
import random
from datetime import datetime
from pathlib import Path
from collections import defaultdict

try:
    import fitz  # PyMuPDF
    PDF_OK = True
except ImportError:
    PDF_OK = False
    print("⚠️  PyMuPDF non disponibile — uso cache testi")

# ── Percorsi ──
BASE = Path(__file__).parent.parent
DB_PATH = BASE / "manuali" / "esperimenti_database.json"
LOG_PATH = BASE / "scripts" / "cervello_log.json"
ELEC_DIR = BASE / "manuali" / "elettrocultura"
MAGIA_DIR = BASE / "manuali" / "magia"
CACHE_DIR = BASE / "scripts" / "testi_cache"
CACHE_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════
# FASE 1: ESTRAZIONE TESTO DAI PDF
# ═══════════════════════════════════════════════════

def hash_file(path):
    """Hash del file per rilevare modifiche."""
    return hashlib.md5(Path(path).read_bytes()).hexdigest()[:8]

def estrai_testo_pdf(path, max_chars=8000):
    """Estrae testo da un PDF con cache."""
    cache_file = CACHE_DIR / f"{Path(path).stem[:40]}_{hash_file(path)}.txt"
    
    if cache_file.exists():
        return cache_file.read_text(encoding='utf-8')
    
    if not PDF_OK:
        return ""
    
    try:
        doc = fitz.open(str(path))
        testo = ""
        for i, page in enumerate(doc):
            if len(testo) > max_chars:
                break
            testo += page.get_text()
        doc.close()
        
        # Pulisci e normalizza
        testo = re.sub(r'\s+', ' ', testo).strip()
        testo = testo[:max_chars]
        
        # Salva in cache
        cache_file.write_text(testo, encoding='utf-8')
        return testo
    except Exception as e:
        print(f"  ⚠️  Errore {Path(path).name}: {e}")
        return ""

def carica_tutti_pdf():
    """Carica tutti i PDF da entrambe le cartelle."""
    libri = []
    
    for cartella, dominio in [(ELEC_DIR, "elettrocultura"), (MAGIA_DIR, "magia")]:
        if not cartella.exists():
            continue
        for pdf in sorted(cartella.glob("*.pdf")):
            nome = pdf.stem[:60]
            print(f"  📖 {dominio}: {nome[:50]}...")
            testo = estrai_testo_pdf(pdf)
            if testo and len(testo) > 200:
                libri.append({
                    "nome": nome,
                    "dominio": dominio,
                    "path": str(pdf),
                    "testo": testo.lower(),
                    "testo_orig": testo[:2000]  # Prime 2000 chars per la descrizione
                })
    
    print(f"\n📚 PDF caricati: {len(libri)} ({sum(1 for l in libri if l['dominio']=='elettrocultura')} elettroc. + {sum(1 for l in libri if l['dominio']=='magia')} magia)")
    return libri


# ═══════════════════════════════════════════════════
# FASE 2: DIZIONARIO CONCETTI CROSS-DOMINIO
# ═══════════════════════════════════════════════════

# Concetti chiave con sinonimi — usati per trovare sovrapposizioni
CONCETTI = {
    "vibrazione": ["vibrat", "frequenz", "risonan", "oscillaz", "onda", "wave", "vibration", "frequency"],
    "spirale": ["spiral", "helix", "vortex", "vortice", "coil", "bobina", "rotazione"],
    "rame": ["copper", "rame", "cuivre", "kupfer"],
    "elettricita": ["electr", "elettr", "corrente", "current", "voltage", "tensione", "carica"],
    "magnetismo": ["magnet", "polarit", "campo", "field", "north", "south", "nord", "sud"],
    "energia": ["energy", "energia", "forza", "force", "potenza", "power"],
    "luna": ["moon", "luna", "lunar", "lunaire", "ciclo", "cycle"],
    "terra": ["earth", "terra", "soil", "ground", "terreno", "suolo"],
    "acqua": ["water", "acqua", "eau", "liquid"],
    "luce": ["light", "luce", "lumiere", "photon", "fotone", "luminoso"],
    "seme": ["seed", "seme", "germina", "germination", "crescita", "growth"],
    "radice": ["root", "radice", "racine", "rhizome"],
    "cristallo": ["crystal", "cristal", "quartz", "quarzo", "pietra", "stone"],
    "intenzione": ["intent", "intenzione", "will", "volonta", "mind", "mente"],
    "trasformazione": ["transform", "trasform", "alchim", "trasmut", "change"],
    "armonia": ["harmon", "armonia", "equilibrio", "balance", "ordine"],
    "elemento": ["element", "elemento", "terra", "fuoco", "aria", "acqua", "fire"],
    "simbolo": ["symbol", "simbolo", "sigil", "segno", "sign", "pentacolo"],
    "ritmo": ["rhythm", "ritmo", "ciclo", "cycle", "cadenza", "period"],
    "corrente": ["current", "corrente", "flusso", "flow", "stream"],
}

def concetti_nel_testo(testo, soglia=2):
    """Trova quali concetti appaiono nel testo (min soglia occorrenze)."""
    trovati = set()
    for concetto, sinonimi in CONCETTI.items():
        count = sum(testo.count(s) for s in sinonimi)
        if count >= soglia:
            trovati.add(concetto)
    return trovati


# ═══════════════════════════════════════════════════
# FASE 3: TROVA CONNESSIONI CROSS-DOMINIO
# ═══════════════════════════════════════════════════

# Template per generare descrizioni delle connessioni
TEMPLATE_CONNESSIONI = {
    ("vibrazione", "vibrazione"): [
        "{A} e {B} convergono sullo stesso principio: la vibrazione come forza primaria. {A_dom} lo misura in Hz, {B_dom} lo chiama energia sottile — stesso fenomeno, linguaggi diversi.",
        "Sia {A} che {B} insegnano che la vibrazione è alla base di ogni trasformazione. La fisica di {A_dom} e la tradizione di {B_dom} si incontrano su questo punto fondamentale.",
    ],
    ("spirale", "spirale"): [
        "La spirale appare sia in {A} che in {B}: {A_dom} la usa come antenna conduttrice, {B_dom} come simbolo di energia in rotazione. La geometria sacra e la fisica applicata condividono la stessa forma.",
        "{A} e {B} usano entrambi la spirale come strumento di captazione energetica. Christofleau e la tradizione ermetica hanno scoperto indipendentemente lo stesso segreto geometrico.",
    ],
    ("elettricita", "energia"): [
        "Ciò che {A} chiama elettricità, {B} chiama energia vitale o prana. La scoperta di {A_dom} che le piante rispondono ai campi elettrici rispecchia ciò che {B_dom} insegna da secoli.",
        "{A} misura in Volt quello che {B} descrive come forza invisibile. Entrambi documentano lo stesso effetto: campi energetici non visibili che influenzano la vita.",
    ],
    ("luna", "luna"): [
        "{A} e {B} confermano entrambi l'influenza lunare sui processi vitali. La biodinamica moderna di {A_dom} e la tradizione di {B_dom} convergono: la luna governa i cicli della vita.",
        "La connessione luna-piante documentata in {A} trova conferma nei testi di {B}. La scienza del {A_dom} e la saggezza del {B_dom} parlano con una sola voce.",
    ],
    ("magnetismo", "energia"): [
        "{A} misura i campi magnetici con strumenti scientifici; {B} li descrive come correnti energetiche sottili. La magnetite nelle piante, documentata da {A_dom}, era già nota alla tradizione di {B_dom}.",
        "Il campo magnetico terrestre — centrale in {A} — è lo stesso 'campo di forza' che {B} descrive nel suo linguaggio. Due discipline, una sola realtà fisica.",
    ],
    ("acqua", "acqua"): [
        "L'acqua strutturata di {A} e l'acqua come elemento sacro di {B}: entrambi riconoscono che l'acqua ha proprietà che vanno oltre la chimica. Schauberger e la tradizione esoterica concordano.",
        "{A} e {B} trattano l'acqua come un essere vivente con memoria. La scienza {A_dom} lo studia con esperimenti; {B_dom} lo sa da millenni.",
    ],
    ("intenzione", "elettricita"): [
        "{A} documenta che l'intenzione del coltivatore influenza la crescita (misurabile con galvanometro). {B} insegna che la volontà è la forza più potente. Tompkins e {B_dom} hanno scoperto la stessa legge.",
        "Il campo elettromagnetico del cervello umano, studiato in {A}, interagisce con le piante. {B} chiama questo 'potere della mente' — la scienza di {A_dom} lo sta ora misurando.",
    ],
    ("cristallo", "elettricita"): [
        "I cristalli di magnetite nelle piante (documentati in {A}) sono anche amplificatori energetici in {B}. La fisica e la tradizione {B_dom} concordano: i cristalli trasmettono e amplificano campi.",
        "{A} usa il quarzo per le sue proprietà piezoelettriche; {B} usa i cristalli come amplificatori rituali. Stesso materiale, stessa funzione — scoperto da due tradizioni separate.",
    ],
    ("simbolo", "elettricita"): [
        "I sigilli fisici di {B} (Pantacolo, Sigillo di Salomone) e le antenne di {A} condividono la funzione: concentrare e dirigere energia. Il metallo fisico inciso è anche antenna.",
        "{B} disegna simboli conduttivi su metallo per amplificare l'intenzione. {A} scopre che le spirali di rame amplificano i campi elettrici. Stesso principio, 500 anni di distanza.",
    ],
    ("trasformazione", "terra"): [
        "Il Living Soil di {A} è alchimia applicata: materia morta si trasforma in vita. {B} descrive questo come il Grande Opus — Solve et Coagula. La microbiologia moderna e l'alchimia antica descrivono la stessa trasformazione.",
        "{A} dimostra che la decomposizione crea nutrimento; {B} chiama questo processo 'la via della putrefazione sacra'. Bokashi, compost e alchimia — tutti parlano della stessa trasmutazione.",
    ],
}

def genera_descrizione(concetto1, concetto2, libro_a, libro_b):
    """Genera una descrizione per la connessione trovata."""
    chiave = (concetto1, concetto2) if (concetto1, concetto2) in TEMPLATE_CONNESSIONI else \
             (concetto2, concetto1) if (concetto2, concetto1) in TEMPLATE_CONNESSIONI else \
             (concetto1, "energia") if (concetto1, "energia") in TEMPLATE_CONNESSIONI else \
             ("vibrazione", "vibrazione")  # fallback
    
    templates = TEMPLATE_CONNESSIONI.get(chiave, TEMPLATE_CONNESSIONI[("vibrazione", "vibrazione")])
    template = random.choice(templates)
    
    nome_a = libro_a['nome'].split(' ')[0:3]
    nome_a = ' '.join(nome_a)[:40]
    nome_b = libro_b['nome'].split(' ')[0:3]
    nome_b = ' '.join(nome_b)[:40]
    
    return template.format(
        A=nome_a, B=nome_b,
        A_dom=libro_a['dominio'],
        B_dom=libro_b['dominio']
    )

def trova_connessioni_nuove(libri, connessioni_esistenti, max_nuove=8):
    """
    Trova connessioni CROSS-DOMINIO tra libri di elettrocultura e magia.
    Mai stesso dominio con stesso dominio.
    """
    print("\n🔍 Cerco connessioni cross-dominio...")
    
    # Separa per dominio
    elec = [l for l in libri if l['dominio'] == 'elettrocultura']
    magia = [l for l in libri if l['dominio'] == 'magia']
    
    # Calcola concetti per ogni libro
    for libro in libri:
        libro['concetti'] = concetti_nel_testo(libro['testo'])
    
    # Coppie già esistenti nel DB (per evitare duplicati)
    coppie_esistenti = set()
    for c in connessioni_esistenti:
        a = c.get('a', c.get('da', ''))[:30].lower()
        b = c.get('b', c.get('a', ''))[:30].lower()
        coppie_esistenti.add((a, b))
        coppie_esistenti.add((b, a))
    
    nuove = []
    
    # Incrocia SOLO elettrocultura × magia
    for libro_e in elec:
        for libro_m in magia:
            if len(nuove) >= max_nuove:
                break
            
            # Concetti in comune
            comuni = libro_e['concetti'] & libro_m['concetti']
            if len(comuni) < 2:
                continue
            
            # Evita duplicati
            chiave_a = libro_e['nome'][:25].lower()
            chiave_b = libro_m['nome'][:25].lower()
            if (chiave_a, chiave_b) in coppie_esistenti:
                continue
            
            # Prendi i 2 concetti più significativi
            concetti_list = list(comuni)[:2]
            c1, c2 = concetti_list[0], concetti_list[-1]
            
            # Genera la connessione
            descrizione = genera_descrizione(c1, c2, libro_e, libro_m)
            
            # Nome pulito dei libri
            nome_e = estrai_nome_autore(libro_e['nome'])
            nome_m = estrai_nome_autore(libro_m['nome'])
            
            connessione = {
                "a": nome_e,
                "b": nome_m,
                "nota": descrizione,
                "tags": list(comuni)[:4],
                "generata": datetime.now().strftime("%Y-%m-%d"),
                "tipo": "sinergia"
            }
            
            nuove.append(connessione)
            coppie_esistenti.add((chiave_a, chiave_b))
            print(f"  ✅ {nome_e[:35]} ↔ {nome_m[:35]}")
            print(f"     Concetti comuni: {', '.join(list(comuni)[:3])}")
    
    return nuove

def estrai_nome_autore(nome_file):
    """Estrae un nome leggibile dal nome del file PDF."""
    # Rimuovi estensione e caratteri speciali
    nome = nome_file
    # Cerca autore in parentesi tipo "(Christofleau Justin)"
    match = re.search(r'\(([^)]+)\)', nome)
    if match:
        autore = match.group(1).split(',')[0].strip()
        # Estrai titolo (prima delle parentesi)
        titolo = nome[:nome.find('(')].strip()
        titolo = titolo.replace('-', ' ').replace('_', ' ')
        titolo = re.sub(r'\s+', ' ', titolo)[:35]
        return f"{titolo} ({autore})"
    
    # Altrimenti usa le prime parole del nome file
    nome = nome.replace('-', ' ').replace('_', ' ')
    nome = re.sub(r'\s+', ' ', nome).strip()
    parole = nome.split()[:4]
    return ' '.join(parole)


# ═══════════════════════════════════════════════════
# FASE 4: AGGIORNA DATABASE
# ═══════════════════════════════════════════════════

def aggiorna_database(nuove_connessioni):
    """Aggiunge le nuove connessioni al database JSON."""
    db = json.loads(DB_PATH.read_text(encoding='utf-8'))
    
    n_prima = len(db['connessioni'])
    db['connessioni'].extend(nuove_connessioni)
    n_dopo = len(db['connessioni'])
    
    # Aggiorna metadata
    db['ultimo_aggiornamento'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    v = db.get("versione", "0"); db["versione"] = str(float(v) + 0.1)[:5]
    
    DB_PATH.write_text(
        json.dumps(db, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    
    print(f"\n💾 Database aggiornato: {n_prima} → {n_dopo} connessioni (+{n_dopo-n_prima})")
    return n_dopo - n_prima


# ═══════════════════════════════════════════════════
# FASE 5: LOG
# ═══════════════════════════════════════════════════

def salva_log(nuove, pdf_letti):
    """Salva un log dell'esecuzione notturna."""
    log = []
    if LOG_PATH.exists():
        try:
            log = json.loads(LOG_PATH.read_text(encoding='utf-8'))
        except:
            log = []
    
    log.append({
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "pdf_analizzati": pdf_letti,
        "connessioni_trovate": len(nuove),
        "nuove_connessioni": [
            {"a": c["a"][:40], "b": c["b"][:40]}
            for c in nuove
        ]
    })
    
    # Mantieni solo ultimi 30 log
    log = log[-30:]
    LOG_PATH.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')


# ═══════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("🧠 CERVELLO NOTTURNO — Mini-Serra Living Soil")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. Carica tutti i PDF
    print("\n📖 FASE 1: Carico i PDF...")
    libri = carica_tutti_pdf()
    
    if len(libri) < 4:
        print("⚠️  Troppo pochi PDF caricati — probabilmente manca PyMuPDF")
        print("    Aggiungo connessioni predefinite di backup...")
        libri = []
    
    # 2. Leggi connessioni esistenti
    print("\n📊 FASE 2: Leggo database esistente...")
    db = json.loads(DB_PATH.read_text(encoding='utf-8'))
    connessioni_esistenti = db.get('connessioni', [])
    print(f"   Connessioni esistenti: {len(connessioni_esistenti)}")
    
    # 3. Trova nuove connessioni
    print("\n🔗 FASE 3: Cerco nuove connessioni cross-dominio...")
    if libri:
        nuove = trova_connessioni_nuove(libri, connessioni_esistenti, max_nuove=5)
    else:
        # Connessioni di fallback se i PDF non sono leggibili
        nuove = genera_connessioni_fallback(connessioni_esistenti)
    
    if not nuove:
        print("   Nessuna nuova connessione trovata oggi (tutte già catalogate)")
        return
    
    print(f"\n🎯 Trovate {len(nuove)} nuove connessioni!")
    
    # 4. Aggiorna database
    print("\n💾 FASE 4: Aggiorno database...")
    n_aggiunte = aggiorna_database(nuove)
    
    # 5. Salva log
    salva_log(nuove, len(libri))
    
    print("\n" + "=" * 60)
    print(f"✅ COMPLETATO — {n_aggiunte} nuove connessioni aggiunte")
    print("   L'app le mostrerà dal prossimo aggiornamento")
    print("=" * 60)


def genera_connessioni_fallback(esistenti):
    """
    Connessioni di riserva basate su analisi manuale profonda,
    usate quando i PDF non sono leggibili (es. prima run senza PyMuPDF).
    Sempre CROSS-dominio: mai stesso libro con stesso libro.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    pool_fallback = [
        {
            "a": "Lemstrom — Electricity in Agriculture (1904)",
            "b": "Tavole Smeraldine — Thoth Trismegisto",
            "nota": "Lemstrom captava l'energia cosmica con fili orizzontali nel 1904. Le Tavole Smeraldine insegnano 'ciò che è in alto è come ciò che è in basso' — la stessa energia cosmica scende sulla Terra. Lemstrom costruì antenne fisiche per catturare quello che Thoth descrisse come legge universale.",
            "tags": ["lemstrom", "tavole-smeraldine", "energia-cosmica", "alto-basso"],
            "generata": today, "tipo": "sinergia"
        },
        {
            "a": "Tompkins & Bird — La Vita Segreta delle Piante",
            "b": "Magick — Aleister Crowley",
            "nota": "Tompkins misurò con galvanometro che le piante rispondono alle emozioni umane. Crowley insegnava che la volontà focalizzata è la forza più potente. Entrambi documentano lo stesso fenomeno: la coscienza umana influenza la materia vivente in modo misurabile.",
            "tags": ["tompkins", "crowley", "coscienza", "volonta", "misura"],
            "generata": today, "tipo": "sinergia"
        },
        {
            "a": "Viktor Schauberger — Acqua Vortice",
            "b": "Il Kybalion — I Tre Iniziati",
            "nota": "Schauberger scoprì che l'acqua in movimento vortice sviluppa proprietà vitali superiori. Il Kybalion insegna il Principio di Ritmo e Vibrazione come legge fondamentale. Il vortice di Schauberger è la manifestazione fisica del ritmo cosmico del Kybalion applicato all'acqua.",
            "tags": ["schauberger", "kybalion", "vortice", "ritmo", "acqua"],
            "generata": today, "tipo": "sinergia"
        },
        {
            "a": "Elaine Ingham — The Soil Biology Primer",
            "b": "Registri Akashici — Melissa Gomes",
            "nota": "Ingham dimostrò che ogni cucchiaio di suolo sano contiene miliardi di organismi con relazioni complesse — una rete di memoria biologica. I Registri Akashici descrivono la memoria universale di ogni essere. Il suolo vivente è il Registro Akashico della Terra.",
            "tags": ["ingham", "akashici", "memoria", "suolo", "rete"],
            "generata": today, "tipo": "sinergia"
        },
        {
            "a": "Ighina — L'Atomo Magnetico (1954)",
            "b": "Esoterismo: Wicca, Rune, Magia delle Candele",
            "nota": "Ighina descrisse l'atomo magnetico come forza primordiale che permea tutto. La Wicca lavora con le forze elementali della natura attraverso rituali precisi. Entrambi insegnano che forze invisibili e magnetiche governano la vita — Ighina le misura, la Wicca le invoca.",
            "tags": ["ighina", "wicca", "magnetico", "forze-elementali", "invisibile"],
            "generata": today, "tipo": "sinergia"
        },
    ]
    
    # Filtra quelle già esistenti
    coppie_es = set()
    for c in esistenti:
        coppie_es.add(c.get('a','')[:20].lower())
        coppie_es.add(c.get('b','')[:20].lower())
    
    nuove = []
    for c in pool_fallback:
        if c['a'][:20].lower() not in coppie_es and c['b'][:20].lower() not in coppie_es:
            nuove.append(c)
            if len(nuove) >= 3:
                break
    
    return nuove


if __name__ == "__main__":
    main()
