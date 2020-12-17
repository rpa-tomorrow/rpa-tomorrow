# HOOK FILE FOR RPA
from PyInstaller.utils.hooks import collect_all

hiddenimports = [
    "lib",
    "lib.automate",
    "lib.automate.modules",
]
# ----------------------------- SPACY -----------------------------
data = collect_all("lib")

datas = data[0]
binaries = data[1]
hiddenimports += data[2]

data = collect_all("lib.modules")

datas = data[0]
binaries = data[1]
hiddenimports = data[2]
