"""Executa sintaxe nativa, testes existentes, regressões e integração completa."""
from pathlib import Path
import argparse,ast,json,os,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parent.parent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=ROOT/".test-results")
    parser.add_argument("--luau",default=os.environ.get("LUAU_BIN") or shutil.which("luau"))
    args=parser.parse_args()
    binary=args.luau or str(ROOT/".tools"/"luau"/("luau.exe" if os.name=="nt" else "luau"))
    if not Path(binary).is_file():
        parser.error("Instale o Luau com tests/setup_luau.py ou informe --luau.")
    env=os.environ.copy()
    env.update(LUAU_BIN=binary,PYTHONDONTWRITEBYTECODE="1",PYTHONIOENCODING="utf-8")
    args.output.mkdir(parents=True,exist_ok=True)
    for file in ROOT.rglob("*.py"):
        if not any(part in {".tools",".venv","__pycache__"} for part in file.parts):
            ast.parse(file.read_text(encoding="utf-8"),filename=str(file))
    commands=[
        ("smoke",["tests/run_tests.py"]),
        ("challenger_m1",["tests/test_challenger_m1.py"]),
        ("challenger_probe",["tests/test_challenger_probe.py"]),
        ("challenger_deep",["tests/test_challenger_v2_deep.py"]),
        ("syntax_regressions",["-m","unittest","discover","-s","tests","-p","test_syntax_regressions.py","-v"]),
        ("integration",["tests/test_hub.py"]),
    ]
    results=[]
    for name,args_list in commands:
        start=time.monotonic()
        try:
            result=subprocess.run([sys.executable,"-B",*args_list],cwd=ROOT,env=env,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=90)
            text=result.stdout+"\n"+result.stderr
            code=result.returncode
        except subprocess.TimeoutExpired:
            code,text=124,"TIMEOUT"
        (args.output/(name+".log")).write_text(text,encoding="utf-8")
        results.append({"name":name,"exit_code":code,"seconds":round(time.monotonic()-start,3)})
        print(f"[{'PASS' if code==0 else 'FAIL'}] {name}",flush=True)
        if code:
            print(text[-5000:],flush=True)
    (args.output/"results.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    return 0 if all(result["exit_code"]==0 for result in results) else 1

if __name__=="__main__": raise SystemExit(main())

