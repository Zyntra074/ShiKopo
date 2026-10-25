"""Comparação reproduzível de trabalho no simulador; não mede FPS no Roblox."""
from pathlib import Path
import argparse,json,subprocess,tempfile
ROOT=Path(__file__).resolve().parent.parent

def run(source:Path,luau:str,scenario:str):
    mock=(ROOT/"tests/mock_roblox.lua").read_text(encoding="utf-8")
    shim=(ROOT/"tests/mock_scheduler.lua").read_text(encoding="utf-8")
    scene='getgenv().MinimapTerrain=true\n' if scenario=="mapa_vazio" else ""
    setup=""
    if scenario=="esp_20":
        setup='''for i=1,20 do MockRoblox.createMockPlayer("Player"..i,1000+i,nil,"Bright red",Vector3.new((i%5)-2,3,-30-i)) end
getgenv().RegisteredSockets["Ativar ESP (Box)"].set(true)
'''
    elif scenario=="mapa_vazio":
        setup='getgenv().RegisteredSockets["Ativar Minimapa"].set(true)\n'
    post=r'''
local nativeCallbacks=0
for _,signal in ipairs({RunService.RenderStepped,RunService.Heartbeat,RunService.Stepped}) do
 for _,connection in ipairs(signal._listeners) do
  local fn=connection._callback
  connection._callback=function(...) nativeCallbacks=nativeCallbacks+1; return fn(...) end
 end
end
MockRoblox.advance(10)
local activeConnections=#RunService.RenderStepped._listeners+#RunService.Heartbeat._listeners+#RunService.Stepped._listeners
local gui=CoreGui:FindFirstChild("DreeZyVoidware")
local snow=gui and gui:FindFirstChild("Main") and gui.Main:FindFirstChild("SnowContainer")
local stats={
 Seconds=10,FrameServiceCallbacks=nativeCallbacks,FrameServiceConnections=activeConnections,
 ActiveDrawings=#Drawing._activeObjects,PendingTasks=MockRoblox.pendingCount(),
 Snowflakes=snow and #snow:GetChildren() or 0,Raycasts=MockRoblox.Counters.Raycasts,
 FullMapScans=MockRoblox.Counters.DescendantScans,SpatialQueries=MockRoblox.Counters.SpatialQueries,
 NetworkCalls=MockRoblox.Counters.NetworkCalls,AsyncErrors=#MockRoblox.AsyncErrors,SignalErrors=#(MockRoblox.Errors or {}),
}
if runtime and runtime.Stats.ESP then stats.ESPUpdates=runtime.Stats.ESP.Calls end
print("BENCH:"..HttpService:JSONEncode(stats))
'''
    program='local _G=getfenv(0)\nmath.randomseed(12345)\n_G.warn=function() end\nlocal function createMock()\n'+mock+'\nend\nlocal MockRoblox=createMock()\n'+shim+'\n'+scene+'\nlocal function boot()\n'+source.read_text(encoding="utf-8")+'\nend\nlocal runtime=boot()\n'+setup+post
    with tempfile.TemporaryDirectory(prefix="dreezy-bench-") as folder:
        generated=Path(folder)/"bench.luau";generated.write_text(program,encoding="utf-8")
        result=subprocess.run([luau,str(generated)],capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=30)
    if result.returncode: raise RuntimeError(result.stderr+result.stdout[-2000:])
    line=next(line for line in result.stdout.splitlines() if line.startswith("BENCH:"))
    return json.loads(line[6:])

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before",type=Path,required=True)
    parser.add_argument("--after",type=Path,default=ROOT/"RespawnHUD.lua")
    parser.add_argument("--luau",required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    results={"note":"Contadores em simulação determinística de 10 s a 60 quadros/s. Não são medições de FPS ou tempo no cliente Roblox.","scenarios":{}}
    for scenario in ["ocioso","esp_20","mapa_vazio"]:
        results["scenarios"][scenario]={"before":run(args.before,args.luau,scenario),"after":run(args.after,args.luau,scenario)}
    args.output.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(results,ensure_ascii=False,indent=2))

if __name__=="__main__": main()

