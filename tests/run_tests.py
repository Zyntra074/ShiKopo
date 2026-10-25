#!/usr/bin/env python3
"""
tests/run_tests.py
Headless Test Suite Runner for DreezHub
Executes:
  1. Static syntax verification across all Lua scripts (verify_syntax.py)
  2. Mock Roblox Engine smoke test verifying all datatypes, services, instances, signals,
     VFS, Drawing API, and executor globals in lupa (Lua 5.5 VM).
"""

import sys
import time
from pathlib import Path
import lupa

# Import verify_syntax module
from verify_syntax import scan_and_verify, REPO_ROOT

def run_mock_engine_smoke_test() -> tuple[int, int, list[str]]:
    """
    Initializes lupa Lua VM, injects mock_roblox.lua, and verifies all features.
    Returns (passed_count, failed_count, error_messages).
    """
    mock_file = REPO_ROOT / "tests" / "mock_roblox.lua"
    if not mock_file.exists():
        return 0, 1, [f"Mock file not found: {mock_file}"]

    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    mock_code = mock_file.read_text(encoding="utf-8")
    
    try:
        mock = lua.execute(mock_code)
    except Exception as e:
        return 0, 1, [f"Failed to load mock_roblox.lua into Lua VM: {e}"]

    tests = []
    
    # -------------------------------------------------------------------------
    # Datatypes Tests
    # -------------------------------------------------------------------------
    def test_vector2():
        v1 = lua.eval('Vector2.new(10, 20)')
        v2 = lua.eval('Vector2.new(5, 5)')
        v_sum = lua.eval('Vector2.new(10, 20) + Vector2.new(5, 5)')
        assert v_sum.X == 15 and v_sum.Y == 25, f"Vector2 add failed: {v_sum}"
        v_sub = lua.eval('Vector2.new(10, 20) - Vector2.new(5, 5)')
        assert v_sub.X == 5 and v_sub.Y == 15, f"Vector2 sub failed: {v_sub}"
        v_mul = lua.eval('Vector2.new(10, 20) * 2')
        assert v_mul.X == 20 and v_mul.Y == 40, f"Vector2 scalar mul failed: {v_mul}"
        mag = lua.eval('Vector2.new(3, 4).Magnitude')
        assert abs(mag - 5.0) < 0.001, f"Vector2 Magnitude failed: {mag}"
        dot = lua.eval('Vector2.new(1, 0):Dot(Vector2.new(0, 1))')
        assert dot == 0, f"Vector2 Dot failed: {dot}"
    tests.append(("Datatypes: Vector2 arithmetic & properties", test_vector2))

    def test_vector3():
        v1 = lua.eval('Vector3.new(1, 2, 3)')
        v2 = lua.eval('Vector3.new(4, 5, 6)')
        v_sum = lua.eval('Vector3.new(1, 2, 3) + Vector3.new(4, 5, 6)')
        assert v_sum.X == 5 and v_sum.Y == 7 and v_sum.Z == 9, f"Vector3 add failed: {v_sum}"
        mag = lua.eval('Vector3.new(2, 3, 6).Magnitude')
        assert abs(mag - 7.0) < 0.001, f"Vector3 Magnitude failed: {mag}"
        dot = lua.eval('Vector3.new(1, 2, 3):Dot(Vector3.new(4, 5, 6))')
        assert dot == 32, f"Vector3 Dot failed: {dot}"
        cross = lua.eval('Vector3.new(1, 0, 0):Cross(Vector3.new(0, 1, 0))')
        assert cross.X == 0 and cross.Y == 0 and cross.Z == 1, f"Vector3 Cross failed: {cross}"
        lerp = lua.eval('Vector3.new(0, 0, 0):Lerp(Vector3.new(10, 20, 30), 0.5)')
        assert lerp.X == 5 and lerp.Y == 10 and lerp.Z == 15, f"Vector3 Lerp failed: {lerp}"
    tests.append(("Datatypes: Vector3 arithmetic, cross & lerp", test_vector3))

    def test_color3():
        c1 = lua.eval('Color3.new(1, 0.5, 0)')
        assert abs(c1.R - 1.0) < 0.001 and abs(c1.G - 0.5) < 0.001 and c1.B == 0
        c_rgb = lua.eval('Color3.fromRGB(255, 128, 0)')
        assert abs(c_rgb.R - 1.0) < 0.01 and abs(c_rgb.G - (128/255)) < 0.01
        c_hex = lua.eval('Color3.fromHex("#FF8000")')
        assert abs(c_hex.R - 1.0) < 0.01 and abs(c_hex.G - (128/255)) < 0.01
        hex_str = lua.eval('Color3.fromRGB(255, 0, 128):ToHex()')
        assert hex_str == "FF0080", f"Color3:ToHex failed: {hex_str}"
    tests.append(("Datatypes: Color3 new, fromRGB, fromHex, ToHex", test_color3))

    def test_cframe():
        cf = lua.eval('CFrame.new(10, 20, 30)')
        assert cf.Position.X == 10 and cf.Position.Y == 20 and cf.Position.Z == 30
        assert cf.X == 10 and cf.Y == 20 and cf.Z == 30
        p_world = lua.eval('CFrame.new(0, 10, 0):PointToWorldSpace(Vector3.new(5, 5, 5))')
        assert p_world.X == 5 and p_world.Y == 15 and p_world.Z == 5
        cf_angles = lua.eval('CFrame.Angles(0, math.rad(90), 0)')
        assert cf_angles.Position.X == 0 and cf_angles.Position.Y == 0
        cf_look = lua.eval('CFrame.lookAt(Vector3.new(0, 0, 0), Vector3.new(0, 0, -10))')
        assert cf_look.Position.Z == 0
        cf_inv = lua.eval('CFrame.new(5, 10, 15):Inverse()')
        assert abs(cf_inv.Position.X - (-5)) < 0.001 and abs(cf_inv.Position.Y - (-10)) < 0.001
    tests.append(("Datatypes: CFrame transforms, Angles, lookAt, Inverse", test_cframe))

    def test_udim2():
        u = lua.eval('UDim2.new(0.5, 10, 0.2, 5)')
        assert u.X.Scale == 0.5 and u.X.Offset == 10
        assert u.Y.Scale == 0.2 and u.Y.Offset == 5
        u_off = lua.eval('UDim2.fromOffset(100, 200)')
        assert u_off.X.Offset == 100 and u_off.Y.Offset == 200
        u_scale = lua.eval('UDim2.fromScale(1, 1)')
        assert u_scale.X.Scale == 1 and u_scale.Y.Scale == 1
    tests.append(("Datatypes: UDim2 and UDim", test_udim2))

    def test_enum():
        mb1 = lua.eval('Enum.UserInputType.MouseButton1')
        assert mb1.Name == "MouseButton1" and mb1.EnumType == "UserInputType"
        kc_e = lua.eval('Enum.KeyCode.E')
        assert kc_e.Name == "E" and kc_e.EnumType == "KeyCode"
        quad = lua.eval('Enum.EasingStyle.Quad')
        assert quad.Name == "Quad" and quad.EnumType == "EasingStyle"
        # Dynamic enum fallback
        dyn = lua.eval('Enum.CustomEnum.DynamicItem')
        assert dyn.Name == "DynamicItem"
    tests.append(("Datatypes: Enum and EnumItem proxy lookup", test_enum))

    # -------------------------------------------------------------------------
    # Signals & Connections Tests
    # -------------------------------------------------------------------------
    def test_signal_connection():
        lua.execute('''
            _test_sig_fired = 0
            _test_sig_val = ""
            local sig = MockRoblox.createSignal()
            local conn = sig:Connect(function(v)
                _test_sig_fired = _test_sig_fired + 1
                _test_sig_val = v
            end)
            sig:Fire("first")
            conn:Disconnect()
            sig:Fire("second")
        ''')
        assert lua.eval('_test_sig_fired') == 1, "Signal fired after disconnect"
        assert lua.eval('_test_sig_val') == "first", "Signal payload mismatch"
    tests.append(("Signals: Connect, Fire, Disconnect lifecycle", test_signal_connection))

    # -------------------------------------------------------------------------
    # Instance Hierarchy & Properties Tests
    # -------------------------------------------------------------------------
    def test_instance_hierarchy():
        lua.execute('''
            local parent = Instance.new("Frame")
            parent.Name = "ParentFrame"
            local child = Instance.new("TextButton", parent)
            child.Name = "ActionBtn"
            child.Text = "Click Me"
            
            _inst_found = parent:FindFirstChild("ActionBtn") == child
            _inst_child_count = #parent:GetChildren()
            _inst_is_a = child:IsA("GuiObject")
            
            child:Destroy()
            _inst_after_destroy_count = #parent:GetChildren()
        ''')
        assert lua.eval('_inst_found') == True, "FindFirstChild failed"
        assert lua.eval('_inst_child_count') == 1, "Child count mismatch"
        assert lua.eval('_inst_is_a') == True, "IsA hierarchy check failed"
        assert lua.eval('_inst_after_destroy_count') == 0, "Destroy did not remove child"
    tests.append(("Instance: Hierarchy, FindFirstChild, IsA, Destroy", test_instance_hierarchy))

    def test_instance_property_signals():
        lua.execute('''
            _prop_fired = false
            local frame = Instance.new("Frame")
            frame.Visible = true
            frame:GetPropertyChangedSignal("Visible"):Connect(function()
                _prop_fired = true
            end)
            frame.Visible = false
        ''')
        assert lua.eval('_prop_fired') == True, "GetPropertyChangedSignal did not fire"
    tests.append(("Instance: GetPropertyChangedSignal observation", test_instance_property_signals))

    # -------------------------------------------------------------------------
    # Services Tests
    # -------------------------------------------------------------------------
    def test_services_availability():
        services = [
            "Workspace", "Players", "Teams", "RunService",
            "UserInputService", "TweenService", "HttpService",
            "CoreGui", "StarterGui"
        ]
        for s in services:
            res = lua.eval(f'game:GetService("{s}")')
            assert res is not None, f"Service {s} is nil"
    tests.append(("Services: game:GetService resolution", test_services_availability))

    def test_runservice_step():
        lua.execute('''
            _render_step_fired = false
            _heartbeat_fired = false
            local rs = game:GetService("RunService")
            local c1 = rs.RenderStepped:Connect(function(dt) _render_step_fired = true end)
            local c2 = rs.Heartbeat:Connect(function(dt) _heartbeat_fired = true end)
            rs:Step(0.016)
            c1:Disconnect()
            c2:Disconnect()
        ''')
        assert lua.eval('_render_step_fired') == True, "RenderStepped did not fire"
        assert lua.eval('_heartbeat_fired') == True, "Heartbeat did not fire"
    tests.append(("Services: RunService Step and frame signals", test_runservice_step))

    def test_httpservice_json():
        lua.execute('''
            local http = game:GetService("HttpService")
            local data = { name = "DreezHub", enabled = true, count = 42, tags = { "combat", "visual" } }
            local jsonStr = http:JSONEncode(data)
            local decoded = http:JSONDecode(jsonStr)
            _json_name = decoded.name
            _json_enabled = decoded.enabled
            _json_count = decoded.count
            _json_tag1 = decoded.tags[1]
            _guid = http:GenerateGUID(false)
        ''')
        assert lua.eval('_json_name') == "DreezHub"
        assert lua.eval('_json_enabled') == True
        assert lua.eval('_json_count') == 42
        assert lua.eval('_json_tag1') == "combat"
        guid = lua.eval('_guid')
        assert len(guid) == 36, f"Invalid GUID format: {guid}"
    tests.append(("Services: HttpService JSONEncode, JSONDecode, GUID", test_httpservice_json))

    def test_camera_projection():
        lua.execute('''
            local cam = workspace.CurrentCamera
            cam.CFrame = CFrame.new(0, 0, 10)
            local screenPos, onScreen = cam:WorldToViewportPoint(Vector3.new(0, 0, -10))
            _cam_on_screen = onScreen
            _cam_screen_x = screenPos.X
            _cam_screen_y = screenPos.Y
            _cam_depth = screenPos.Z
        ''')
        assert lua.eval('_cam_on_screen') == True, "Point in front of camera should be on screen"
        assert abs(lua.eval('_cam_screen_x') - 960) < 5.0, "Projected center X mismatch"
        assert abs(lua.eval('_cam_screen_y') - 540) < 5.0, "Projected center Y mismatch"
        assert lua.eval('_cam_depth') > 0, "Depth must be positive"
    tests.append(("Services: Camera WorldToViewportPoint perspective projection", test_camera_projection))

    def test_players_and_character():
        lua.execute('''
            local p = MockRoblox.createMockPlayer("EnemyTarget", 999111, "RedTeam", "Bright red", Vector3.new(0, 0, 20))
            _player_created_name = p.Name
            _player_team_name = p.Team.Name
            _player_hrp_exists = (p.Character and p.Character:FindFirstChild("HumanoidRootPart") ~= nil)
            _players_count = #game:GetService("Players"):GetPlayers()
        ''')
        assert lua.eval('_player_created_name') == "EnemyTarget"
        assert lua.eval('_player_team_name') == "RedTeam"
        assert lua.eval('_player_hrp_exists') == True
        assert lua.eval('_players_count') >= 2 # LocalPlayer + EnemyTarget
    tests.append(("Services: Players, Teams, and MockPlayer creation", test_players_and_character))

    # -------------------------------------------------------------------------
    # Drawing API Tests
    # -------------------------------------------------------------------------
    def test_drawing_api():
        lua.execute('''
            local sq = Drawing.new("Square")
            sq.Visible = true
            sq.Size = Vector2.new(100, 200)
            sq.Position = Vector2.new(50, 50)
            sq.Color = Color3.fromRGB(255, 0, 0)
            
            local txt = Drawing.new("Text")
            txt.Text = "Enemy [50m]"
            txt.Size = 14
            txt.Visible = true
            
            _drawing_active_before = #Drawing._activeDrawings
            sq:Remove()
            _drawing_active_after = #Drawing._activeDrawings
            txt:Remove()
        ''')
        assert lua.eval('_drawing_active_before') >= 2, "Drawings not tracked in _activeDrawings"
        assert lua.eval('_drawing_active_after') == lua.eval('_drawing_active_before') - 1, "Drawing:Remove did not untrack"
    tests.append(("Drawing API: Square, Text instantiation, properties and removal", test_drawing_api))

    # -------------------------------------------------------------------------
    # Virtual File System Tests
    # -------------------------------------------------------------------------
    def test_vfs():
        lua.execute('''
            writefile("DreezHub/test_cfg.json", '{"fov": 120, "esp": true}')
            _vfs_isfile = isfile("DreezHub/test_cfg.json")
            _vfs_content = readfile("DreezHub/test_cfg.json")
            _vfs_isfolder = isfolder("DreezHub")
            delfile("DreezHub/test_cfg.json")
            _vfs_isfile_after_del = isfile("DreezHub/test_cfg.json")
        ''')
        assert lua.eval('_vfs_isfile') == True, "isfile returned false for written file"
        assert '{"fov": 120' in lua.eval('_vfs_content'), "readfile returned corrupted content"
        assert lua.eval('_vfs_isfolder') == True, "isfolder returned false"
        assert lua.eval('_vfs_isfile_after_del') == False, "delfile did not remove file"
    tests.append(("VFS: writefile, readfile, isfile, isfolder, delfile", test_vfs))

    # -------------------------------------------------------------------------
    # Mouse & Loadstring Tests
    # -------------------------------------------------------------------------
    def test_mouse_and_loadstring():
        lua.execute('''
            mousemoverel(15, -10)
            local mouseLoc = game:GetService("UserInputService"):GetMouseLocation()
            _mouse_x = mouseLoc.X
            _mouse_y = mouseLoc.Y
            
            local chunk = loadstring("return 40 + 2")
            _loadstring_res = chunk()
        ''')
        assert lua.eval('_mouse_x') == 960 + 15, "mousemoverel X mismatch"
        assert lua.eval('_mouse_y') == 540 - 10, "mousemoverel Y mismatch"
        assert lua.eval('_loadstring_res') == 42, "loadstring failed to execute"
    tests.append(("Executor Globals: mousemoverel, UserInputService, loadstring", test_mouse_and_loadstring))

    # -------------------------------------------------------------------------
    # Milestone 1 Fix Additions: task.spawn, typeof, GetMouse, and Services
    # -------------------------------------------------------------------------
    def test_m1_fix_additions():
        lua.execute('''
            -- task.spawn unpack check
            local task_executed = false
            task.spawn(function(a, b)
                if a == 10 and b == 20 then
                    task_executed = true
                end
            end, 10, 20)
            _task_ok = task_executed

            -- typeof check
            _typeof_inst = typeof(workspace)
            _typeof_v3 = typeof(Vector3.new(1, 2, 3))
            _typeof_v2 = typeof(Vector2.new(1, 2))
            _typeof_c3 = typeof(Color3.new(1, 0, 0))
            _typeof_num = typeof(123)

            -- LocalPlayer mouse check
            local mouse = game:GetService("Players").LocalPlayer:GetMouse()
            _mouse_hit_ok = (mouse.Hit ~= nil and mouse.X == 960 and mouse.Y == 540)
            _mouse_sig_ok = (mouse.Button1Down ~= nil and mouse.KeyDown ~= nil)

            -- PlayerGui check
            _playergui_ok = (game:GetService("Players").LocalPlayer.PlayerGui ~= nil)

            -- Thumbnail check
            local thumb, thumb_ok = game:GetService("Players"):GetUserThumbnailAsync(1, Enum.ThumbnailType.HeadShot, Enum.ThumbnailSize.Size48x48)
            _thumb_ok = (thumb_ok == true and thumb:find("rbxassetid") ~= nil)

            -- Service retrieval
            local rep = game:GetService("ReplicatedStorage")
            local cas = game:GetService("ContextActionService")
            _services_ok = (rep ~= nil and cas ~= nil and rep.Name == "ReplicatedStorage")

            -- Hierarchy check
            local folder = Instance.new("Folder")
            local part = Instance.new("Part", folder)
            _hierarchy_ok = part:IsDescendantOf(folder) and folder:IsAncestorOf(part)
        ''')
        assert lua.eval('_task_ok') == True, "task.spawn did not execute with arguments"
        assert lua.eval('_typeof_inst') == "Instance", f"typeof(workspace) failed: {lua.eval('_typeof_inst')}"
        assert lua.eval('_typeof_v3') == "Vector3", "typeof(Vector3) failed"
        assert lua.eval('_typeof_v2') == "Vector2", "typeof(Vector2) failed"
        assert lua.eval('_typeof_c3') == "Color3", "typeof(Color3) failed"
        assert lua.eval('_typeof_num') == "number", "typeof(number) failed"
        assert lua.eval('_mouse_hit_ok') == True, "mouse.Hit or position mismatch"
        assert lua.eval('_mouse_sig_ok') == True, "mouse signals missing"
        assert lua.eval('_playergui_ok') == True, "LocalPlayer.PlayerGui missing"
        assert lua.eval('_thumb_ok') == True, "GetUserThumbnailAsync failed"
        assert lua.eval('_services_ok') == True, "ReplicatedStorage or ContextActionService resolution failed"
        assert lua.eval('_hierarchy_ok') == True, "IsDescendantOf or IsAncestorOf failed"
    tests.append(("M1 Fix Engine Additions: task.spawn, typeof, GetMouse, Services, Hierarchy", test_m1_fix_additions))

    # Run all smoke tests
    print("=== DreezHub Mock Roblox Engine Smoke Test ===")
    passed = 0
    failed = 0
    errors = []

    for name, test_fn in tests:
        try:
            test_fn()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name} -> {e}")
            failed += 1
            errors.append(f"{name}: {e}")

    print("--------------------------------------------------")
    print(f"Smoke Test Results: {passed} passed, {failed} failed out of {len(tests)} tests.")
    return passed, failed, errors

def main():
    start_time = time.time()
    print("==================================================")
    print("           DreezHub Test Suite Runner             ")
    print("==================================================")
    
    # Step 1: Syntax Verification
    syntax_ok = scan_and_verify()
    if not syntax_ok:
        print("\n[ERROR] Syntax verification failed!")
        sys.exit(1)
        
    print("")
    # Step 2: Mock Engine Smoke Test
    passed, failed, errors = run_mock_engine_smoke_test()
    
    elapsed = time.time() - start_time
    print(f"\nCompleted all test runs in {elapsed:.2f} seconds.")
    
    if failed > 0:
        print(f"\n[ERROR] {failed} smoke tests failed:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    print("\n[SUCCESS] All syntax checks and mock engine smoke tests passed cleanly!")
    sys.exit(0)

if __name__ == "__main__":
    main()
