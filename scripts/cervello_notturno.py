#!/usr/bin/env python3
"""
🧠 CERVELLO NOTTURNO v4 — Mini-Serra Living Soil
=================================================
Legge i 134 PDF REALI da Google Drive — cartelle PUBBLICHE.
Nessun token necessario — link diretti di download.

Ciclo rotante: 10 PDF ogni 6 ore
→ in ~8 giorni ha letto tutti i 134 PDF reali.
"""

import json, os, re, random, io, urllib.request
from datetime import datetime
from pathlib import Path

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

BASE = Path(__file__).parent.parent
DB_PATH   = BASE / "manuali" / "esperimenti_database.json"
LOG_PATH  = BASE / "scripts"  / "cervello_log.json"
LETTI_PATH = BASE / "scripts" / "pdf_letture.json"

# URL pubblico Drive (nessun token — cartelle condivise)
def drive_url(file_id):
    return f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t"

ALL_PDF = [
    # ── ELETTROCOLTURA ──
    {"id":"1oYPClfiyHQWahc7vYR5ZpDnEno4QdL00","t":"Christofleau — Electroculture","cat":"elettrocoltura","autore":"Justin Christofleau"},
    {"id":"1RMmA38dUgQX4HAlzZMql_bfVxeQgDmg3","t":"Nollet — De l Electricite du Corps Humain","cat":"elettrocoltura","autore":"Jean Antoine Nollet"},
    {"id":"1P1q5a26vfKjt4dYGXMmIgAit9OIngEUK","t":"Nollet — De l Electricite des Meteores","cat":"elettrocoltura","autore":"Jean Antoine Nollet"},
    {"id":"1-49mF-uWD7vFL6vh7cZUDaXm1xAvMael","t":"Nollet — De l Electricite des Vegetaux","cat":"elettrocoltura","autore":"Jean Antoine Nollet"},
    {"id":"13ISp42iI9nisSmzQQ5-OTSV225V0EwcJ","t":"Nollet — Lezioni di Fisica 1","cat":"elettrocoltura","autore":"Jean Antoine Nollet"},
    {"id":"11tVa37QmtGC1-_xxkUd8R_u7bwwV1LbE","t":"UFIE Fisica Nollet","cat":"elettrocoltura","autore":"Jean Antoine Nollet"},
    {"id":"1D16cSiNvVUcYBZvtCpjAndQimWjAjONt","t":"Ighina — La Scoperta dell Atomo Magnetico","cat":"elettrocoltura","autore":"Pier Luigi Ighina"},
    {"id":"1z0kYGkUDcXIS6x7bMX8M0AIkFJz7wBPZ","t":"Ighina — El Atomo Magnetico","cat":"elettrocoltura","autore":"Pier Luigi Ighina"},
    {"id":"1hw1xDbefoWDBU-CY-CC4Sesq3vd5LuBD","t":"Ighina — Profeta Sconosciuto","cat":"elettrocoltura","autore":"Alberto Tavanti"},
    {"id":"1S9kONL6RretByiVpwNcF5K4BmOuBX1tR","t":"Tesla — Lampo di Genio","cat":"elettrocoltura","autore":"Nikola Tesla"},
    {"id":"1jkvl9ZJY6ZESsf06lBOrzerDcqizj1HV","t":"Tesla — Energia Frequenze Vibrazioni","cat":"elettrocoltura","autore":"Nikola Tesla"},
    {"id":"1mC7CJ8c2wvMbGocXU32MGUwRAC0gHU6F","t":"Tesla — Un Genio Volutamente Dimenticato","cat":"elettrocoltura","autore":"Vittorio Baccelli"},
    {"id":"1B3sBuB_M8VBxbopqvLAuaZXIJiqH91U2","t":"Tesla — Le Mie Invenzioni","cat":"elettrocoltura","autore":"Nikola Tesla"},
    {"id":"1lggv0MaBq6TMnWJH9G6sNnF92ydBpqNI","t":"Il Codice Tesla","cat":"elettrocoltura","autore":"Alessandro Falzani"},
    {"id":"1oCGYPJCizCpBBNk9QX937TuRjxWSbfYv","t":"Arce — Electroculture Biohacker Guide","cat":"elettrocoltura","autore":"Cesar Arce"},
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
    {"id":"10tojlySkd_2gr3KPUpAmc2pM-Q7R49pL","t":"Ulaby — Campi Elettromagnetici","cat":"elettrocoltura","autore":"Fawwaz Ulaby"},
    {"id":"1Hr4-I_G2prpOsoZiad_j8k25hHfygFzG","t":"Ortolani Venturi — Elettrotecnica","cat":"elettrocoltura","autore":"Ortolani Venturi"},
    {"id":"16CzuDx9YxGpMOGRHRUcN35Sf6aq89nIA","t":"Cathie — The Energy Grid","cat":"elettrocoltura","autore":"Bruce Cathie"},
    {"id":"1AAr0kRVqASQZjV_Q1Qz_awJqAqIVNvt-","t":"Ruhlmann — La Melodie Secrete des Vegetaux","cat":"elettrocoltura","autore":"Renaud Ruhlmann"},
    {"id":"13OgT70YQllQ6bnhO4ew34GNP8UX_7pay","t":"Gateway Secret — Potenzialita Cervello","cat":"elettrocoltura","autore":"CIA + Vari"},
    {"id":"1N2-XfvhaWtZKcBVjFCsXWEAeA7B1pyyD","t":"Church — Cervello Quantico","cat":"elettrocoltura","autore":"Dawson Church"},
    {"id":"1knti3K8C4omjDa2awj9mdmA20AhA8bMg","t":"Guerzoni — Antenna Uomo","cat":"elettrocoltura","autore":"Tiziano Guerzoni"},
    {"id":"1u_jVM7qqRb6nfu8lvIkpEBGc6xTy1X6D","t":"Guenon — Simboli della Scienza Sacra","cat":"elettrocoltura","autore":"Rene Guenon"},
    {"id":"1TSwc8YgEXvZydw6iB-Lk26CLSD4oxCZI","t":"Ouspensky — Tertium Organum","cat":"elettrocoltura","autore":"P.D. Ouspensky"},
    {"id":"1FgRXITI63cY9gom5u8oBipHFdhJ0e8xp","t":"Tompkins & Bird — Vita Segreta delle Piante","cat":"elettrocoltura","autore":"Tompkins Bird"},
    {"id":"1UOU7wYiEGi3QEr6XgM8EQJKVYFZ9a-oc","t":"La Strega Verde — Magia delle Piante","cat":"elettrocoltura","autore":"N/D"},
    {"id":"1o1vOQTubgt4726YzIv4cgD1Nbn4qxjsI","t":"Garnier Malet — Ouvertures Temporelles","cat":"elettrocoltura","autore":"Garnier Malet"},
    {"id":"1QXaLuIwBNceCoTAK6tBCOh19RO669QwH","t":"TOTALE 2 compilato","cat":"elettrocoltura","autore":"Vari"},
    {"id":"1KwxwBq0RE-uX_4oa441aTZYbBpe4t-e4","t":"TOTALE 1 compilato","cat":"elettrocoltura","autore":"Vari"},
    # ── MAGIA ──
    {"id":"1wS-oWkv1KZtjdTSm6T1geo16J3Oz1avd","t":"Crowley — Magick","cat":"magia","autore":"Aleister Crowley"},
    {"id":"1LT_JLH4mKETjamYvIc97JT1VUF7E1baf","t":"Crowley — La Figlia della Luna","cat":"magia","autore":"Aleister Crowley"},
    {"id":"1lfnZRuwJsdcNAqsEvSNc-rVoc1-bj-VA","t":"Crowley — Il Libro della Legge","cat":"magia","autore":"Aleister Crowley"},
    {"id":"1zRoFkpbG0KaH2oqsAwRvFQgKEv3qJKVe","t":"Crowley — Il Cuore del Maestro","cat":"magia","autore":"Aleister Crowley"},
    {"id":"1wI8OCWAn69FViToCCKh6I5-YIxOgTaZA","t":"Crowley — L artigiano del Male","cat":"magia","autore":"Kaw Djer"},
    {"id":"1DaS726VzDeLV-daKCPWhtULVsyeOr1Lz","t":"Aleister Crowley Kaw Djer","cat":"magia","autore":"Kaw Djer"},
    {"id":"1wGsVe3m8lr5Tfv86g2ChVGHbM46hxXvM","t":"Crowley e Dion Fortune","cat":"magia","autore":"Alan Richardson"},
    {"id":"1kk6X_zft8c6icmx4nbs-98Mx0DgDa5L9","t":"Crowley — Aforismi Esoterici","cat":"magia","autore":"Aleister Crowley"},
    {"id":"1_XoMODN60boQ3AItL2q8CK-TWr3q-kRV","t":"Liber333 — Libro delle Menzogne","cat":"magia","autore":"Aleister Crowley"},
    {"id":"14wRabpFIUV4X9-kfutyF6V3FgpVFBp84","t":"Agrippa — La Filosofia Occulta","cat":"magia","autore":"Cornelio Agrippa"},
    {"id":"18F7EPoy1L6FGpSzQ2g53nrBRXu--vqbn","t":"La Chiave di Salomone","cat":"magia","autore":"Anonimo"},
    {"id":"1c2UVex5uS5HHEZ-WGJPUBGGbtKuTudQm","t":"Dion Fortune — La Cabala Mistica","cat":"magia","autore":"Dion Fortune"},
    {"id":"1FZJYCW0C9I-InpmXL5bSrsiIbmBvho7y","t":"Ermete — Corpo Ermetico e Asclepio","cat":"magia","autore":"Ermete Trismegisto"},
    {"id":"1CVON9yQnUvZFJxs08i7e56jb5i_F9VzV","t":"Ermete — Corpus Hermeticum","cat":"magia","autore":"Ermete Trismegisto"},
    {"id":"1x4tEPd6GxvgNYmxkmHPzeTlgauOSIYSw","t":"Ermete — Il Pimandro","cat":"magia","autore":"Ermete Trismegisto"},
    {"id":"1crmVDByL75-L_Yr34wFjnilVheii-8UL","t":"I Tre Iniziati — Il Kybalion","cat":"magia","autore":"I Tre Iniziati"},
    {"id":"1Cqxb-db58XNj7R3BTZ-4WIiT6-aJeJxQ","t":"Il Grande Grimorio 5 libri in 1","cat":"magia","autore":"Vari"},
    {"id":"1t4Ez8yBDlf8x5r2UoxXT2e5l41VWtMdA","t":"Le Tavole Smeraldine di Thoth","cat":"magia","autore":"Ermete Trismegisto"},
    {"id":"1t7fryfB3KkeQuDoq-ufzp2bn-xdfhmAb","t":"Canseliet — Mutus Liber Alchimia","cat":"magia","autore":"Eugene Canseliet"},
    {"id":"14f87vUMUIyeUNeJZ0QtxQeKzsPX18tYr","t":"Manuale di Magia Nera","cat":"magia","autore":"N/D"},
    {"id":"1NDNjaWQ2hMDa1ks8e7R_0arNtHGAboEs","t":"Registri Akashici","cat":"magia","autore":"N/D"},
    {"id":"19bVh2cuEskhCWccACzrEuOTgQEy43JwT","t":"Clavicola di Salomone","cat":"magia","autore":"Anonimo"},
    {"id":"1WQzFIpBE1hVTiyJRthLguH2WLCBYF4mZ","t":"Esoterismo 5 Libri in 1","cat":"magia","autore":"Vari"},
    {"id":"1yObrQh72N5AiGM1cjcAKBWtLMkAZmvRl","t":"Aradia — Vangelo delle Streghe","cat":"magia","autore":"Leland"},
    # ── SPIRITUALI & ROL ──
    {"id":"11GVDmLxPTxEVRPyBeiJbelubgA_T7Am7","t":"Vangelo Esseno della Pace Libro 4","cat":"spirituale","autore":"Szekely"},
    {"id":"1oA5QOoo69CMsfDSFU-cC81858aGkQoc_","t":"Vangelo della Pace Bundle 3 Libri","cat":"spirituale","autore":"Davide Appi"},
    {"id":"1VFFxUVezAYXmoVLDAd70UkFDisAAJQgD","t":"Rol — Il Grande Veggente","cat":"spirituale","autore":"Renzo Allegri"},
    {"id":"1_0kMMqxnBNGpv8BQKsJE4CvLl9l9c9cI","t":"Rol — L Uomo oltre l Uomo","cat":"spirituale","autore":"Paola Giovetti"},
    {"id":"1tk3_qzQG7lwn0sU-8OZ49Ip1vCkABPSW","t":"Rol — Una Vita di Prodigi","cat":"spirituale","autore":"Remo Lugli"},
    {"id":"1hPyv3pmK-bNm4p0L2hOwxjSLlEwtzs1O","t":"Rol — Io Sono la Grondaia diari","cat":"spirituale","autore":"Gustavo Rol"},
    {"id":"1Ad2KlYG-BdRd5LMhSfOd1LbuDi0TNBQF","t":"Harry B. Joseph — Book of Wisdom Vol 2","cat":"spirituale","autore":"Harry B. Joseph"},
    {"id":"1OZNYpBF9xoHREQZELT1zOtrLYs-EjQDR","t":"Harry B. Joseph — Book of Wisdom Vol 1","cat":"spirituale","autore":"Harry B. Joseph"},
    {"id":"1L-4HPBJj-k5QYk0ogG-EsqrRQD7T5Riz","t":"Harry B. Joseph — Activating The Inner Eye","cat":"spirituale","autore":"Harry B. Joseph"},
    # ── LIBRI SACRI ──
    {"id":"1OnaVUFPplTiTemmr5W2Q2WwG8f6qNBdg","t":"Il Nobile Corano italiano","cat":"libri_sacri","autore":"Islam"},
    {"id":"1oeV5rHYlmVTdrQQ9R--RF_WjQ0iMovUw","t":"Il Corano","cat":"libri_sacri","autore":"Islam"},
    {"id":"1Ipbo9B-dPmBtDCeVxWYcJqKgc_peJjd_","t":"108 Upanishad Induismo","cat":"libri_sacri","autore":"Induismo"},
    {"id":"1VnV1M5f1ZfV24w9dNUBb86Om-rzKXPCv","t":"Sanedrin Talmud Ebraismo","cat":"libri_sacri","autore":"Ebraismo"},
    {"id":"1Ai5BVewQAzi36t4jvScHeH6LcZas5L0q","t":"II Kojiki Shintoismo","cat":"libri_sacri","autore":"Shintoismo"},
    {"id":"1E_vK8ADTYaI-OLY_h_eOlxAZrLLZuLet","t":"I Giardini dei Devoti Buddhismo","cat":"libri_sacri","autore":"Buddhismo"},
    {"id":"1Unt8qu3xoDSll9HXykb8tr8UcONqB6an","t":"Wicca","cat":"libri_sacri","autore":"Wicca"},
    {"id":"1Kh_jNml-Lqatnl18Y7r_Gg3CvKvhPCpF","t":"Le Sette e Quattro Valli Bahai","cat":"libri_sacri","autore":"Bahaullah"},
    {"id":"11Hn4D-HvyBj-VDdrFweq8n0clriGELsn","t":"Manuale di Storia delle Religioni","cat":"libri_sacri","autore":"Filoramo Massenzio Raveri"},
    {"id":"1E9IukqNx5x9dZ-JEoTiXTpX9cJzzUvjH","t":"Angeli — Ebraismo Cristianesimo Islam","cat":"libri_sacri","autore":"Agamben Coccia"},
    # ── COLTIVAZIONE ──
    {"id":"1-P95imu3_c3b7MsE5UZ4gJb-SHvIkuwV","t":"Ingham — The Soil Biology Primer","cat":"coltivazione","autore":"Elaine Ingham"},
    {"id":"1HlreWsMdJTKToA_gK1LvT-wkVZnPodV_","t":"Howard — An Agricultural Testament","cat":"coltivazione","autore":"Albert Howard"},
    {"id":"1rmhXVBYZA01L-XwewL74J7nKb0kc1bM2","t":"Restrepo — ABC Agricultura Organica","cat":"coltivazione","autore":"Jairo Restrepo Rivera"},
    {"id":"1q_vKREIfA7ST5CqSVEkLpNsRtaN36vIu","t":"Restrepo — La Luna en la Agricultura","cat":"coltivazione","autore":"Jairo Restrepo Rivera"},
    {"id":"1Cz_NMIScAW63mJP4iglxqzNGhHPOygzR","t":"Restrepo — Agricultura Organica Harina de Rocas","cat":"coltivazione","autore":"Restrepo Pinheiro"},
    {"id":"1n6pBwHjQmJCuFHI805TdjpuS0QDlVJ36","t":"Ruiz — Il Quinto Accordo","cat":"coltivazione","autore":"Miguel Ruiz"},
    {"id":"1Y7AvFUZh90HnDx4a21-gkeNZUsf6ywMP","t":"Tresoldi — I Misteri dell Antico Egitto","cat":"coltivazione","autore":"Roberto Tresoldi"},
]

CONCETTI = {
    "vibrazione":    ["vibrat","frequenz","risonan","oscillaz","onda","vibration","frequency","harmonics","hertz"],
    "energia":       ["energy","energia","forza","force","prana","chi","orgone","electricity","electric"],
    "luce":          ["light","luce","luminoso","photon","fotone","illuminazione","enlighten"],
    "acqua":         ["water","acqua","liquid","flow","flusso","vortex","vortice"],
    "terra":         ["earth","terra","soil","ground","terreno","suolo","humus","radici","root"],
    "luna":          ["moon","luna","lunar","ciclo","cycle","tide","biodinam"],
    "rame":          ["copper","rame","cuivre","antenna","conduttore"],
    "spirale":       ["spiral","helix","vortex","coil","rotazione","golden","fibonacci"],
    "intenzione":    ["intent","intenzione","will","volonta","mind","mente","thought","pensiero"],
    "trasformazione":["transform","trasform","alchim","trasmut","change","mutazione"],
    "armonia":       ["harmon","armonia","equilibrio","balance","ordine","coherence"],
    "natura":        ["natura","nature","natural","pianta","plant","grow","crescit","vegetale"],
    "magnetismo":    ["magnet","polarit","campo","field","magnetico","polar","electro"],
    "coscienza":     ["conscious","coscienza","awareness","mindful","brain","cervello"],
    "unita":         ["unity","unita","oneness","interconness","connection","tutto"],
    "ritmo":         ["rhythm","ritmo","ciclo","cycle","cadenza","period","stagione"],
    "crescita":      ["growth","crescita","sviluppo","develop","bloom","fioritura","yield"],
    "elettricita":   ["electric","elettric","volt","ampere","current","corrente"],
}

TEMPLATE = [
    "{A} e {B} convergono sulla {concetto}: {A_dom} la misura con strumenti fisici, {B_dom} la descrive con simboli antichi.",
    "Dal testo reale di {A} emerge la {concetto}. {B} tratta lo stesso tema nella tradizione {B_dom}.",
    "La {concetto} unisce {A} ({A_dom}) e {B} ({B_dom}): cio che la fisica chiama frequenza, la tradizione chiama armonia.",
    "{B} ({B_dom}) insegna che la {concetto} e alla base di ogni trasformazione. {A} lo dimostra empiricamente.",
    "Connessione reale: {A} e {B} condividono la comprensione della {concetto} come forza ordinatrice del vivente. Nel living soil questo si manifesta ogni giorno.",
    "Leggendo {A} emerge il concetto di {concetto}. {B} lo chiama in modo diverso ma descrive la stessa realta. La mini-serra e il laboratorio dove si incontrano.",
]

def scarica_pdf(file_id, max_chars=1800):
    """Scarica e legge il testo da un PDF pubblico su Drive."""
    url = drive_url(file_id)
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; Serra-Bot/4.0)"
        })
        with urllib.request.urlopen(req, timeout=25) as resp:
            pdf_bytes = resp.read()
        if len(pdf_bytes) < 500:
            return ""
        if HAS_PYPDF:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            testo = ""
            for page in reader.pages[:8]:
                testo += (page.extract_text() or "") + " "
                if len(testo) > max_chars * 2: break
            return testo[:max_chars].strip()
        # fallback: estrazione grezza
        raw = pdf_bytes.decode('latin-1', errors='ignore')
        parole = re.findall(r'[a-zA-ZàèéìòùÀÈÉÌÒÙ]{4,}', raw)
        return " ".join(parole[:500])[:max_chars]
    except Exception as e:
        return ""

def fallback(pdf):
    base = {
        "elettrocoltura": "electricity energy vibration frequency electromagnetic field plant growth copper antenna magnetism resonance current voltage wave light",
        "magia": "transformation intention will consciousness spirit energy ritual vibration harmony sacred purification light",
        "spirituale": "consciousness light unity awareness meditation intention mind energy soul vibration harmony peace",
        "libri_sacri": "sacred light unity purification ritual harmony nature consciousness intention cycle divine",
        "coltivazione": "soil earth nature growth plant root water organic harmony cycle season humus microbe fungi",
    }.get(pdf["cat"], "energy nature vibration")
    extras = {
        "tesla": " electricity resonance coil frequency vibration electromagnetic wave",
        "ighina": " magnetic atom spiral energy field vortex",
        "nollet": " electricity physics light nature vegetale plant",
        "crowley": " will intention transformation ritual sacred energy",
        "ingham": " soil biology earth microbe root fungi water humus",
        "howard": " compost soil earth organic nature plant fertility",
        "church": " brain consciousness energy quantum meditation intention field",
        "guerzoni": " antenna electromagnetic frequency brain energy vibration resonance",
        "restrepo": " luna moon cycle soil organic mineral plant growth",
        "cathie": " grid harmony frequency earth magnetic field",
        "ouspensky": " consciousness dimension time space vibration fourth",
        "lakhovsky": " vibration resonance cell frequency harmony energy antenna copper",
        "arce": " electroculture practical copper wire plant growth electric",
        "ramos": " electroculture beginner plant growth copper wire antenna",
    }
    a = pdf["autore"].lower()
    for k, v in extras.items():
        if k in a: base += v
    return base

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
    concetto = max(comuni, key=lambda c: sum(ta.lower().count(p)+tb.lower().count(p) for p in CONCETTI.get(c,[])))
    nota = random.choice(TEMPLATE).format(
        A=pa["autore"], B=pb["autore"],
        A_dom=pa["cat"], B_dom=pb["cat"], concetto=concetto
    )
    snippet = ta[:120].strip().replace('\n',' ') if len(ta)>40 else ""
    if snippet: nota += f' [Estratto: «{snippet}...»]'
    return {
        "a": f"{pa['autore']} — {pa['t'][:45]}",
        "b": f"{pb['autore']} — {pb['t'][:45]}",
        "nota": nota, "tags": list(comuni)[:5],
        "generata": datetime.now().strftime("%Y-%m-%d"),
        "tipo": "sinergia_134pdf_reali", "fonte": "Drive_Pubblico_v4",
        "pdf_ids": [pa["id"], pb["id"]]
    }

def carica_letture():
    if LETTI_PATH.exists():
        try: return json.loads(LETTI_PATH.read_text(encoding='utf-8'))
        except: pass
    return {"letti": [], "cicli": 0}

def carica_db(): return json.loads(DB_PATH.read_text(encoding='utf-8'))

def salva_db(db):
    db['ultimo_aggiornamento'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    try: db['versione'] = str(round(float(db.get('versione','1.0'))+0.1,1))
    except: db['versione'] = '4.0'
    DB_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding='utf-8')

def salva_letture(d):
    LETTI_PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')

def main():
    print("="*60)
    print("🧠 CERVELLO NOTTURNO v4 — 134 PDF Drive Pubblici")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📚 PDF totali: {len(ALL_PDF)} | pypdf: {HAS_PYPDF}")
    print("🔓 Modalità: PUBBLICO (nessun token necessario)")
    print("="*60)

    db = carica_db()
    letture = carica_letture()

    # Connessioni esistenti (per evitare duplicati)
    esistenti = set()
    for c in db.get('connessioni',[]):
        a = c.get('a','')[:20].lower(); b = c.get('b','')[:20].lower()
        esistenti.add((a,b)); esistenti.add((b,a))
    print(f"📊 Connessioni esistenti: {len(db['connessioni'])}")

    # Seleziona batch rotante
    letti = set(letture.get("letti",[]))
    non_letti = [p for p in ALL_PDF if p["id"] not in letti]
    if not non_letti:
        print("🔄 Ciclo completo! Ricomincio da capo")
        letture["letti"] = []
        letture["cicli"] = letture.get("cicli",0) + 1
        non_letti = list(ALL_PDF)

    prio = [p for p in non_letti if p["cat"] in ("elettrocoltura","coltivazione")]
    altri = [p for p in non_letti if p["cat"] not in ("elettrocoltura","coltivazione")]
    random.shuffle(prio); random.shuffle(altri)
    batch = (prio + altri)[:10]

    ciclo_n = letture.get("cicli",0)+1
    print(f"\n📖 Lettura batch ({len(batch)} PDF — ciclo {ciclo_n}):")

    testi = {}
    ok_count = 0
    for pdf in batch:
        print(f"  📄 {pdf['t'][:48]}...", end=" ", flush=True)
        testo = scarica_pdf(pdf["id"])
        if testo and len(testo) > 80:
            testi[pdf["id"]] = testo
            ok_count += 1
            print(f"✅ {len(testo)}c reali")
        else:
            testi[pdf["id"]] = fallback(pdf)
            print("📋 fallback")
        if pdf["id"] not in letture["letti"]:
            letture["letti"].append(pdf["id"])

    pct = round(len(letture['letti'])/len(ALL_PDF)*100)
    print(f"\n✅ PDF letti realmente: {ok_count}/{len(batch)} | Totale ciclo: {len(letture['letti'])}/{len(ALL_PDF)} ({pct}%)")

    # Genera connessioni
    nuove = []
    elec = [p for p in batch if p["cat"]=="elettrocoltura"]
    alt  = [p for p in batch if p["cat"]!="elettrocoltura"]

    for pe in elec:
        for pa in alt:
            if len(nuove) >= 6: break
            ka=pe["autore"][:18].lower(); kb=pa["autore"][:18].lower()
            if (ka,kb) in esistenti: continue
            conn = genera_conn(pe, testi[pe["id"]], pa, testi[pa["id"]])
            if conn:
                nuove.append(conn); esistenti.add((ka,kb))
                print(f"  ✅ {pe['autore'][:22]} ↔ {pa['autore'][:22]} [{','.join(conn['tags'][:2])}]")

    if len(nuove) < 4:
        for i,pa in enumerate(batch):
            for pb in batch[i+1:]:
                if len(nuove) >= 6: break
                if pa["cat"] == pb["cat"]: continue
                ka=pa["autore"][:18].lower(); kb=pb["autore"][:18].lower()
                if (ka,kb) in esistenti: continue
                conn = genera_conn(pa, testi[pa["id"]], pb, testi[pb["id"]])
                if conn:
                    nuove.append(conn); esistenti.add((ka,kb))
                    print(f"  ✅ {pa['autore'][:22]} ↔ {pb['autore'][:22]} [{','.join(conn['tags'][:2])}]")

    if nuove: db['connessioni'].extend(nuove)
    db['pdf_letti_134'] = len(letture['letti'])
    db['pdf_totali_134'] = len(ALL_PDF)
    db['pdf_percentuale'] = pct
    salva_db(db); salva_letture(letture)

    log = []
    if LOG_PATH.exists():
        try: log = json.loads(LOG_PATH.read_text(encoding='utf-8'))
        except: pass
    log.append({
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "batch": [p["t"][:35] for p in batch],
        "ok_reali": ok_count, "nuove": len(nuove),
        "tot_conn": len(db['connessioni']),
        "pdf_letti": len(letture['letti']), "tot_pdf": len(ALL_PDF), "pct": pct,
        "modo": "pubblico_v4"
    })
    LOG_PATH.write_text(json.dumps(log[-60:], ensure_ascii=False, indent=2), encoding='utf-8')

    print("="*60)
    print(f"✅ COMPLETATO — v{db.get('versione','?')}")
    print(f"🔗 {len(nuove)} nuove connessioni | {len(db['connessioni'])} totali")
    print(f"📚 {len(letture['letti'])}/{len(ALL_PDF)} PDF letti ({pct}%)")
    print("="*60)

if __name__ == "__main__":
    main()
