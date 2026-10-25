"""Instala o Luau 0.744 oficial para testes locais no Windows, com SHA-256 fixado."""
from pathlib import Path
import argparse,hashlib,io,sys,urllib.request,zipfile
VERSION="0.744"
URL=f"https://github.com/luau-lang/luau/releases/download/{VERSION}/luau-windows.zip"
SHA256="fde3e22c557aac6afe20a34e8050b7d8c290fa42638c04274a307ed5d0ef0db8"
FILES={"luau.exe","luau-compile.exe","luau-analyze.exe","luau-ast.exe"}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory",type=Path,default=Path(__file__).resolve().parent.parent/".tools"/"luau")
    args=parser.parse_args()
    if sys.platform!="win32": parser.error("Em outros sistemas, instale o Luau oficial e configure LUAU_BIN/LUAU_COMPILER.")
    payload=urllib.request.urlopen(URL,timeout=60).read()
    if hashlib.sha256(payload).hexdigest()!=SHA256: raise RuntimeError("SHA-256 diferente do pacote validado; download não será extraído.")
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        if set(archive.namelist())!=FILES: raise RuntimeError("Conteúdo inesperado no pacote do compilador.")
        args.directory.mkdir(parents=True,exist_ok=True)
        for name in sorted(FILES):
            (args.directory/name).write_bytes(archive.read(name))
    print(f"Luau {VERSION}: {args.directory.resolve()}")

if __name__=="__main__": main()

