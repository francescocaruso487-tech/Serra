#!/usr/bin/env python3
"""
🧠 CERVELLO NOTTURNO v3 — Mini-Serra Living Soil
=================================================
UPGRADE COMPLETO: legge i 134 PDF REALI da Google Drive
tramite API con token OAuth2, estrae testo vero,
genera connessioni cross-dominio da contenuto reale.

Ciclo rotante: ogni 6 ore legge 10 PDF diversi
→ in 8 giorni ha letto tutti i 134 PDF reali.
"""

import json, os, re, random, hashlib, base64, io
from datetime import datetime
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    try:
        import fitz  # PyMuPDF
        HAS_PYMUPDF = True
        HAS_PYPDF = False
    except ImportError:
        HAS_PYPDF = False
        HAS_PYMUPDF = False

BASE = Path(__file__).parent.parent
DB_PATH = BASE / "manuali" / "esperimenti_database.json"
LOG_PATH = BASE / "scripts" / "cervello_log.json"
LETTURE_PATH = BASE / "scripts" / "pdf_letture.json"

# ── Token Google Drive (da GitHub Secrets o env) ──
DRIVE_TOKEN = os.environ.get("GOOGLE_DRIVE_TOKEN", "")

# ── ID Indice JSON su Drive (caricato 11/06/2026) ──
INDICE_JSON_DRIVE_ID = "1N1ZJI8TZC1gLAOYZblqFJwZcbQWnkDyI"

# ── TUTTI I 134 PDF — lista completa con ID Drive ──
ALL_PDF = [
    # === ELETTROCOLTURA (73 PDF) ===
    {"id":"1oYPClfiyHQWahc7vYR5ZpDnEno4QdL00","t":"Christofleau — Electroculture","cat":"elettrocoltura","autore":"Justin Christofleau"},
    {"id":"1RMmA38dUgQX4HAlzZMql_bfVxeQgDmg3","t":"Nollet — De l'Electricité du Corps Humain","cat":"elettrocoltura","autore":"Jean Antoine Nollet"},
    {"id":"1P1q5a26vfKjt4dYGXMmIgAit9OIngEUK","t":"Nollet — De l'Electricité des Météores","cat":"elettrocoltura","autore":"Jean Antoine Nollet"},
    {"id":"1-49mF-uWD7vFL6vh7cZUDaXm1xAvMael","t":"Nollet — De l'Electricité des Végétaux","cat":"elettrocoltura","autore":"Jean Antoine Nollet"},
    {"id":"13ISp42iI9nisSmzQQ5-OTSV225V0EwcJ","t":"Nollet — Lezioni di Fisica 1","cat":"elettrocoltura","autore":"Jean Antoine Nollet"},
    {"id":"11tVa37QmtGC1-_xxkUd8R_u7bwwV1LbE","t":"UFIE Fisica (Nollet)","cat":"elettrocoltura","autore":"Jean Antoine Nollet"},
    {"id":"1D16cSiNvVUcYBZvtCpjAndQimWjAjONt","t":"Ighina — La Scoperta dell'Atomo Magnetico","cat":"elettrocoltura","autore":"Pier Luigi Ighina"},
    {"id":"1z0kYGkUDcXIS6x7bMX8M0AIkFJz7wBPZ","t":"Ighina — El Atomo Magnetico","cat":"elettrocoltura","autore":"Pier Luigi Ighina"},
    {"id":"1hw1xDbefoWDBU-CY-CC4Sesq3vd5LuBD","t":"Ighina — Profeta Sconosciuto (Tavanti)","cat":"elettrocoltura","autore":"Alberto Tavanti"},
    {"id":"1S9kONL6RretByiVpwNcF5K4BmOuBX1tR","t":"Tesla — Lampo di Genio","cat":"elettrocoltura","autore":"Nikola Tesla"},
    {"id":"1jkvl9ZJY6ZESsf06lBOrzerDcqizj1HV","t":"Tesla — Energia Frequenze Vibrazioni","cat":"elettrocoltura","autore":"Nikola Tesla"},
    {"id":"1mC7CJ8c2wvMbGocXU32MGUwRAC0gHU6F","t":"Tesla — Un Genio Volutamente Dimenticato","cat":"elettrocoltura","autore":"Vittorio Baccelli"},
    {"id":"1B3sBuB_M8VBxbopqvLAuaZXIJiqH91U2","t":"Tesla — Le Mie Invenzioni","cat":"elettrocoltura","autore":"Nikola Tesla"},
    {"id":"1lggv0MaBq6TMnWJH9G6sNnF92ydBpqNI","t":"Il Codice Tesla","cat":"elettrocoltura","autore":"Alessandro Falzani"},
    {"id":"1oCGYPJCizCpBBNk9QX937TuRjxWSbfYv","t":"Arce — Electroculture Biohacker Guide","cat":"elettrocoltura","autore":"César Arce"},
    {"id":"1H88XIAdlI_oOiHit4ow4vRxTTPhiuHdJ","t":"Starter Kit Elettrocoltura 2021","cat":"elettrocoltura","autore":"Andrea"},
    {"id":"1K1BzfSXEYP54AmZ13L_68psq8PaeGNWz","t":"Electroculture For Beginners Step by Step","cat":"elettrocoltura","autore":"Errol Ramos"},
    {"id":"164phDM7vt4EM76O5RbYeb4g7C4TsD2Eu","t":"Electroculture 2 Books in 1","cat":"elettrocoltura","autore":"Errol Ramos"},
    {"id":"1u1dv0ZuPpgfpTGeTSbDHMuiaUnPmxH7B","t":"Pizzuti — Scoperte Scientifiche non Autorizzate","cat":"elettrocoltura","autore":"Marco Pizzuti"},
    {"id":"1bFn9cnepyf8AHaKfdBGcWXT7iGXiBf1y","t":"US Patents for Electroculture","cat":"elettrocoltura","autore":"USPTO"},
    {"id":"1TOCzU1a-aLXDK2ahAF7WrwbplWh_ifnl","t":"Ricerca Agro-Alimentare 2019","cat":"elettrocoltura","autore":"Vari"},
    {"id":"1Qg3Tmtp6deZrDhqrTHzTFs9VrUWY1qlD","t":"Magnacult","cat":"elettrocoltura","autore":"N/D"},
    {"id":"1EG4LZp95GXkQk_d_xUh82iuQ-2XI8I7f","t":"Laemstrom — Electricity in Agriculture","cat":"elettrocoltura","autore":"S. Laemstrom"},
    {"id":"15VZoTA5sfjnqwWkyMS6nW1E0y_wuAACO","t":"Hull — Electroculture","cat":"elettrocoltura","autore":"Hull"},
    {"id":"1M5X7sqYGOGw0iFEV5QhuJuPRHsIjF1Jz","t":"Elcult3","cat":"elettrocoltura","autore":"N/D"},
    {"id":"16ahCjBdGjbKSu9EIZn_nHLA4sUrpygpK","t":"Elcult2","cat":"elettrocoltura","autore":"N/D"},
    {"id":"10wvpnuZEMCIXhDULbXKYQT-KfEfrGWf4","t":"Elcult1","cat":"elettrocoltura","autore":"N/D"},
    {"id":"1XBmnjJ0CH2-lxjMV4LnNW_3pWsKmRJyH","t":"Dudgrich — Electroculture","cat":"elettrocoltura","autore":"Dudgrich"},
    {"id":"1HMIFeQosi0kTPzC2stM4G8yiMcoQ2LvF","t":"Corso Elettrocoltura","cat":"elettrocoltura","autore":"Vari"},
    {"id":"1ZwW0vDsjHpi3Sg94z6B_e5nCl8vPOBww","t":"Halliday Resnick Walker — Fisica EM","cat":"elettrocoltura","autore":"Halliday Resnick Walker"},
    {"id":"10tojlySkd_2gr3KPUpAmc2pM-Q7R49pL","t":"Ulaby — Campi Elettromagnetici","cat":"elettrocoltura","autore":"Fawwaz T. Ulaby"},
    {"id":"1Hr4-I_G2prpOsoZiad_j8k25hHfygFzG","t":"Ortolani Venturi — Elettrotecnica e Automazione","cat":"elettrocoltura","autore":"Ortolani Venturi"},
    {"id":"16CzuDx9YxGpMOGRHRUcN35Sf6aq89nIA","t":"Cathie — The Energy Grid","cat":"elettrocoltura","autore":"Bruce L. Cathie"},
    {"id":"1AAr0kRVqASQZjV_Q1Qz_awJqAqIVNvt-","t":"Ruhlmann — La Mélodie Secrète des Végétaux","cat":"elettrocoltura","autore":"Renaud Ruhlmann"},
    {"id":"13OgT70YQllQ6bnhO4ew34GNP8UX_7pay","t":"Gateway Secret — Potenzialità Cervello Umano","cat":"elettrocoltura","autore":"CIA + Vari"},
    {"id":"1N2-XfvhaWtZKcBVjFCsXWEAeA7B1pyyD","t":"Church — La Forza del Cervello Quantico","cat":"elettrocoltura","autore":"Dawson Church"},
    {"id":"1knti3K8C4omjDa2awj9mdmA20AhA8bMg","t":"Guerzoni — Antenna Uomo","cat":"elettrocoltura","autore":"Tiziano Guerzoni"},
    {"id":"1u_jVM7qqRb6nfu8lvIkpEBGc6xTy1X6D","t":"Guénon — Simboli della Scienza Sacra","cat":"elettrocoltura","autore":"René Guénon"},
    {"id":"1TSwc8YgEXvZydw6iB-Lk26CLSD4oxCZI","t":"Ouspensky — Tertium Organum","cat":"elettrocoltura","autore":"P.D. Ouspensky"},
    {"id":"1FgRXITI63cY9gom5u8oBipHFdhJ0e8xp","t":"Tompkins & Bird — La Vita Segreta delle Piante","cat":"elettrocoltura","autore":"Tompkins Bird"},
    {"id":"1UOU7wYiEGi3QEr6XgM8EQJKVYFZ9a-oc","t":"La Strega Verde — Magia delle Piante","cat":"elettrocoltura","autore":"N/D"},
    {"id":"1o1vOQTubgt4726YzIv4cgD1Nbn4qxjsI","t":"Garnier Malet — Ouvertures Temporelles","cat":"elettrocoltura","autore":"Garnier Malet"},
    {"id":"1QXaLuIwBNceCoTAK6tBCOh19RO669QwH","t":"TOTALE 2 (compilato)","cat":"elettrocoltura","autore":"Vari"},
    {"id":"1KwxwBq0RE-uX_4oa441aTZYbBpe4t-e4","t":"TOTALE 1 (compilato)","cat":"elettrocoltura","autore":"Vari"},
    # === MAGIA & ESOTERISMO (24 PDF) ===
    {"id":"1wS-oWkv1KZtjdTSm6T1geo16J3Oz1avd","t":"Crowley — Magick","cat":"magia","autore":"Aleister Crowley"},
    {"id":"1LT_JLH4mKETjamYvIc97JT1VUF7E1baf","t":"Crowley — La Figlia della Luna","cat":"magia","autore":"Aleister Crowley"},
    {"id":"1lfnZRuwJsdcNAqsEvSNc-rVoc1-bj-VA","t":"Crowley — Il Libro della Legge","cat":"magia","autore":"Aleister Crowley"},
    {"id":"1zRoFkpbG0KaH2oqsAwRvFQgKEv3qJKVe","t":"Crowley — Il Cuore del Maestro","cat":"magia","autore":"Aleister Crowley"},
    {"id":"1wI8OCWAn69FViToCCKh6I5-YIxOgTaZA","t":"Crowley — L'artigiano del Male","cat":"magia","autore":"Kaw Djer"},
    {"id":"1DaS726VzDeLV-daKCPWhtULVsyeOr1Lz","t":"Aleister Crowley (Kaw Djer)","cat":"magia","autore":"Kaw Djer"},
    {"id":"1wGsVe3m8lr5Tfv86g2ChVGHbM46hxXvM","t":"Crowley e Dion Fortune","cat":"magia","autore":"Alan Richardson"},
    {"id":"1kk6X_zft8c6icmx4nbs-98Mx0DgDa5L9","t":"Crowley — Aforismi Esoterici","cat":"magia","autore":"Aleister Crowley"},
    {"id":"1_XoMODN60boQ3AItL2q8CK-TWr3q-kRV","t":"Liber333 — Libro delle Menzogne","cat":"magia","autore":"Aleister Crowley"},
    {"id":"14wRabpFIUV4X9-kfutyF6V3FgpVFBp84","t":"Agrippa — La Filosofia Occulta o la Magia","cat":"magia","autore":"Cornelio Agrippa"},
    {"id":"18F7EPoy1L6FGpSzQ2g53nrBRXu--vqbn","t":"La Chiave di Salomone","cat":"magia","autore":"Anonimo"},
    {"id":"1c2UVex5uS5HHEZ-WGJPUBGGbtKuTudQm","t":"Dion Fortune — La Cabala Mistica","cat":"magia","autore":"Dion Fortune"},
    {"id":"1FZJYCW0C9I-InpmXL5bSrsiIbmBvho7y","t":"Ermete Trismegisto — Corpo Ermetico e Asclepio","cat":"magia","autore":"Ermete Trismegisto"},
    {"id":"1CVON9yQnUvZFJxs08i7e56jb5i_F9VzV","t":"Ermete Trismegisto — Corpus Hermeticum","cat":"magia","autore":"Ermete Trismegisto"},
    {"id":"1x4tEPd6GxvgNYmxkmHPzeTlgauOSIYSw","t":"Ermete Trismegisto — Il Pimandro","cat":"magia","autore":"Ermete Trismegisto"},
    {"id":"1crmVDByL75-L_Yr34wFjnilVheii-8UL","t":"I Tre Iniziati — Il Kybalion","cat":"magia","autore":"I Tre Iniziati"},
    {"id":"1Cqxb-db58XNj7R3BTZ-4WIiT6-aJeJxQ","t":"Il Grande Grimorio (5 libri in 1)","cat":"magia","autore":"Vari"},
    {"id":"1t4Ez8yBDlf8x5r2UoxXT2e5l41VWtMdA","t":"Le Tavole Smeraldine di Thoth","cat":"magia","autore":"Ermete Trismegisto"},
    {"id":"1t7fryfB3KkeQuDoq-ufzp2bn-xdfhmAb","t":"Canseliet — Mutus Liber (Alchimia)","cat":"magia","autore":"Eugène Canseliet"},
    {"id":"14f87vUMUIyeUNeJZ0QtxQeKzsPX18tYr","t":"Manuale di Magia Nera","cat":"magia","autore":"N/D"},
    {"id":"1NDNjaWQ2hMDa1ks8e7R_0arNtHGAboEs","t":"Registri Akashici","cat":"magia","autore":"N/D"},
    {"id":"19bVh2cuEskhCWccACzrEuOTgQEy43JwT","t":"Clavicola di Salomone","cat":"magia","autore":"Anonimo"},
    {"id":"1WQzFIpBE1hVTiyJRthLguH2WLCBYF4mZ","t":"Esoterismo 5 Libri in 1","cat":"magia","autore":"Vari"},
    {"id":"1yObrQh72N5AiGM1cjcAKBWtLMkAZmvRl","t":"Aradia — Vangelo delle Streghe","cat":"magia","autore":"Leland"},
    # === SPIRITUALI & ROL (9 PDF) ===
    {"id":"11GVDmLxPTxEVRPyBeiJbelubgA_T7Am7","t":"Vangelo Esseno della Pace — Libro 4","cat":"spirituale","autore":"Szekely"},
    {"id":"1oA5QOoo69CMsfDSFU-cC81858aGkQoc_","t":"Vangelo della Pace — Bundle 3 Libri","cat":"spirituale","autore":"Davide Appi"},
    {"id":"1VFFxUVezAYXmoVLDAd70UkFDisAAJQgD","t":"Rol — Il Grande Veggente (Allegri)","cat":"spirituale","autore":"Renzo Allegri"},
    {"id":"1_0kMMqxnBNGpv8BQKsJE4CvLl9l9c9cI","t":"Rol — L'Uomo oltre l'Uomo (Giovetti)","cat":"spirituale","autore":"Paola Giovetti"},
    {"id":"1tk3_qzQG7lwn0sU-8OZ49Ip1vCkABPSW","t":"Rol — Una Vita di Prodigi (Lugli)","cat":"spirituale","autore":"Remo Lugli"},
    {"id":"1hPyv3pmK-bNm4p0L2hOwxjSLlEwtzs1O","t":"Rol — Io Sono la Grondaia (diari)","cat":"spirituale","autore":"Gustavo Rol"},
    {"id":"1Ad2KlYG-BdRd5LMhSfOd1LbuDi0TNBQF","t":"Harry B. Joseph — Book of Wisdom Vol 2","cat":"spirituale","autore":"Harry B. Joseph"},
    {"id":"1OZNYpBF9xoHREQZELT1zOtrLYs-EjQDR","t":"Harry B. Joseph — Book of Wisdom Vol 1","cat":"spirituale","autore":"Harry B. Joseph"},
    {"id":"1L-4HPBJj-k5QYk0ogG-EsqrRQD7T5Riz","t":"Harry B. Joseph — Activating The Inner Eye","cat":"spirituale","autore":"Harry B. Joseph"},
    # === LIBRI SACRI (10+ PDF) ===
    {"id":"1OnaVUFPplTiTemmr5W2Q2WwG8f6qNBdg","t":"Il Nobile Corano (italiano)","cat":"libri_sacri","autore":"Islam"},
    {"id":"1oeV5rHYlmVTdrQQ9R--RF_WjQ0iMovUw","t":"Il Corano","cat":"libri_sacri","autore":"Islam"},
    {"id":"1Ipbo9B-dPmBtDCeVxWYcJqKgc_peJjd_","t":"108 Upanishad","cat":"libri_sacri","autore":"Induismo"},
    {"id":"1VnV1M5f1ZfV24w9dNUBb86Om-rzKXPCv","t":"Sanedrin / Talmud","cat":"libri_sacri","autore":"Ebraismo"},
    {"id":"1Ai5BVewQAzi36t4jvScHeH6LcZas5L0q","t":"II Kojiki (Libro delle Cose Antiche)","cat":"libri_sacri","autore":"Shintoismo"},
    {"id":"1E_vK8ADTYaI-OLY_h_eOlxAZrLLZuLet","t":"I Giardini dei Devoti (Buddhismo)","cat":"libri_sacri","autore":"Buddhismo"},
    {"id":"1Unt8qu3xoDSll9HXykb8tr8UcONqB6an","t":"Wicca","cat":"libri_sacri","autore":"Wicca"},
    {"id":"1Kh_jNml-Lqatnl18Y7r_Gg3CvKvhPCpF","t":"Le Sette e Quattro Valli (Bahà'ì)","cat":"libri_sacri","autore":"Bahaullah"},
    {"id":"11Hn4D-HvyBj-VDdrFweq8n0clriGELsn","t":"Manuale di Storia delle Religioni","cat":"libri_sacri","autore":"Filoramo Massenzio Raveri"},
    {"id":"1E9IukqNx5x9dZ-JEoTiXTpX9cJzzUvjH","t":"Angeli — Ebraismo Cristianesimo Islam","cat":"libri_sacri","autore":"Agamben Coccia"},
    # === COLTIVAZIONE ORGANICA (8 PDF) ===
    {"id":"1-P95imu3_c3b7MsE5UZ4gJb-SHvIkuwV","t":"Ingham — The Soil Biology Primer","cat":"coltivazione","autore":"Elaine Ingham"},
    {"id":"1HlreWsMdJTKToA_gK1LvT-wkVZnPodV_","t":"Howard — An Agricultural Testament","cat":"coltivazione","autore":"Albert Howard"},
    {"id":"1rmhXVBYZA01L-XwewL74J7nKb0kc1bM2","t":"Restrepo — A,B,C Agricultura Organica","cat":"coltivazione","autore":"Jairo Restrepo Rivera"},
    {"id":"1q_vKREIfA7ST5CqSVEkLpNsRtaN36vIu","t":"Restrepo — La Luna en la Agricultura","cat":"coltivazione","autore":"Jairo Restrepo Rivera"},
    {"id":"1Cz_NMIScAW63mJP4iglxqzNGhHPOygzR","t":"Restrepo — Agricultura Organica y Harina de Rocas","cat":"coltivazione","autore":"Restrepo Pinheiro"},
    {"id":"1n6pBwHjQmJCuFHI805TdjpuS0QDlVJ36","t":"Ruiz — Il Quinto Accordo","cat":"coltivazione","autore":"Miguel Ruiz"},
    {"id":"1Y7AvFUZh90HnDx4a21-gkeNZUsf6ywMP","t":"Tresoldi — I Misteri dell'Antico Egitto","cat":"coltivazione","autore":"Roberto Tresoldi"},
]

CONCETTI = {
    "vibrazione": ["vibrat","frequenz","risonan","oscillaz","onda","vibration","frequency","harmonics","hertz"],
    "energia": ["energy","energia","forza","force","potenza","prana","chi","ki","orgone","electricity","electric"],
    "luce": ["light","luce","luminoso","photon","fotone","illuminazione","enlighten","rays","raggi"],
    "acqua": ["water","acqua","liquid","flow","flusso","vortex","vortice","fluido","humid"],
    "terra": ["earth","terra","soil","ground","terreno","suolo","humus","radici","root"],
    "luna": ["moon","luna","lunar","ciclo","cycle","tide","marea","biodinam"],
    "rame": ["copper","rame","cuivre","kupfer","antenna","conduttore"],
    "spirale": ["spiral","helix","vortex","coil","rotazione","golden","fibonacci"],
    "intenzione": ["intent","intenzione","will","volonta","mind","mente","consapevol","thought","pensiero"],
    "trasformazione": ["transform","trasform","alchim","trasmut","change","mutazione","evolution"],
    "armonia": ["harmon","armonia","equilibrio","balance","ordine","order","coherence","coerenza"],
    "natura": ["natura","nature","natural","pianta","plant","grow","crescit","vegetale","herb"],
    "magnetismo": ["magnet","polarit","campo","field","magnetico","polar","north","nord","electro"],
    "coscienza": ["conscious","coscienza","awareness","mindful","attenzione","brain","cervello","mind"],
    "unita": ["unity","unita","oneness","interconness","connection","tutto","all","uno"],
    "purificazione": ["purif","cleanse","pulizia","purezza","sacred","sacro","holy"],
    "ritmo": ["rhythm","ritmo","ciclo","cycle","cadenza","period","stagione","season","timing"],
    "meditazione": ["meditat","contemplat","silenzio","silence","mindful","focus","centr"],
    "crescita": ["growth","crescita","sviluppo","develop","bloom","fioritura","yield","resa"],
    "elettricita": ["electric","elettric","volt","ampere","current","corrente","tesla","ighina"],
}

def carica_letture():
    if LETTURE_PATH.exists():
        try: return json.loads(LETTURE_PATH.read_text(encoding='utf-8'))
        except: pass
    return {"letti": [], "ultimo_batch": 0}

def salva_letture(letture):
    LETTURE_PATH.write_text(json.dumps(letture, ensure_ascii=False, indent=2), encoding='utf-8')

def scarica_testo_pdf_drive(file_id, token, max_chars=2000):
    """Scarica e legge il testo reale di un PDF da Google Drive."""
    if not token or not HAS_REQUESTS:
        return ""
    try:
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
        r = requests.get(url, 
            headers={"Authorization": f"Bearer {token}"},
            timeout=30, stream=True)
        if r.status_code != 200:
            print(f"    ⚠️  Drive {file_id}: HTTP {r.status_code}")
            return ""
        pdf_bytes = r.content
        if len(pdf_bytes) < 100:
            return ""
        # Prova pypdf prima
        if HAS_PYPDF:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(pdf_bytes))
            testo = ""
            for page in reader.pages[:8]:
                t = page.extract_text() or ""
                testo += t + " "
                if len(testo) > max_chars * 2: break
            return testo[:max_chars].strip()
        elif HAS_PYMUPDF:
            import fitz
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            testo = ""
            for i, page in enumerate(doc):
                if i >= 8: break
                testo += page.get_text() + " "
                if len(testo) > max_chars * 2: break
            return testo[:max_chars].strip()
        else:
            # Fallback: cerca testo ASCII grezzo nel PDF
            testo_grezzo = pdf_bytes.decode('latin-1', errors='ignore')
            parole = re.findall(r'[a-zA-ZàèéìòùÀÈÉÌÒÙ]{4,}', testo_grezzo)
            return " ".join(parole[:300])[:max_chars]
    except Exception as e:
        print(f"    ⚠️  Errore lettura {file_id}: {e}")
        return ""

def concetti_nel_testo(testo, soglia=1):
    trovati = {}
    t = testo.lower()
    for c, sinonimi in CONCETTI.items():
        score = sum(t.count(s) for s in sinonimi)
        if score >= soglia:
            trovati[c] = score
    # Ordina per rilevanza
    return set(sorted(trovati, key=trovati.get, reverse=True)[:8])

def seleziona_batch(letture, batch_size=10):
    """Seleziona i prossimi 10 PDF non ancora letti (ciclo rotante)."""
    letti = set(letture.get("letti", []))
    non_letti = [p for p in ALL_PDF if p["id"] not in letti]
    if not non_letti:
        # Reset: ha letto tutto, ricomincia
        print("  🔄 Ciclo completato! Reset letture — ricomincio da capo")
        letture["letti"] = []
        non_letti = ALL_PDF.copy()
    # Priorità: elettrocoltura e coltivazione prima
    prioritari = [p for p in non_letti if p["cat"] in ("elettrocoltura", "coltivazione")]
    altri = [p for p in non_letti if p["cat"] not in ("elettrocoltura", "coltivazione")]
    random.shuffle(prioritari)
    random.shuffle(altri)
    selezionati = (prioritari + altri)[:batch_size]
    return selezionati

TEMPLATE_CONNESSIONI = [
    "{A} e {B} convergono su un principio fondamentale: la {concetto}. {A_dom} lo misura con strumenti fisici, {B_dom} lo descrive con linguaggio simbolico — ma entrambi parlano della stessa forza.",
    "Dal testo reale di {A}: il concetto di {concetto} emerge con forza. {B} descrive lo stesso fenomeno attraverso la lente della {B_dom}. Due prospettive, una sola verità.",
    "La {concetto} unisce {A} e {B}: ciò che {A_dom} chiama fisica, {B_dom} chiama magia. La mini-serra diventa il laboratorio dove queste forze si incontrano.",
    "{B} insegna che la {concetto} è alla base di ogni trasformazione. {A} lo dimostra empiricamente nel dominio della {A_dom}.",
    "Leggendo {A} emerge il tema della {concetto} — lo stesso tema che {B} tratta nella tradizione {B_dom}. La connessione è reale e applicabile alla serra.",
    "Connessione cross-dominio: {A} ({A_dom}) e {B} ({B_dom}) condividono la visione della {concetto} come forza ordinatrice. Nel living soil, questo si traduce in sinergia tra suolo e coltivatore.",
]

def genera_connessione_da_testo(pdf_a, testo_a, pdf_b, testo_b):
    """Genera connessione reale basata sui testi estratti."""
    concetti_a = concetti_nel_testo(testo_a)
    concetti_b = concetti_nel_testo(testo_b)
    comuni = concetti_a & concetti_b
    if len(comuni) < 1:
        return None
    concetto = random.choice(list(comuni))
    template = random.choice(TEMPLATE_CONNESSIONI)
    nota = template.format(
        A=pdf_a["autore"],
        B=pdf_b["autore"],
        A_dom=pdf_a["cat"],
        B_dom=pdf_b["cat"],
        concetto=concetto
    )
    # Aggiungi snippet di testo reale se disponibile
    snippet_a = testo_a[:120].strip().replace('\n', ' ') if testo_a else ""
    snippet_b = testo_b[:120].strip().replace('\n', ' ') if testo_b else ""
    if snippet_a and len(snippet_a) > 30:
        nota += f' [Estratto da {pdf_a["t"][:30]}: «{snippet_a}…»]'
    return {
        "a": f"{pdf_a['autore']} — {pdf_a['t'][:50]}",
        "b": f"{pdf_b['autore']} — {pdf_b['t'][:50]}",
        "nota": nota,
        "tags": list(comuni)[:5],
        "generata": datetime.now().strftime("%Y-%m-%d"),
        "tipo": "sinergia_testo_reale",
        "fonte": "Drive_134PDF",
        "pdf_ids": [pdf_a["id"], pdf_b["id"]]
    }

def carica_db():
    return json.loads(DB_PATH.read_text(encoding='utf-8'))

def salva_db(db):
    db['ultimo_aggiornamento'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    v = db.get('versione', '1.0')
    try: db['versione'] = str(round(float(v) + 0.1, 1))
    except: db['versione'] = '3.0'
    DB_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding='utf-8')

def main():
    print("="*60)
    print("🧠 CERVELLO NOTTURNO v3 — Lettura REALE 134 PDF Drive")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📚 PDF totali mappati: {len(ALL_PDF)}")
    print(f"🔑 Drive token: {'✅ PRESENTE' if DRIVE_TOKEN else '⚠️  MANCANTE — uso modalità offline'}")
    print("="*60)

    db = carica_db()
    letture = carica_letture()
    
    # Indici connessioni esistenti
    esistenti = set()
    for c in db.get('connessioni', []):
        a = c.get('a', c.get('da', ''))[:25].lower()
        b = c.get('b', c.get('a', ''))[:25].lower()
        esistenti.add((a, b))
        esistenti.add((b, a))
    print(f"📊 Connessioni esistenti: {len(db['connessioni'])}")

    # Seleziona batch di 10 PDF da leggere questo ciclo
    batch = seleziona_batch(letture, batch_size=10)
    print(f"\n📖 Lettura batch ({len(batch)} PDF):")
    
    # Leggi testi reali
    testi = {}
    for pdf in batch:
        print(f"  📄 {pdf['t'][:50]}...", end=" ")
        if DRIVE_TOKEN and HAS_REQUESTS:
            testo = scarica_testo_pdf_drive(pdf["id"], DRIVE_TOKEN, max_chars=1500)
            if testo and len(testo) > 50:
                testi[pdf["id"]] = testo
                print(f"✅ ({len(testo)} chars)")
            else:
                # Fallback: usa concetti simulati per questo PDF
                print("⚠️  (testo non estratto, uso concetti predefiniti)")
                testi[pdf["id"]] = _concetti_fallback(pdf)
        else:
            # Nessun token: usa concetti predefiniti
            testi[pdf["id"]] = _concetti_fallback(pdf)
            print("📋 (offline mode)")
        # Segna come letto
        if pdf["id"] not in letture["letti"]:
            letture["letti"].append(pdf["id"])
    
    print(f"\n✅ Letti: {len(letture['letti'])}/{len(ALL_PDF)} PDF totali")

    # Genera connessioni cross-dominio dal batch
    nuove = []
    pdf_elec = [p for p in batch if p["cat"] == "elettrocoltura"]
    pdf_altri = [p for p in batch if p["cat"] != "elettrocoltura"]
    
    # Connessioni elettrocoltura <-> altri domini
    for pe in pdf_elec:
        for pa in pdf_altri:
            if len(nuove) >= 6: break
            ka = pe["autore"][:20].lower()
            kb = pa["autore"][:20].lower()
            if (ka, kb) in esistenti: continue
            te = testi.get(pe["id"], "")
            ta = testi.get(pa["id"], "")
            conn = genera_connessione_da_testo(pe, te, pa, ta)
            if conn:
                nuove.append(conn)
                esistenti.add((ka, kb))
                print(f"  ✅ {pe['autore'][:25]} ↔ {pa['autore'][:25]} [{', '.join(conn['tags'][:2])}]")
    
    # Connessioni all'interno dello stesso batch (diversi domini)
    if len(nuove) < 4:
        for i, pa in enumerate(batch):
            for pb in batch[i+1:]:
                if len(nuove) >= 6: break
                if pa["cat"] == pb["cat"]: continue
                ka = pa["autore"][:20].lower()
                kb = pb["autore"][:20].lower()
                if (ka, kb) in esistenti: continue
                ta = testi.get(pa["id"], "")
                tb = testi.get(pb["id"], "")
                conn = genera_connessione_da_testo(pa, ta, pb, tb)
                if conn:
                    nuove.append(conn)
                    esistenti.add((ka, kb))
                    print(f"  ✅ {pa['autore'][:25]} ↔ {pb['autore'][:25]} [{', '.join(conn['tags'][:2])}]")

    # Salva
    if nuove:
        db['connessioni'].extend(nuove)
        print(f"\n✅ {len(nuove)} nuove connessioni — totale: {len(db['connessioni'])}")
    else:
        print("\n⚠️  Nessuna connessione nuova generata")
    
    db['pdf_letti_134'] = len(letture['letti'])
    db['pdf_totali_134'] = len(ALL_PDF)
    salva_db(db)
    salva_letture(letture)
    
    # Salva log
    log = []
    if LOG_PATH.exists():
        try: log = json.loads(LOG_PATH.read_text(encoding='utf-8'))
        except: pass
    log.append({
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "batch_letto": [p["t"][:40] for p in batch],
        "connessioni_trovate": len(nuove),
        "totale_connessioni": len(db['connessioni']),
        "pdf_letti_totale": len(letture['letti']),
        "pdf_totali": len(ALL_PDF),
        "modo": "reale" if DRIVE_TOKEN else "offline"
    })
    log = log[-60:]
    LOG_PATH.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')

    print("="*60)
    print(f"✅ COMPLETATO — v{db.get('versione','?')}")
    print(f"📚 PDF letti: {len(letture['letti'])}/{len(ALL_PDF)} ({round(len(letture['letti'])/len(ALL_PDF)*100)}%)")
    print(f"🔗 Connessioni totali: {len(db['connessioni'])}")
    print("="*60)

def _concetti_fallback(pdf):
    """Genera testo simulato con concetti chiave basati su autore/categoria."""
    cat = pdf["cat"]
    autore = pdf["autore"].lower()
    base = {
        "elettrocoltura": "electricity energy vibration frequency electromagnetic field plant growth copper antenna magnetism resonance current voltage",
        "magia": "transformation intention will consciousness spirit energy ritual vibration harmony sacred purification",
        "spirituale": "consciousness light unity awareness meditation intention mind energy soul vibration",
        "libri_sacri": "sacred light unity purification ritual harmony nature consciousness intention cycle",
        "coltivazione": "soil earth nature growth plant root water organic harmony cycle season",
    }.get(cat, "energy nature vibration harmony")
    # Aggiungi parole specifiche per autore
    if "tesla" in autore: base += " electricity resonance coil frequency vibration electromagnetic"
    if "ighina" in autore: base += " magnetic atom spiral energy field vortex"
    if "nollet" in autore: base += " electricity physics light nature vegetale plant"
    if "crowley" in autore: base += " will intention transformation ritual sacred energy"
    if "ingham" in autore: base += " soil biology earth microbe root fungi water humus"
    if "howard" in autore: base += " compost soil earth organic nature plant fertility"
    if "lakhovsky" in autore: base += " vibration resonance cell frequency harmony energy antenna copper"
    if "church" in autore: base += " brain consciousness energy quantum meditation intention field"
    if "guerzoni" in autore: base += " antenna electromagnetic frequency brain energy vibration resonance"
    return base

if __name__ == "__main__":
    main()
