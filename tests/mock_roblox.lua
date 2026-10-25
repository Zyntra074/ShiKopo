--[[
    tests/mock_roblox.lua
    Pure-Lua headless Roblox API & Executor Environment Mock
    Provides genuine state and simulation for testing ShiKopo modules offline.
]]

local _nativeLoad=load or loadstring
local MockRoblox = {}
local _genv = {}

-- Initialize _G and getgenv
_genv.getgenv = function()
    return _genv
end
_genv.getrenv = function()
    return _G
end
_genv.identifyexecutor = function()
    return "ShiKopoHeadlessMock", "1.0.0"
end

-- ============================================================================
-- Lua Compatibility & Global Helpers
-- ============================================================================
local _unpack = unpack or table.unpack
_genv.unpack = _unpack
_G.unpack = _unpack

local function typeof_impl(val)
    local t = type(val)
    if t == "table" then
        if val.ClassName then return "Instance" end
        if val.EnumType then return "EnumItem" end
        if val.X and val.Y and val.Z then return "Vector3" end
        if val.X and val.Y then return "Vector2" end
        if val.R and val.G and val.B then return "Color3" end
        if val.Scale and val.Offset then return "UDim" end
    end
    return t
end
_genv.typeof = typeof_impl
_G.typeof = typeof_impl

-- ============================================================================
-- Timing & Coroutine Helpers
-- ============================================================================
local _startTime = os.clock and os.clock() or os.time()
_genv.tick = function()
    return (os.clock and os.clock() or os.time())
end
_genv.time = function()
    return (os.clock and os.clock() or os.time()) - _startTime
end
_genv.wait = function(s)
    return s or 0.03, os.clock()
end

_genv.task = {
    wait = function(s) return s or 0.03 end,
    spawn = function(fn, ...)
        local args = { ... }
        return coroutine.wrap(function() fn(_unpack(args)) end)()
    end,
    defer = function(fn, ...)
        local args = { ... }
        return coroutine.wrap(function() fn(_unpack(args)) end)()
    end,
    delay = function(s, fn, ...)
        local args = { ... }
        return coroutine.wrap(function() fn(_unpack(args)) end)()
    end
}

-- ============================================================================
-- Virtual File System (VFS)
-- ============================================================================
local _vfsFiles = {}
local _vfsFolders = { [""] = true, ["/"] = true }

local function normalizePath(path)
    path = tostring(path):gsub("\\", "/")
    if path == "." or path == "./" then
        return ""
    end
    if path:sub(1, 2) == "./" then
        path = path:sub(3)
    end
    return path
end

local function registerFolders(path)
    local parts = {}
    for part in path:gmatch("[^/]+") do
        table.insert(parts, part)
        _vfsFolders[table.concat(parts, "/")] = true
    end
end

_genv.writefile = function(path, content)
    local p = normalizePath(path)
    _vfsFiles[p] = tostring(content)
    local parent = p:match("^(.-)/[^/]+$")
    if parent and parent ~= "" then
        _vfsFolders[parent] = true
        registerFolders(parent)
    end
    return true
end

_genv.readfile = function(path)
    local p = normalizePath(path)
    if _vfsFiles[p] ~= nil then
        return _vfsFiles[p]
    end
    error("VFS: File not found: " .. tostring(path), 2)
end

_genv.isfile = function(path)
    local p = normalizePath(path)
    return _vfsFiles[p] ~= nil
end

_genv.makefolder = function(path)
    local p = normalizePath(path)
    if p ~= "" then
        _vfsFolders[p] = true
        registerFolders(p)
    end
    return true
end

_genv.isfolder = function(path)
    local p = normalizePath(path)
    return _vfsFolders[p] == true
end

_genv.delfile = function(path)
    local p = normalizePath(path)
    _vfsFiles[p] = nil
end

_genv.listfiles = function(path)
    local p = normalizePath(path)
    if p ~= "" and p:sub(-1) ~= "/" then
        p = p .. "/"
    end
    local results = {}
    for fPath, _ in pairs(_vfsFiles) do
        if p == "" or fPath:sub(1, #p) == p then
            local rest = fPath:sub(#p + 1)
            if not rest:find("/") then
                table.insert(results, fPath)
            end
        end
    end
    return results
end

-- ============================================================================
-- Mouse APIs
-- ============================================================================
local _mousePos = { X = 960, Y = 540 }
local _mouseButtons = { [1] = false, [2] = false, [3] = false }

_genv.mousemoverel = function(dx, dy)
    _mousePos.X = _mousePos.X + (tonumber(dx) or 0)
    _mousePos.Y = _mousePos.Y + (tonumber(dy) or 0)
    if _genv.UserInputService and _genv.UserInputService.InputChanged then
        _genv.UserInputService.InputChanged:Fire({
            UserInputType = _genv.Enum.UserInputType.MouseMovement,
            Position = _genv.Vector3.new(_mousePos.X, _mousePos.Y, 0),
            Delta = _genv.Vector3.new(dx, dy, 0)
        })
    end
end

_genv.mouse1press = function()
    _mouseButtons[1] = true
    if _genv.UserInputService and _genv.UserInputService.InputBegan then
        _genv.UserInputService.InputBegan:Fire({
            UserInputType = _genv.Enum.UserInputType.MouseButton1,
            Position = _genv.Vector3.new(_mousePos.X, _mousePos.Y, 0)
        }, false)
    end
end

_genv.mouse1release = function()
    _mouseButtons[1] = false
    if _genv.UserInputService and _genv.UserInputService.InputEnded then
        _genv.UserInputService.InputEnded:Fire({
            UserInputType = _genv.Enum.UserInputType.MouseButton1,
            Position = _genv.Vector3.new(_mousePos.X, _mousePos.Y, 0)
        }, false)
    end
end

_genv.mouse1click = function()
    _genv.mouse1press()
    _genv.mouse1release()
end

_genv.mouse2press = function()
    _mouseButtons[2] = true
    if _genv.UserInputService and _genv.UserInputService.InputBegan then
        _genv.UserInputService.InputBegan:Fire({
            UserInputType = _genv.Enum.UserInputType.MouseButton2,
            Position = _genv.Vector3.new(_mousePos.X, _mousePos.Y, 0)
        }, false)
    end
end

_genv.mouse2release = function()
    _mouseButtons[2] = false
    if _genv.UserInputService and _genv.UserInputService.InputEnded then
        _genv.UserInputService.InputEnded:Fire({
            UserInputType = _genv.Enum.UserInputType.MouseButton2,
            Position = _genv.Vector3.new(_mousePos.X, _mousePos.Y, 0)
        }, false)
    end
end

_genv.mouse2click = function()
    _genv.mouse2press()
    _genv.mouse2release()
end

-- ============================================================================
-- Signals & Connections
-- ============================================================================
local function createSignal()
    local sig = { _listeners = {} }
    
    function sig:Connect(callback)
        assert(type(callback) == "function", "Signal:Connect argument must be a function")
        local conn = {
            Connected = true,
            _callback = callback
        }
        function conn:Disconnect()
            conn.Connected = false
            for i = #sig._listeners, 1, -1 do
                if sig._listeners[i] == conn then
                    table.remove(sig._listeners, i)
                    break
                end
            end
        end
        table.insert(sig._listeners, conn)
        return conn
    end
    
    sig.connect = sig.Connect
    
    function sig:Once(callback)
        local conn
        conn = sig:Connect(function(...)
            conn:Disconnect()
            callback(...)
        end)
        return conn
    end
    
    function sig:Fire(...)
        local listeners = {}
        for _, c in ipairs(sig._listeners) do
            if c.Connected then
                table.insert(listeners, c)
            end
        end
        for _, c in ipairs(listeners) do
            if c.Connected then
                local ok,err=pcall(c._callback,...)
                if not ok then
                    MockRoblox.Errors=MockRoblox.Errors or {}
                    table.insert(MockRoblox.Errors,tostring(err))
                end
            end
        end
    end
    
    function sig:Wait()
        return true
    end
    
    return sig
end

MockRoblox.createSignal = createSignal
_genv.createSignal = createSignal
_G.createSignal = createSignal

-- ============================================================================
-- Datatypes
-- ============================================================================

-- Vector2
local Vector2 = {}
Vector2.__index = function(t, k)
    if k == "Magnitude" then
        return math.sqrt(t.X * t.X + t.Y * t.Y)
    elseif k == "Unit" then
        local m = t.Magnitude
        if m == 0 then return Vector2.new(0, 0) end
        return Vector2.new(t.X / m, t.Y / m)
    end
    return Vector2[k]
end

function Vector2.new(x, y)
    local v = setmetatable({ X = tonumber(x) or 0, Y = tonumber(y) or 0 }, Vector2)
    return v
end

Vector2.zero = Vector2.new(0, 0)

function Vector2:Dot(other)
    return self.X * other.X + self.Y * other.Y
end

function Vector2:Cross(other)
    return self.X * other.Y - self.Y * other.X
end

function Vector2:Lerp(other, alpha)
    alpha = math.max(0, math.min(1, alpha))
    return Vector2.new(self.X + (other.X - self.X) * alpha, self.Y + (other.Y - self.Y) * alpha)
end

Vector2.__add = function(a, b) return Vector2.new(a.X + b.X, a.Y + b.Y) end
Vector2.__sub = function(a, b) return Vector2.new(a.X - b.X, a.Y - b.Y) end
Vector2.__mul = function(a, b)
    if type(a) == "number" then return Vector2.new(b.X * a, b.Y * a) end
    if type(b) == "number" then return Vector2.new(a.X * b, a.Y * b) end
    return Vector2.new(a.X * b.X, a.Y * b.Y)
end
Vector2.__div = function(a, b)
    if type(b) == "number" then return Vector2.new(a.X / b, a.Y / b) end
    return Vector2.new(a.X / b.X, a.Y / b.Y)
end
Vector2.__unm = function(a) return Vector2.new(-a.X, -a.Y) end
Vector2.__eq = function(a, b) return a.X == b.X and a.Y == b.Y end
Vector2.__tostring = function(a) return string.format("%g, %g", a.X, a.Y) end

_genv.Vector2 = Vector2

-- Vector3
local Vector3 = {}
Vector3.__index = function(t, k)
    if k == "Magnitude" then
        return math.sqrt(t.X * t.X + t.Y * t.Y + t.Z * t.Z)
    elseif k == "Unit" then
        local m = t.Magnitude
        if m == 0 then return Vector3.new(0, 0, 0) end
        return Vector3.new(t.X / m, t.Y / m, t.Z / m)
    end
    return Vector3[k]
end

function Vector3.new(x, y, z)
    return setmetatable({
        X = tonumber(x) or 0,
        Y = tonumber(y) or 0,
        Z = tonumber(z) or 0
    }, Vector3)
end

Vector3.zero = Vector3.new(0, 0, 0)
Vector3.one = Vector3.new(1, 1, 1)

function Vector3:Dot(other)
    return self.X * other.X + self.Y * other.Y + self.Z * other.Z
end

function Vector3:Cross(other)
    return Vector3.new(
        self.Y * other.Z - self.Z * other.Y,
        self.Z * other.X - self.X * other.Z,
        self.X * other.Y - self.Y * other.X
    )
end

function Vector3:Lerp(other, alpha)
    alpha = math.max(0, math.min(1, alpha))
    return Vector3.new(
        self.X + (other.X - self.X) * alpha,
        self.Y + (other.Y - self.Y) * alpha,
        self.Z + (other.Z - self.Z) * alpha
    )
end

Vector3.__add = function(a, b) return Vector3.new(a.X + b.X, a.Y + b.Y, a.Z + b.Z) end
Vector3.__sub = function(a, b) return Vector3.new(a.X - b.X, a.Y - b.Y, a.Z - b.Z) end
Vector3.__mul = function(a, b)
    if type(a) == "number" then return Vector3.new(b.X * a, b.Y * a, b.Z * a) end
    if type(b) == "number" then return Vector3.new(a.X * b, a.Y * b, a.Z * b) end
    return Vector3.new(a.X * b.X, a.Y * b.Y, a.Z * b.Z)
end
Vector3.__div = function(a, b)
    if type(b) == "number" then return Vector3.new(a.X / b, a.Y / b, a.Z / b) end
    return Vector3.new(a.X / b.X, a.Y / b.Y, a.Z / b.Z)
end
Vector3.__unm = function(a) return Vector3.new(-a.X, -a.Y, -a.Z) end
Vector3.__eq = function(a, b) return a.X == b.X and a.Y == b.Y and a.Z == b.Z end
Vector3.__tostring = function(a) return string.format("%g, %g, %g", a.X, a.Y, a.Z) end

_genv.Vector3 = Vector3

-- Color3
local Color3 = {}
Color3.__index = Color3

function Color3.new(r, g, b)
    return setmetatable({
        R = tonumber(r) or 0,
        G = tonumber(g) or 0,
        B = tonumber(b) or 0
    }, Color3)
end

function Color3.fromRGB(r, g, b)
    return Color3.new((tonumber(r) or 0) / 255, (tonumber(g) or 0) / 255, (tonumber(b) or 0) / 255)
end

function Color3.fromHex(hex)
    hex = tostring(hex):gsub("#", "")
    local r = tonumber(hex:sub(1, 2), 16) or 0
    local g = tonumber(hex:sub(3, 4), 16) or 0
    local b = tonumber(hex:sub(5, 6), 16) or 0
    return Color3.fromRGB(r, g, b)
end

function Color3.fromHSV(h, s, v)
    h = (h % 1) * 6
    local i = math.floor(h)
    local f = h - i
    local p = v * (1 - s)
    local q = v * (1 - f * s)
    local t = v * (1 - (1 - f) * s)
    local r, g, b
    if i == 0 then r, g, b = v, t, p
    elseif i == 1 then r, g, b = q, v, p
    elseif i == 2 then r, g, b = p, v, t
    elseif i == 3 then r, g, b = p, q, v
    elseif i == 4 then r, g, b = t, p, v
    else r, g, b = v, p, q
    end
    return Color3.new(r, g, b)
end

function Color3:Lerp(other, alpha)
    alpha = math.max(0, math.min(1, alpha))
    return Color3.new(
        self.R + (other.R - self.R) * alpha,
        self.G + (other.G - self.G) * alpha,
        self.B + (other.B - self.B) * alpha
    )
end

function Color3:ToHex()
    return string.format("%02X%02X%02X", math.floor(self.R * 255 + 0.5), math.floor(self.G * 255 + 0.5), math.floor(self.B * 255 + 0.5))
end

Color3.__eq = function(a, b)
    return math.abs(a.R - b.R) < 0.001 and math.abs(a.G - b.G) < 0.001 and math.abs(a.B - b.B) < 0.001
end
Color3.__tostring = function(a)
    return string.format("%g, %g, %g", a.R, a.G, a.B)
end

_genv.Color3 = Color3

-- CFrame
local CFrame = {}
CFrame.__index = function(t, k)
    if k == "Position" or k == "p" then
        return Vector3.new(t._x, t._y, t._z)
    elseif k == "X" then return t._x
    elseif k == "Y" then return t._y
    elseif k == "Z" then return t._z
    elseif k == "LookVector" then
        return Vector3.new(-t._m02, -t._m12, -t._m22)
    elseif k == "RightVector" then
        return Vector3.new(t._m00, t._m10, t._m20)
    elseif k == "UpVector" then
        return Vector3.new(t._m01, t._m11, t._m21)
    end
    return CFrame[k]
end

function CFrame.new(x, y, z, r00, r01, r02, r10, r11, r12, r20, r21, r22)
    local cf = setmetatable({}, CFrame)
    if type(x) == "table" and x.X and x.Y and x.Z then
        -- CFrame.new(posVector3) or CFrame.new(pos, lookAt)
        cf._x = x.X
        cf._y = x.Y
        cf._z = x.Z
        if type(y) == "table" and y.X and y.Y and y.Z then
            local diff = Vector3.new(y.X - x.X, y.Y - x.Y, y.Z - x.Z)
            local look = diff.Unit
            if look.Magnitude < 0.001 then look = Vector3.new(0, 0, -1) end
            local up = Vector3.new(0, 1, 0)
            local right = look:Cross(up).Unit
            if right.Magnitude < 0.001 then right = Vector3.new(1, 0, 0) end
            up = right:Cross(look).Unit
            cf._m00, cf._m10, cf._m20 = right.X, right.Y, right.Z
            cf._m01, cf._m11, cf._m21 = up.X, up.Y, up.Z
            cf._m02, cf._m12, cf._m22 = -look.X, -look.Y, -look.Z
        else
            cf._m00, cf._m10, cf._m20 = 1, 0, 0
            cf._m01, cf._m11, cf._m21 = 0, 1, 0
            cf._m02, cf._m12, cf._m22 = 0, 0, 1
        end
    else
        cf._x = tonumber(x) or 0
        cf._y = tonumber(y) or 0
        cf._z = tonumber(z) or 0
        if r00 ~= nil then
            cf._m00 = tonumber(r00) or 1
            cf._m01 = tonumber(r01) or 0
            cf._m02 = tonumber(r02) or 0
            cf._m10 = tonumber(r10) or 0
            cf._m11 = tonumber(r11) or 1
            cf._m12 = tonumber(r12) or 0
            cf._m20 = tonumber(r20) or 0
            cf._m21 = tonumber(r21) or 0
            cf._m22 = tonumber(r22) or 1
        else
            cf._m00, cf._m10, cf._m20 = 1, 0, 0
            cf._m01, cf._m11, cf._m21 = 0, 1, 0
            cf._m02, cf._m12, cf._m22 = 0, 0, 1
        end
    end
    return cf
end

function CFrame.Angles(rx, ry, rz)
    rx = rx or 0
    ry = ry or 0
    rz = rz or 0
    local cf = setmetatable({}, CFrame)
    cf._x, cf._y, cf._z = 0, 0, 0
    local cx, sx = math.cos(rx), math.sin(rx)
    local cy, sy = math.cos(ry), math.sin(ry)
    local cz, sz = math.cos(rz), math.sin(rz)
    
    cf._m00 = cy * cz
    cf._m01 = -cy * sz
    cf._m02 = sy
    
    cf._m10 = sx * sy * cz + cx * sz
    cf._m11 = -sx * sy * sz + cx * cz
    cf._m12 = -sx * cy
    
    cf._m20 = -cx * sy * cz + sx * sz
    cf._m21 = cx * sy * sz + sx * cz
    cf._m22 = cx * cy
    return cf
end

CFrame.fromEulerAnglesXYZ = CFrame.Angles
CFrame.fromOrientation = CFrame.Angles

function CFrame.lookAt(at, target)
    local cf = setmetatable({}, CFrame)
    cf._x = at.X or 0
    cf._y = at.Y or 0
    cf._z = at.Z or 0
    local diff = Vector3.new((target.X or 0) - cf._x, (target.Y or 0) - cf._y, (target.Z or 0) - cf._z)
    local look = diff.Unit
    if look.Magnitude < 0.001 then look = Vector3.new(0, 0, -1) end
    local up = Vector3.new(0, 1, 0)
    local right = look:Cross(up).Unit
    if right.Magnitude < 0.001 then right = Vector3.new(1, 0, 0) end
    up = right:Cross(look).Unit
    cf._m00, cf._m10, cf._m20 = right.X, right.Y, right.Z
    cf._m01, cf._m11, cf._m21 = up.X, up.Y, up.Z
    cf._m02, cf._m12, cf._m22 = -look.X, -look.Y, -look.Z
    return cf
end

function CFrame:GetComponents()
    return self._x, self._y, self._z,
           self._m00, self._m01, self._m02,
           self._m10, self._m11, self._m12,
           self._m20, self._m21, self._m22
end

function CFrame:VectorToObjectSpace(v)
    return Vector3.new(
        v.X * self._m00 + v.Y * self._m10 + v.Z * self._m20,
        v.X * self._m01 + v.Y * self._m11 + v.Z * self._m21,
        v.X * self._m02 + v.Y * self._m12 + v.Z * self._m22
    )
end

function CFrame:PointToObjectSpace(v)
    local rx = v.X - self._x
    local ry = v.Y - self._y
    local rz = v.Z - self._z
    return Vector3.new(
        rx * self._m00 + ry * self._m10 + rz * self._m20,
        rx * self._m01 + ry * self._m11 + rz * self._m21,
        rx * self._m02 + ry * self._m12 + rz * self._m22
    )
end

function CFrame:VectorToWorldSpace(v)
    return Vector3.new(
        v.X * self._m00 + v.Y * self._m01 + v.Z * self._m02,
        v.X * self._m10 + v.Y * self._m11 + v.Z * self._m12,
        v.X * self._m20 + v.Y * self._m21 + v.Z * self._m22
    )
end

function CFrame:PointToWorldSpace(v)
    return self.Position + self:VectorToWorldSpace(v)
end

function CFrame:Inverse()
    local cf = setmetatable({}, CFrame)
    cf._m00, cf._m01, cf._m02 = self._m00, self._m10, self._m20
    cf._m10, cf._m11, cf._m12 = self._m01, self._m11, self._m21
    cf._m20, cf._m21, cf._m22 = self._m02, self._m12, self._m22
    local invPos = cf:VectorToWorldSpace(Vector3.new(-self._x, -self._y, -self._z))
    cf._x, cf._y, cf._z = invPos.X, invPos.Y, invPos.Z
    return cf
end

CFrame.__add = function(cf, v3)
    return CFrame.new(cf._x + v3.X, cf._y + v3.Y, cf._z + v3.Z)
end

CFrame.__sub = function(cf, v3)
    return CFrame.new(cf._x - v3.X, cf._y - v3.Y, cf._z - v3.Z)
end

CFrame.__mul = function(a, b)
    if type(b) == "table" and b.Z and not b._m00 then
        -- CFrame * Vector3 -> transforms point
        return a:PointToWorldSpace(b)
    elseif type(b) == "table" and b._m00 then
        -- CFrame * CFrame
        local cf = setmetatable({}, CFrame)
        local pos = a:PointToWorldSpace(b.Position)
        cf._x, cf._y, cf._z = pos.X, pos.Y, pos.Z
        
        cf._m00 = a._m00 * b._m00 + a._m01 * b._m10 + a._m02 * b._m20
        cf._m01 = a._m00 * b._m01 + a._m01 * b._m11 + a._m02 * b._m21
        cf._m02 = a._m00 * b._m02 + a._m01 * b._m12 + a._m02 * b._m22
        
        cf._m10 = a._m10 * b._m00 + a._m11 * b._m10 + a._m12 * b._m20
        cf._m11 = a._m10 * b._m01 + a._m11 * b._m11 + a._m12 * b._m21
        cf._m12 = a._m10 * b._m02 + a._m11 * b._m12 + a._m12 * b._m22
        
        cf._m20 = a._m20 * b._m00 + a._m21 * b._m10 + a._m22 * b._m20
        cf._m21 = a._m20 * b._m01 + a._m21 * b._m11 + a._m22 * b._m21
        cf._m22 = a._m20 * b._m02 + a._m21 * b._m12 + a._m22 * b._m22
        return cf
    end
    error("Invalid operand for CFrame multiplication", 2)
end

CFrame.__tostring = function(cf)
    return string.format("%g, %g, %g, %g, %g, %g, %g, %g, %g, %g, %g, %g", cf:GetComponents())
end

_genv.CFrame = CFrame

-- UDim and UDim2
local UDim = {}
UDim.__index = UDim
function UDim.new(scale, offset)
    return setmetatable({ Scale = tonumber(scale) or 0, Offset = tonumber(offset) or 0 }, UDim)
end
UDim.__add = function(a, b) return UDim.new(a.Scale + b.Scale, a.Offset + b.Offset) end
UDim.__sub = function(a, b) return UDim.new(a.Scale - b.Scale, a.Offset - b.Offset) end
UDim.__eq = function(a, b) return a.Scale == b.Scale and a.Offset == b.Offset end
UDim.__tostring = function(a) return string.format("%g, %g", a.Scale, a.Offset) end
_genv.UDim = UDim

local UDim2 = {}
UDim2.__index = function(t, k)
    if k == "Width" then return t.X
    elseif k == "Height" then return t.Y
    end
    return UDim2[k]
end

function UDim2.new(sx, ox, sy, oy)
    return setmetatable({
        X = UDim.new(sx, ox),
        Y = UDim.new(sy, oy)
    }, UDim2)
end

function UDim2.fromOffset(x, y)
    return UDim2.new(0, x, 0, y)
end

function UDim2.fromScale(x, y)
    return UDim2.new(x, 0, y, 0)
end

UDim2.__add = function(a, b) return UDim2.new(a.X.Scale + b.X.Scale, a.X.Offset + b.X.Offset, a.Y.Scale + b.Y.Scale, a.Y.Offset + b.Y.Offset) end
UDim2.__sub = function(a, b) return UDim2.new(a.X.Scale - b.X.Scale, a.X.Offset - b.X.Offset, a.Y.Scale - b.Y.Scale, a.Y.Offset - b.Y.Offset) end
UDim2.__eq = function(a, b) return a.X == b.X and a.Y == b.Y end
UDim2.__tostring = function(a) return string.format("{%g, %g}, {%g, %g}", a.X.Scale, a.X.Offset, a.Y.Scale, a.Y.Offset) end
_genv.UDim2 = UDim2

-- BrickColor
local BrickColor = {}
BrickColor.__index = BrickColor
local _colorPalette = {
    ["White"] = Color3.fromRGB(242, 243, 243),
    ["Bright red"] = Color3.fromRGB(196, 40, 28),
    ["Bright blue"] = Color3.fromRGB(13, 105, 172),
    ["Bright green"] = Color3.fromRGB(75, 151, 75),
    ["Bright yellow"] = Color3.fromRGB(245, 205, 47),
    ["Medium stone grey"] = Color3.fromRGB(163, 162, 165),
    ["Really black"] = Color3.fromRGB(17, 17, 17)
}

function BrickColor.new(val)
    local name = "White"
    local c = _colorPalette["White"]
    if type(val) == "string" and _colorPalette[val] then
        name = val
        c = _colorPalette[val]
    elseif type(val) == "table" and val.R then
        name = "Custom"
        c = val
    end
    return setmetatable({ Name = name, Color = c }, BrickColor)
end

function BrickColor.random()
    return BrickColor.new("Bright blue")
end
function BrickColor.White() return BrickColor.new("White") end
function BrickColor.Red() return BrickColor.new("Bright red") end
function BrickColor.Blue() return BrickColor.new("Bright blue") end

BrickColor.__tostring = function(bc) return bc.Name end
_genv.BrickColor = BrickColor

-- TweenInfo
local TweenInfo = {}
TweenInfo.__index = TweenInfo
function TweenInfo.new(time, easingStyle, easingDirection, repeatCount, reverses, delayTime)
    return setmetatable({
        Time = time or 1,
        EasingStyle = easingStyle or "Quad",
        EasingDirection = easingDirection or "Out",
        RepeatCount = repeatCount or 0,
        Reverses = reverses or false,
        DelayTime = delayTime or 0
    }, TweenInfo)
end
_genv.TweenInfo = TweenInfo

-- RaycastParams
local RaycastParams = {}
RaycastParams.__index = RaycastParams
function RaycastParams.new()
    return setmetatable({
        FilterDescendantsInstances = {},
        FilterType = 0,
        IgnoreWater = true,
        CollisionGroup = "Default"
    }, RaycastParams)
end
_genv.RaycastParams = RaycastParams

-- Enums
local function createEnumProxy(enumName)
    local enumTable = {}
    return setmetatable(enumTable, {
        __index = function(_, itemName)
            local item = {
                Name = itemName,
                Value = 0,
                EnumType = enumName,
                __tostring = function() return "Enum." .. enumName .. "." .. itemName end
            }
            rawset(enumTable, itemName, item)
            return item
        end
    })
end

local Enum = setmetatable({}, {
    __index = function(t, enumName)
        local ep = createEnumProxy(enumName)
        rawset(t, enumName, ep)
        return ep
    end
})

local commonEnums = {
    UserInputType = { "MouseButton1", "MouseButton2", "MouseButton3", "MouseMovement", "MouseWheel", "Keyboard", "Touch", "None" },
    KeyCode = {
        "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z",
        "Zero","One","Two","Three","Four","Five","Six","Seven","Eight","Nine",
        "LeftShift","RightShift","LeftControl","RightControl","LeftAlt","RightAlt",
        "Space","Return","Backspace","Tab","Escape","CapsLock",
        "Up","Down","Left","Right",
        "F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12",
        "Unknown"
    },
    EasingStyle = { "Linear", "Sine", "Back", "Quad", "Quart", "Quint", "Bounce", "Elastic", "Cubic" },
    EasingDirection = { "In", "Out", "InOut" },
    Font = { "SourceSans", "SourceSansBold", "SourceSansItalic", "Gotham", "GothamBold", "Roboto", "Ubuntu" },
    RaycastFilterType = { "Blacklist", "Whitelist", "Exclude", "Include" },
    TextXAlignment = { "Left", "Center", "Right" },
    TextYAlignment = { "Top", "Center", "Bottom" },
    PlaybackState = { "Begin", "Delayed", "Playing", "Paused", "Completed", "Cancelled" }
}

for enumName, items in pairs(commonEnums) do
    local ep = Enum[enumName]
    for _, item in ipairs(items) do
        local _ = ep[item]
    end
end

_genv.Enum = Enum

-- ============================================================================
-- Instance System
-- ============================================================================
local Instance = {}
local _instanceIdCounter = 0

function Instance.new(className, parent)
    assert(type(className) == "string", "Instance.new requires a className string")
    _instanceIdCounter = _instanceIdCounter + 1
    
    local defaultProperties = {
        Visible = true,
        Transparency = 0,
        BackgroundTransparency = 0,
        BackgroundColor3 = Color3.new(1, 1, 1),
        TextColor3 = Color3.new(0, 0, 0),
        Text = "",
        TextSize = 14,
        Font = Enum.Font.SourceSans,
        BorderSizePixel = 0,
        ZIndex = 1,
        AnchorPoint = Vector2.new(0, 0),
        Size = UDim2.new(0, 100, 0, 100),
        Position = UDim2.new(0, 0, 0, 0),
        CanvasSize = UDim2.new(0, 0, 0, 0),
        ScrollBarThickness = 6,
        ClipsDescendants = false,
        Active = false,
        Draggable = false,
        AutoButtonColor = true,
        AbsolutePosition=Vector2.new(0,0),
        AbsoluteSize=Vector2.new(200,36),
        AbsoluteContentSize=Vector2.new(200,36),
        TextBounds=Vector2.new(100,14),
        CameraOffset=Vector3.new(0,0,0),
        AutoRotate=true,
        Neutral=false,
        PlaceholderText = "",
        Health = 100,
        MaxHealth = 100,
        WalkSpeed = 16,
        JumpPower = 50,
        CFrame = CFrame.new(0, 0, 0),
        Anchored = false,
        CanCollide = true,
        Value = nil,
        PrimaryPart = nil
    }
    
    local obj = {
        _id = _instanceIdCounter,
        ClassName = className,
        Name = className,
        _parent = nil,
        _children = {},
        _properties = defaultProperties,
        _propertySignals = {},
        
        -- Common Signals
        Changed = createSignal(),
        ChildAdded = createSignal(),
        ChildRemoved = createSignal(),
        AncestryChanged = createSignal(),
        Destroying=createSignal(),
        
        -- Button signals
        MouseButton1Click = createSignal(),
        MouseButton1Down = createSignal(),
        MouseButton1Up = createSignal(),
        MouseButton2Click = createSignal(),
        MouseButton2Down = createSignal(),
        MouseButton2Up = createSignal(),
        Activated = createSignal(),
        
        -- Input signals
        InputBegan = createSignal(),
        InputEnded = createSignal(),
        InputChanged = createSignal(),
        MouseEnter = createSignal(),
        MouseLeave = createSignal(),
        FocusLost = createSignal(),
        Focused = createSignal(),
        
        -- Humanoid signals
        Died = createSignal(),
        HealthChanged = createSignal()
    }
    
    function obj:FindFirstChild(name, recursive)
        for _, child in ipairs(self._children) do
            if child.Name == name then
                return child
            end
        end
        if recursive then
            for _, child in ipairs(self._children) do
                local found = child:FindFirstChild(name, true)
                if found then return found end
            end
        end
        return nil
    end
    
    function obj:WaitForChild(name, timeout)
        local child = self:FindFirstChild(name)
        return child
    end
    
    function obj:FindFirstChildOfClass(className)
        for _, child in ipairs(self._children) do
            if child.ClassName == className then
                return child
            end
        end
        return nil
    end
    
    function obj:FindFirstChildWhichIsA(className)
        for _, child in ipairs(self._children) do
            if child:IsA(className) then
                return child
            end
        end
        return nil
    end
    
    function obj:FindFirstAncestor(name)
        local curr = self._parent
        while curr do
            if curr.Name == name then return curr end
            curr = curr._parent
        end
        return nil
    end
    
    function obj:FindFirstAncestorOfClass(className)
        local curr = self._parent
        while curr do
            if curr.ClassName == className then return curr end
            curr = curr._parent
        end
        return nil
    end
    
    function obj:GetChildren()
        local list = {}
        for _, c in ipairs(self._children) do
            table.insert(list, c)
        end
        return list
    end
    
    function obj:GetDescendants()
        local list = {}
        local function scan(target)
            for _, c in ipairs(target._children) do
                table.insert(list, c)
                scan(c)
            end
        end
        scan(self)
        return list
    end
    
    function obj:IsDescendantOf(ancestor)
        local curr = self._parent
        while curr do
            if curr == ancestor then return true end
            curr = curr._parent
        end
        return false
    end
    
    function obj:IsAncestorOf(descendant)
        if not descendant then return false end
        return descendant:IsDescendantOf(self)
    end
    
    function obj:SetPrimaryPartCFrame(cf)
        if self.PrimaryPart then
            self.PrimaryPart.CFrame = cf
        else
            self.CFrame = cf
        end
    end
    
    function obj:IsA(className)
        if self.ClassName == className then return true end
        if className == "Instance" then return true end
        if className == "GuiObject" and (self.ClassName == "Frame" or self.ClassName == "TextLabel" or self.ClassName == "TextButton" or self.ClassName == "ScrollingFrame" or self.ClassName == "TextBox" or self.ClassName == "ImageLabel" or self.ClassName == "ImageButton") then
            return true
        end
        if className == "BasePart" and (self.ClassName == "Part" or self.ClassName == "MeshPart") then
            return true
        end
        return false
    end
    
    function obj:Destroy()
        if rawget(self,"_destroyed") then return end
        rawset(self,"_destroyed",true)
        self.Destroying:Fire()
        if self._parent then
            self.Parent = nil
        end
        for i = #self._children, 1, -1 do
            self._children[i]:Destroy()
        end
        local function disconnectSignals(values)
            for _,value in pairs(values) do
                if type(value)=="table" and rawget(value,"_listeners") then
                    while #value._listeners>0 do value._listeners[#value._listeners]:Disconnect() end
                end
            end
        end
        disconnectSignals(self)
        disconnectSignals(rawget(self,"_properties"))
        disconnectSignals(rawget(self,"_propertySignals"))
    end
    
    function obj:ClearAllChildren()
        for i = #self._children, 1, -1 do
            self._children[i]:Destroy()
        end
    end
    
    function obj:GetPropertyChangedSignal(prop)
        local sigs = rawget(self, "_propertySignals")
        if not sigs[prop] then
            sigs[prop] = createSignal()
        end
        return sigs[prop]
    end
    
    function obj:TweenPosition(endPos, easingDirection, easingStyle, time, override, callback)
        self.Position = endPos
        if callback then callback(Enum.PlaybackState.Completed) end
        return true
    end
    
    function obj:TweenSize(endSize, easingDirection, easingStyle, time, override, callback)
        self.Size = endSize
        if callback then callback(Enum.PlaybackState.Completed) end
        return true
    end
    
    function obj:Clone()
        local copy = Instance.new(self.ClassName)
        copy.Name = self.Name
        for k, v in pairs(self._properties) do
            copy[k] = v
        end
        for _, c in ipairs(self._children) do
            local childCopy = c:Clone()
            childCopy.Parent = copy
        end
        return copy
    end
    
    -- Metatable for index and property changed events
    local meta = {
        __index = function(t, k)
            if k == "Parent" then
                return rawget(t, "_parent")
            end
            local raw = rawget(t, k)
            if raw ~= nil then return raw end
            
            local propVal = rawget(t, "_properties")[k]
            if propVal ~= nil then return propVal end
            
            -- Child indexing (e.g. Character.HumanoidRootPart)
            local child = t:FindFirstChild(k)
            if child then return child end
            
            return nil
        end,
        
        __newindex = function(t, k, v)
            if k == "Parent" then
                local oldParent = rawget(t, "_parent")
                if oldParent == v then return end
                if oldParent then
                    for idx, c in ipairs(oldParent._children) do
                        if c == t then
                            table.remove(oldParent._children, idx)
                            break
                        end
                    end
                    oldParent.ChildRemoved:Fire(t)
                end
                rawset(t, "_parent", v)
                if v then
                    table.insert(v._children, t)
                    v.ChildAdded:Fire(t)
                end
                t.AncestryChanged:Fire(t, v)
                return
            end
            
            if k == "Name" then
                local old = rawget(t, "Name")
                rawset(t, "Name", v)
                if old ~= v then
                    local sig = rawget(t, "_propertySignals")["Name"]
                    if sig then sig:Fire(v) end
                    t.Changed:Fire("Name")
                end
                return
            end
            
            local props = rawget(t, "_properties")
            local oldVal = props[k]
            props[k] = v
            
            if k == "Health" and t.HealthChanged then
                if v ~= oldVal then
                    t.HealthChanged:Fire(v)
                    if v <= 0 and t.Died then
                        t.Died:Fire()
                    end
                end
            end
            
            if oldVal ~= v then
                local sig = rawget(t, "_propertySignals")[k]
                if sig then sig:Fire(v) end
                t.Changed:Fire(k)
            end
        end
    }
    
    setmetatable(obj, meta)
    if className=="BindableEvent" then
        obj.Event=createSignal()
        function obj:Fire(...) self.Event:Fire(...) end
    end
    
    if parent then
        obj.Parent = parent
    end
    
    return obj
end

_genv.Instance = Instance

-- ============================================================================
-- Drawing API
-- ============================================================================
local Drawing = { _activeDrawings = {} }
Drawing._activeObjects = Drawing._activeDrawings

function Drawing.new(drawType)
    local d = {
        _id = #Drawing._activeDrawings + 1,
        Type = drawType,
        Visible = false,
        Transparency = 1,
        Color = Color3.new(1, 1, 1),
        ZIndex = 1,
        Thickness = 1,
        Filled = false,
        Position = Vector2.new(0, 0),
        Size = Vector2.new(0, 0),
        From = Vector2.new(0, 0),
        To = Vector2.new(0, 0),
        Text = "",
        Center = false,
        Outline = false,
        OutlineColor = Color3.new(0, 0, 0),
        Radius = 10,
        NumSides = 16
    }
    
    function d:Remove()
        d.Visible = false
        for i = #Drawing._activeDrawings, 1, -1 do
            if Drawing._activeDrawings[i] == d then
                table.remove(Drawing._activeDrawings, i)
                break
            end
        end
    end
    d.Destroy = d.Remove
    
    table.insert(Drawing._activeDrawings, d)
    return d
end

_genv.Drawing = Drawing

-- ============================================================================
-- JSON Parser & Serializer (Pure Lua HttpService mock)
-- ============================================================================
local function jsonEncode(val)
    local t = type(val)
    if t == "nil" then
        return "null"
    elseif t == "boolean" then
        return val and "true" or "false"
    elseif t == "number" then
        if val ~= val then return "null" end
        if val >= math.huge or val <= -math.huge then return "null" end
        return tostring(val)
    elseif t == "string" then
        local s = val:gsub('\\', '\\\\'):gsub('"', '\\"'):gsub('\n', '\\n'):gsub('\r', '\\r'):gsub('\t', '\\t')
        return '"' .. s .. '"'
    elseif t == "table" then
        local isArray = true
        local n = 0
        for k, _ in pairs(val) do
            n = n + 1
            if type(k) ~= "number" or k ~= n then
                isArray = false
                break
            end
        end
        if n == 0 then
            return "{}"
        end
        if isArray then
            local parts = {}
            for i = 1, n do
                table.insert(parts, jsonEncode(val[i]))
            end
            return "[" .. table.concat(parts, ",") .. "]"
        else
            local parts = {}
            for k, v in pairs(val) do
                table.insert(parts, jsonEncode(tostring(k)) .. ":" .. jsonEncode(v))
            end
            return "{" .. table.concat(parts, ",") .. "}"
        end
    else
        return '"' .. tostring(val) .. '"'
    end
end

local function jsonDecode(str)
    str = tostring(str)
    local idx = 1
    local len = #str
    
    local function skipWhitespace()
        while idx <= len do
            local b = str:sub(idx, idx)
            if b == ' ' or b == '\t' or b == '\n' or b == '\r' then
                idx = idx + 1
            else
                break
            end
        end
    end
    
    local parseValue
    
    local function parseString()
        idx = idx + 1
        local buf = {}
        while idx <= len do
            local c = str:sub(idx, idx)
            if c == '"' then
                idx = idx + 1
                return table.concat(buf)
            elseif c == '\\' then
                idx = idx + 1
                local esc = str:sub(idx, idx)
                idx = idx + 1
                if esc == 'n' then table.insert(buf, '\n')
                elseif esc == 'r' then table.insert(buf, '\r')
                elseif esc == 't' then table.insert(buf, '\t')
                elseif esc == 'b' then table.insert(buf, '\b')
                elseif esc == 'f' then table.insert(buf, '\f')
                elseif esc == '"' then table.insert(buf, '"')
                elseif esc == '\\' then table.insert(buf, '\\')
                elseif esc == '/' then table.insert(buf, '/')
                elseif esc == 'u' then
                    local hex = str:sub(idx, idx + 3)
                    idx = idx + 4
                    local code = tonumber(hex, 16)
                    if code then
                        if utf8 and utf8.char then
                            table.insert(buf, utf8.char(code))
                        elseif code < 256 then
                            table.insert(buf, string.char(code))
                        else
                            table.insert(buf, "\\u" .. hex)
                        end
                    end
                else table.insert(buf, esc) end
            else
                table.insert(buf, c)
                idx = idx + 1
            end
        end
        error("Unterminated string in JSON")
    end
    
    local function parseNumber()
        local start = idx
        if str:sub(idx, idx) == '-' then idx = idx + 1 end
        while idx <= len do
            local c = str:sub(idx, idx)
            if (c >= '0' and c <= '9') or c == '.' or c == 'e' or c == 'E' or c == '+' or c == '-' then
                idx = idx + 1
            else
                break
            end
        end
        local numStr = str:sub(start, idx - 1)
        local n = tonumber(numStr)
        if not n then error("Invalid number in JSON: " .. numStr) end
        return n
    end
    
    local function parseArray()
        idx = idx + 1
        local arr = {}
        skipWhitespace()
        if str:sub(idx, idx) == ']' then
            idx = idx + 1
            return arr
        end
        while idx <= len do
            local val = parseValue()
            table.insert(arr, val)
            skipWhitespace()
            local c = str:sub(idx, idx)
            if c == ']' then
                idx = idx + 1
                return arr
            elseif c == ',' then
                idx = idx + 1
            else
                error("Expected ',' or ']' in JSON array at " .. idx)
            end
        end
        error("Unterminated array in JSON")
    end
    
    local function parseObject()
        idx = idx + 1
        local obj = {}
        skipWhitespace()
        if str:sub(idx, idx) == '}' then
            idx = idx + 1
            return obj
        end
        while idx <= len do
            skipWhitespace()
            if str:sub(idx, idx) ~= '"' then
                error("Expected string key in JSON object at " .. idx)
            end
            local key = parseString()
            skipWhitespace()
            if str:sub(idx, idx) ~= ':' then
                error("Expected ':' after key in JSON object at " .. idx)
            end
            idx = idx + 1
            local val = parseValue()
            obj[key] = val
            skipWhitespace()
            local c = str:sub(idx, idx)
            if c == '}' then
                idx = idx + 1
                return obj
            elseif c == ',' then
                idx = idx + 1
            else
                error("Expected ',' or '}' in JSON object at " .. idx)
            end
        end
        error("Unterminated object in JSON")
    end
    
    parseValue = function()
        skipWhitespace()
        if idx > len then error("Unexpected end of JSON") end
        local c = str:sub(idx, idx)
        if c == '"' then
            return parseString()
        elseif c == '{' then
            return parseObject()
        elseif c == '[' then
            return parseArray()
        elseif c == 't' and str:sub(idx, idx + 3) == "true" then
            idx = idx + 4
            return true
        elseif c == 'f' and str:sub(idx, idx + 4) == "false" then
            idx = idx + 5
            return false
        elseif c == 'n' and str:sub(idx, idx + 3) == "null" then
            idx = idx + 4
            return nil
        else
            return parseNumber()
        end
    end
    
    local res = parseValue()
    return res
end

-- ============================================================================
-- Services & DataModel Hierarchy
-- ============================================================================
local game = Instance.new("DataModel")
game.Name = "Game"
game.Loaded = createSignal()
function game:IsLoaded() return true end

local workspace = Instance.new("Workspace", game)
workspace.Name = "Workspace"

local currentCamera = Instance.new("Camera", workspace)
currentCamera.Name = "Camera"
currentCamera.FieldOfView = 70
currentCamera.ViewportSize = Vector2.new(1920, 1080)
currentCamera.CFrame = CFrame.new(0, 10, 20)

function currentCamera:WorldToViewportPoint(worldPos)
    local rel = self.CFrame:PointToObjectSpace(worldPos)
    local depth = -rel.Z
    if depth <= 0.1 then
        return Vector3.new(-1000, -1000, depth), false
    end
    local fovRad = math.rad(self.FieldOfView)
    local h = math.tan(fovRad / 2) * 2
    local aspect = self.ViewportSize.X / self.ViewportSize.Y
    local w = h * aspect
    
    local normX = (rel.X / (depth * w * 0.5))
    local normY = (rel.Y / (depth * h * 0.5))
    
    local screenX = (normX + 1) * 0.5 * self.ViewportSize.X
    local screenY = (1 - normY) * 0.5 * self.ViewportSize.Y
    local onScreen = (depth > 0.1) and (screenX >= 0 and screenX <= self.ViewportSize.X) and (screenY >= 0 and screenY <= self.ViewportSize.Y)
    return Vector3.new(screenX, screenY, depth), onScreen
end

function currentCamera:WorldToScreenPoint(worldPos)
    return self:WorldToViewportPoint(worldPos)
end

function currentCamera:ScreenPointToRay(x, y)
    local origin = self.CFrame.Position
    local dir = Vector3.new(x - self.ViewportSize.X/2, self.ViewportSize.Y/2 - y, -1000).Unit
    return { Origin = origin, Direction = dir }
end

workspace.CurrentCamera = currentCamera

function workspace:Raycast(origin, direction, params)
    return nil
end

local Players = Instance.new("Players", game)
Players.PlayerAdded = createSignal()
Players.PlayerRemoving = createSignal()

local LocalPlayer = Instance.new("Player", Players)
LocalPlayer.Name = "LocalPlayer"
LocalPlayer.DisplayName = "LocalPlayer"
LocalPlayer.UserId = 12345678
LocalPlayer.TeamColor = BrickColor.new("Bright blue")
LocalPlayer.CharacterAdded = createSignal()
LocalPlayer.CharacterRemoving = createSignal()
LocalPlayer._friendCache = {}

local PlayerGui = Instance.new("PlayerGui", LocalPlayer)
PlayerGui.Name = "PlayerGui"
LocalPlayer.PlayerGui = PlayerGui

local MockMouse = {
    Hit = CFrame.new(0, 0, 0),
    Target = nil,
    X = 960,
    Y = 540,
    KeyDown = createSignal(),
    KeyUp = createSignal(),
    Button1Down = createSignal(),
    Button1Up = createSignal(),
    Button2Down = createSignal(),
    Button2Up = createSignal(),
    Move = createSignal()
}
function LocalPlayer:GetMouse()
    return MockMouse
end

function LocalPlayer:IsFriendsWith(userId)
    if self._friendCache[userId] ~= nil then
        return self._friendCache[userId]
    end
    return false
end

Players.LocalPlayer = LocalPlayer

function Players:GetUserThumbnailAsync(userId, thumbType, thumbSize)
    return "rbxassetid://0", true
end

function Players:GetPlayers()
    local list = {}
    for _, child in ipairs(self:GetChildren()) do
        if child.ClassName == "Player" then
            table.insert(list, child)
        end
    end
    return list
end

function Players:GetPlayerFromCharacter(char)
    if not char then return nil end
    for _, p in ipairs(self:GetPlayers()) do
        if p.Character == char then return p end
    end
    return nil
end

local Teams = Instance.new("Teams", game)
Teams.TeamsAdded = createSignal()
Teams.TeamsRemoving = createSignal()

function Teams:GetTeams()
    local list = {}
    for _, child in ipairs(self:GetChildren()) do
        if child.ClassName == "Team" then
            table.insert(list, child)
        end
    end
    return list
end

local RunService = Instance.new("RunService", game)
RunService.RenderStepped = createSignal()
RunService.Heartbeat = createSignal()
RunService.Stepped = createSignal()
RunService._boundRenderSteps = {}
function RunService:IsStudio() return false end
function RunService:IsClient() return true end
function RunService:IsServer() return false end

function RunService:BindToRenderStep(name, priority, callback)
    self._boundRenderSteps[name] = callback
end

function RunService:UnbindFromRenderStep(name)
    self._boundRenderSteps[name] = nil
end

function RunService:Step(dt)
    dt = dt or (1 / 60)
    for _, cb in pairs(self._boundRenderSteps) do
        pcall(cb, dt)
    end
    self.RenderStepped:Fire(dt)
    self.Stepped:Fire(0, dt)
    self.Heartbeat:Fire(dt)
end

local UserInputService = Instance.new("UserInputService", game)
UserInputService.InputBegan = createSignal()
UserInputService.InputEnded = createSignal()
UserInputService.InputChanged = createSignal()
UserInputService.WindowFocused = createSignal()
UserInputService.WindowFocusReleased = createSignal()
UserInputService.MouseBehavior = 0

function UserInputService:GetMouseLocation()
    return Vector2.new(_mousePos.X, _mousePos.Y)
end

function UserInputService:IsKeyDown(keyCode)
    return false
end

function UserInputService:IsMouseButtonPressed(mouseButton)
    if mouseButton == Enum.UserInputType.MouseButton1 then return _mouseButtons[1] end
    if mouseButton == Enum.UserInputType.MouseButton2 then return _mouseButtons[2] end
    return false
end

local TweenService = Instance.new("TweenService", game)
function TweenService:Create(instance, tweenInfo, properties)
    local tween = {
        Instance = instance,
        TweenInfo = tweenInfo,
        Properties = properties,
        PlaybackState = Enum.PlaybackState.Begin,
        Completed = createSignal()
    }
    function tween:Play()
        self.PlaybackState = Enum.PlaybackState.Playing
        for k, v in pairs(self.Properties) do
            self.Instance[k] = v
        end
        self.PlaybackState = Enum.PlaybackState.Completed
        self.Completed:Fire(Enum.PlaybackState.Completed)
    end
    function tween:Cancel()
        self.PlaybackState = Enum.PlaybackState.Cancelled
    end
    function tween:Pause()
        self.PlaybackState = Enum.PlaybackState.Paused
    end
    return tween
end

local HttpService = Instance.new("HttpService", game)
function HttpService:JSONEncode(data)
    return jsonEncode(data)
end
function HttpService:JSONDecode(str)
    return jsonDecode(str)
end
function HttpService:GenerateGUID(wrap)
    local guid = string.format("%08x-%04x-4%03x-%04x-%012x",
        math.random(0, 0xFFFFFFFF), math.random(0, 0xFFFF),
        math.random(0, 0xFFF), math.random(0x8000, 0xBFFF),
        math.random(0, 0xFFFFFFFFFFFF)
    )
    if wrap then return "{" .. guid .. "}" end
    return guid
end

local CoreGui = Instance.new("ScreenGui", game)
CoreGui.Name = "CoreGui"

local StarterGui = Instance.new("StarterGui", game)
StarterGui._notifications = {}
function StarterGui:SetCore(coreType, data)
    if coreType == "SendNotification" then
        table.insert(self._notifications, data)
    end
end

local ReplicatedStorage = Instance.new("Folder", game)
ReplicatedStorage.Name = "ReplicatedStorage"

local ContextActionService = Instance.new("ContextActionService", game)
function ContextActionService:BindAction(name, fn, touch, ...) end
function ContextActionService:UnbindAction(name) end
function ContextActionService:BindActionAtPriority(name, fn, touch, priority, ...) end

-- Wire Services to game:GetService
local _services = {
    ["Workspace"] = workspace,
    ["Players"] = Players,
    ["Teams"] = Teams,
    ["RunService"] = RunService,
    ["UserInputService"] = UserInputService,
    ["TweenService"] = TweenService,
    ["HttpService"] = HttpService,
    ["CoreGui"] = CoreGui,
    ["StarterGui"] = StarterGui,
    ["ReplicatedStorage"] = ReplicatedStorage,
    ["ContextActionService"] = ContextActionService
}

function game:GetService(serviceName)
    local s = _services[serviceName]
    if s then return s end
    error("Service not found in mock: " .. tostring(serviceName), 2)
end

function game:HttpGet(url)
    url = tostring(url)
    local cleanUrl = url:gsub("%?.*$", "")
    
    local githubPrefix = "https://raw.githubusercontent.com/fraudesnaoseinaosei-max/j4rty678/main/"
    if cleanUrl:sub(1, #githubPrefix) == githubPrefix then
        local relPath = cleanUrl:sub(#githubPrefix + 1)
        if _vfsFiles[relPath] ~= nil then
            return _vfsFiles[relPath]
        end
        local f = io.open(relPath, "r")
        if f then
            local content = f:read("*a")
            f:close()
            return content
        end
    end
    
    local f = io.open(cleanUrl, "r")
    if f then
        local content = f:read("*a")
        f:close()
        return content
    end
    
    if _vfsFiles[cleanUrl] ~= nil then
        return _vfsFiles[cleanUrl]
    end
    
    error("HttpGet 404: " .. url, 2)
end

_genv.loadstring = function(code, chunkname)
    local fn, err = _nativeLoad(code, chunkname or "mock_loadstring")
    if not fn then
        error("Mock loadstring syntax error: " .. tostring(err), 2)
    end
    return fn
end

-- ============================================================================
-- Helper Factories for Tests
-- ============================================================================
function MockRoblox.createMockCharacter(name, pos, teamColor)
    local model = Instance.new("Model", workspace)
    model.Name = name
    
    local hrp = Instance.new("Part", model)
    hrp.Name = "HumanoidRootPart"
    hrp.Size = Vector3.new(2, 2, 1)
    hrp.Position = pos or Vector3.new(0, 3, 0)
    hrp.CFrame = CFrame.new(hrp.Position)
    
    local head = Instance.new("Part", model)
    head.Name = "Head"
    head.Size = Vector3.new(1.2, 1.2, 1.2)
    head.Position = hrp.Position + Vector3.new(0, 1.5, 0)
    head.CFrame = CFrame.new(head.Position)
    
    local humanoid = Instance.new("Humanoid", model)
    humanoid.Name = "Humanoid"
    humanoid.Health = 100
    humanoid.MaxHealth = 100
    
    return model
end

function MockRoblox.createMockPlayer(name, userId, teamName, teamColorName, charPos)
    local player = Instance.new("Player", Players)
    player.Name = name
    player.DisplayName = name
    player.UserId = userId or math.random(100000, 999999)
    
    if teamName then
        local team = Teams:FindFirstChild(teamName)
        if not team then
            team = Instance.new("Team", Teams)
            team.Name = teamName
            team.TeamColor = BrickColor.new(teamColorName or "Bright red")
        end
        player.Team = team
        player.TeamColor = team.TeamColor
    else
        player.TeamColor = BrickColor.new(teamColorName or "Bright red")
    end
    
    local char = MockRoblox.createMockCharacter(name, charPos or Vector3.new(0, 3, 50), player.TeamColor)
    player.Character = char
    Players.PlayerAdded:Fire(player)
    return player
end

-- Export globals to _genv and _G
_genv.game = game
_genv.workspace = workspace
_genv.Workspace = workspace
_genv.Players = Players
_genv.Teams = Teams
_genv.RunService = RunService
_genv.UserInputService = UserInputService
_genv.TweenService = TweenService
_genv.HttpService = HttpService
_genv.CoreGui = CoreGui
_genv.StarterGui = StarterGui
_genv.ReplicatedStorage = ReplicatedStorage
_genv.ContextActionService = ContextActionService
_genv.MockRoblox = MockRoblox

for k, v in pairs(_genv) do
    _G[k] = v
end

MockRoblox.genv = _genv
MockRoblox.game = game
MockRoblox.workspace = workspace
MockRoblox.Players = Players
MockRoblox.Teams = Teams
MockRoblox.RunService = RunService
MockRoblox.UserInputService = UserInputService
MockRoblox.TweenService = TweenService
MockRoblox.HttpService = HttpService
MockRoblox.CoreGui = CoreGui
MockRoblox.StarterGui = StarterGui
MockRoblox.ReplicatedStorage = ReplicatedStorage
MockRoblox.ContextActionService = ContextActionService
MockRoblox.Drawing = Drawing
MockRoblox.vfsFiles = _vfsFiles

return MockRoblox
