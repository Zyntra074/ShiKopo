-- Extensão do mock para integração: tempo virtual, entrada, serviços e consultas espaciais.
local clock=0
local pending, canceled={},{}
MockRoblox.AsyncErrors={}
MockRoblox.Counters={Raycasts=0,SpatialQueries=0,DescendantScans=0,FriendQueries=0,MouseEvents=0,NetworkCalls=0}
local function resumeThread(thread,...)
    local result=table.pack(coroutine.resume(thread,...))
    if not result[1] then table.insert(MockRoblox.AsyncErrors,tostring(result[2])); return end
    if coroutine.status(thread)~="dead" then
        pending[thread]=clock+math.max(tonumber(result[2]) or 1/60,1/60)
    end
end
task={}
function task.spawn(callback,...)
    local thread=coroutine.create(callback)
    resumeThread(thread,...)
    return thread
end
function task.wait(seconds)
    local start=clock
    coroutine.yield(math.max(seconds or 1/60,1/60))
    return clock-start
end
function task.delay(seconds,callback,...)
    local args=table.pack(...)
    local thread=coroutine.create(function() callback(table.unpack(args,1,args.n)) end)
    pending[thread]=clock+math.max(seconds,1/60)
    return thread
end
function task.defer(callback,...) return task.delay(0,callback,...) end
function task.cancel(thread) pending[thread]=nil; canceled[thread]=true end
_G.task=task
local originalOs=os
os={clock=function() return clock end,time=function() return 1792897200+math.floor(clock) end}
_G.os=os
_G.tick=function() return clock end
_G.time=function() return clock end
function MockRoblox.advance(seconds,rate)
    local step=1/(rate or 60)
    local frames=math.floor(seconds/step+0.5)
    for _=1,frames do
        clock=clock+step
        RunService:Step(step)
        local ready={}
        for thread,due in pairs(pending) do
            if due<=clock+0.000001 then pending[thread]=nil; table.insert(ready,thread) end
        end
        for _,thread in ipairs(ready) do if not canceled[thread] then resumeThread(thread,step) end end
    end
end
function MockRoblox.pendingCount() local count=0; for _ in pairs(pending) do count=count+1 end; return count end
MockRoblox.Teleports={}
MockRoblox.InputEvents={}
MockRoblox.Keys={}
local VirtualInputManager={}
function VirtualInputManager:SendMouseButtonEvent(x,y,button,down)
    MockRoblox.Counters.MouseEvents=MockRoblox.Counters.MouseEvents+1
    table.insert(MockRoblox.InputEvents,{Button=button,Down=down})
    local input={UserInputType=Enum.UserInputType["MouseButton"..(button+1)],KeyCode=Enum.KeyCode.Unknown,Position=Vector3.new(x,y,0)}
    if down then UserInputService.InputBegan:Fire(input,false) else UserInputService.InputEnded:Fire(input,false) end
end
function VirtualInputManager:SendKeyEvent(down,key)
    table.insert(MockRoblox.InputEvents,{Key=key.Name,Down=down})
    local input={UserInputType=Enum.UserInputType.Keyboard,KeyCode=key,Position=Vector3.new()}
    if down then UserInputService.InputBegan:Fire(input,false) else UserInputService.InputEnded:Fire(input,false) end
end
function VirtualInputManager:SendMouseMoveEvent() end
local TeleportService={}
function TeleportService:Teleport(place) table.insert(MockRoblox.Teleports,place) end
function TeleportService:TeleportToPlaceInstance(place,job) table.insert(MockRoblox.Teleports,{place,job}) end
local VirtualUser={}
function VirtualUser:CaptureController() end
function VirtualUser:ClickButton2() end
local oldService=game.GetService
function game:GetService(name)
    if name=="VirtualInputManager" then return VirtualInputManager end
    if name=="TeleportService" then return TeleportService end
    if name=="VirtualUser" then return VirtualUser end
    return oldService(self,name)
end
function UserInputService:IsKeyDown(key) return MockRoblox.Keys[key.Name]==true end
function UserInputService:IsMouseButtonPressed(key) return MockRoblox.Keys[key.Name]==true end
function MockRoblox.input(name,down,gpe)
    local mouse=name:match("^MouseButton")
    local input={KeyCode=mouse and Enum.KeyCode.Unknown or Enum.KeyCode[name],UserInputType=mouse and Enum.UserInputType[name] or Enum.UserInputType.Keyboard,Position=Vector3.new()}
    MockRoblox.Keys[name]=down
    if down then UserInputService.InputBegan:Fire(input,gpe or false) else UserInputService.InputEnded:Fire(input,gpe or false) end
end
OverlapParams={new=function() return {} end}
_G.OverlapParams=OverlapParams
MockRoblox.SpatialParts={}
function workspace:GetPartBoundsInRadius(center,radius,params)
    MockRoblox.Counters.SpatialQueries=MockRoblox.Counters.SpatialQueries+1
    local result={}
    for _,part in ipairs(MockRoblox.SpatialParts) do
        if part.Parent and (part.Position-center).Magnitude<=radius then
            table.insert(result,part)
            if #result>=(params.MaxParts or 100000) then break end
        end
    end
    return result
end
function workspace:Raycast(origin,direction,params)
    MockRoblox.Counters.Raycasts=MockRoblox.Counters.Raycasts+1
    return MockRoblox.RaycastHit
end
local oldDescendants=workspace.GetDescendants
function workspace:GetDescendants()
    MockRoblox.Counters.DescendantScans=MockRoblox.Counters.DescendantScans+1
    return oldDescendants(self)
end
local friend=Players.LocalPlayer.IsFriendsWith
function Players.LocalPlayer:IsFriendsWith(id)
    MockRoblox.Counters.FriendQueries=MockRoblox.Counters.FriendQueries+1
    return friend(self,id)
end
local oldTween=TweenService.Create
function TweenService:Create(instance,info,properties)
    local result=oldTween(self,instance,info,properties)
    function result:Play()
        self.PlaybackState=Enum.PlaybackState.Playing
        for key,value in pairs(properties) do instance[key]=value end
        task.delay(info.Time or 0.1,function()
            if self.PlaybackState==Enum.PlaybackState.Playing then self.PlaybackState=Enum.PlaybackState.Completed; self.Completed:Fire(Enum.PlaybackState.Completed) end
        end)
    end
    return result
end
Players.LocalPlayer.Character=MockRoblox.createMockCharacter("LocalPlayer",Vector3.new(0,3,0))
Players.LocalPlayer.Idled=MockRoblox.createSignal()
game.PlaceId,game.JobId=1,"offline"
local oldHttp=game.HttpGet
function game:HttpGet() MockRoblox.Counters.NetworkCalls=MockRoblox.Counters.NetworkCalls+1; error("Rede proibida nos testes de integração") end
_G.loadstring=loadstring
getgenv().task=task
_G.MockRoblox=MockRoblox

