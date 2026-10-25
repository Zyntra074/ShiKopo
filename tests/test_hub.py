"""Executa o hub completo em Luau nativo, com simulador determinístico e sem rede."""
from pathlib import Path
import argparse, os, shutil, subprocess, tempfile, sys

ROOT=Path(__file__).resolve().parent.parent

def generate(source: Path) -> str:
    mock=(ROOT/"tests/mock_roblox.lua").read_text(encoding="utf-8")
    scheduler=(ROOT/"tests/mock_scheduler.lua").read_text(encoding="utf-8")
    code=source.read_text(encoding="utf-8")
    cases=(ROOT/"tests/test_cases.lua").read_text(encoding="utf-8")
    return (
        'local _G=getfenv(0)\n_G.warn=function(...) end\n'
        'local function createMock()\n'+mock+'\nend\n'
        'local function extendMock()\n'+scheduler+'\nend\n'
        'local function boot()\n'+code+'\nend\n'
        'local function setup(options)\n'
        ' options=options or {}\n'
        ' local previous=getgenv and getgenv().ShiKopoRuntime\n'
        ' if previous then previous:Destroy() end\n'
        ' _G.MockRoblox=createMock()\n'
        ' extendMock()\n'
        ' if options.NoDrawing then _G.Drawing=nil end\n'
        ' if options.FailService then\n'
        '  MockRoblox.RestoreGetService=game.GetService\n'
        '  game.GetService=function(self,name) if name==options.FailService then error("Serviço indisponível") end; return MockRoblox.RestoreGetService(self,name) end\n'
        ' end\n'
        ' if options.BeforeBoot then options.BeforeBoot() end\n'
        ' return boot()\n'
        'end\n'+cases
    )

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,default=ROOT/"RespawnHUD.lua")
    parser.add_argument("--luau",default=os.environ.get("LUAU_BIN") or shutil.which("luau") or str(ROOT/".tools"/"luau"/("luau.exe" if os.name=="nt" else "luau")))
    parser.add_argument("--log",type=Path)
    args=parser.parse_args()
    if not args.luau: parser.error("Defina LUAU_BIN ou passe --luau com o interpretador Luau.")
    with tempfile.TemporaryDirectory(prefix="shikopo-tests-") as folder:
        generated=Path(folder)/"integration.luau"
        generated.write_text(generate(args.source),encoding="utf-8")
        result=subprocess.run([args.luau,str(generated)],capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=60)
    output=result.stdout+("\nSTDERR:\n"+result.stderr if result.stderr else "")
    if args.log: args.log.write_text(output,encoding="utf-8")
    print(output)
    return result.returncode

if __name__=="__main__":
    raise SystemExit(main())

