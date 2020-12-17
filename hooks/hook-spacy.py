# HOOK FILE FOR SPACY
from PyInstaller.utils.hooks import collect_all

hiddenimports = [
    "cymem",
    "cymem.cymem",
    "srsly.msgpack.util",
    "preshed.maps",
    "thinc.linalg",
    "murmurhash",
]

# ----------------------------- SPACY -----------------------------
data = collect_all("spacy")

datas = data[0]
binaries = data[1]
hiddenimports += data[2]

data = collect_all("en_rpa_simple")
datas += data[0]
binaries += data[1]
hiddenimports += data[2]

data = collect_all("en_core_web_md")
datas += data[0]
binaries += data[1]
hiddenimports += data[2]


data = collect_all("xx_ent_wiki_sm")
datas += data[0]
binaries += data[1]
hiddenimports += data[2]

data = collect_all("en_rpa_simple_calendar")
datas += data[0]
binaries += data[1]
hiddenimports += data[2]

data = collect_all("en_rpa_simple_reminder")
datas += data[0]
binaries += data[1]
hiddenimports += data[2]

data = collect_all("en_rpa_simple_email")
datas += data[0]
binaries += data[1]
hiddenimports += data[2]

# ----------------------------- THINC -----------------------------
data = collect_all("thinc")

datas += data[0]
binaries += data[1]
hiddenimports += data[2]

# ----------------------------- CYMEM -----------------------------
data = collect_all("cymem")

datas += data[0]
binaries += data[1]
hiddenimports += data[2]

# ----------------------------- PRESHED -----------------------------
data = collect_all("preshed")

datas += data[0]
binaries += data[1]
hiddenimports += data[2]

# ----------------------------- BLIS -----------------------------

data = collect_all("blis")

datas += data[0]
binaries += data[1]
hiddenimports += data[2]
