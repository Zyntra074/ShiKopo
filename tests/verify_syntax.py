"""Valida os fontes originais com luau-compile, sem reescrever strings ou continue."""
from pathlib import Path
import os, shutil, subprocess, sys

REPO_ROOT=Path(__file__).resolve().parent.parent

def find_compiler():
    explicit=os.environ.get("LUAU_COMPILER")
    if explicit:
        return explicit if Path(explicit).is_file() else None
    binary=shutil.which("luau-compile")
    if binary:
        return binary
    interpreter=os.environ.get("LUAU_BIN")
    if interpreter:
        sibling=Path(interpreter).with_name("luau-compile.exe" if os.name=="nt" else "luau-compile")
        if sibling.is_file():
            return str(sibling)
    local=REPO_ROOT/".tools"/"luau"/("luau-compile.exe" if os.name=="nt" else "luau-compile")
    return str(local) if local.is_file() else None

def preprocess_luau(code: str) -> str:
    """Compatibilidade de API: o compilador Luau aceita o fonte intacto."""
    return code

def verify_file(file_path: Path) -> tuple[bool,str]:
    file_path=Path(file_path)
    try:
        content=file_path.read_text(encoding="utf-8")
    except (OSError,UnicodeError) as error:
        return False,f"Failed to read file: {error}"
    compiler=find_compiler()
    if not compiler:
        return False,"Luau compiler unavailable. Run tests/setup_luau.py or set LUAU_COMPILER."
    try:
        result=subprocess.run([compiler,"--null",str(file_path)],capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=30)
    except (OSError,subprocess.TimeoutExpired) as error:
        return False,f"Compiler error: {error}"
    if result.returncode:
        return False,"Syntax Error: "+(result.stderr or result.stdout).strip()
    return True,f"OK ({len(content.splitlines())} lines, native Luau)"

def scan_and_verify(target_paths=None) -> bool:
    if target_paths:
        files=[Path(p).resolve() for p in target_paths]
    else:
        files=[]
        for root,dirs,names in os.walk(REPO_ROOT):
            dirs[:]=[d for d in dirs if d not in {".git",".agents",".tools","__pycache__",".venv"}]
            files.extend(Path(root)/name for name in names if name.endswith((".lua",".luau")))
    files.sort()
    if not files:
        print("[ERROR] No Lua files found.")
        return False
    print(f"=== Native Luau syntax verification ({len(files)} files) ===")
    passed=0
    for file in files:
        ok,message=verify_file(file)
        label=file.relative_to(REPO_ROOT) if file.is_relative_to(REPO_ROOT) else file
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}: {message}")
        passed+=int(ok)
    print(f"Results: {passed} passed, {len(files)-passed} failed out of {len(files)} total files.")
    return passed==len(files)

if __name__=="__main__":
    raise SystemExit(0 if scan_and_verify(sys.argv[1:] or None) else 1)

