#!/usr/bin/env python3
"""
tests/test_challenger_m1.py
Empirical Challenger Test Suite for Milestone 1.
Tests:
  1. tests/mock_roblox.lua
     - CFrame multiplications (associativity, identity, composition, stress)
     - CFrame inverse calculations (cf * cf:Inverse() == Identity, precision drift)
     - WorldToViewportPoint edge cases (behind camera, near plane, center, outside FOV left/right/top/bottom)
     - Signal lifecycle & stress (1,000 rapid connects, disconnections in reverse order, re-entrant fire, idempotency)
  2. tests/verify_syntax.py
     - Valid Luau code (continue in for/while/repeat, continue in strings/comments, table fields)
     - Intentionally invalid Lua code (unclosed strings, syntax errors, missing ends, malformed expressions)
"""

import sys
import math
import tempfile
from pathlib import Path
import lupa

# Add tests directory to sys.path
TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

import verify_syntax

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.findings = []

    def record_pass(self, name: str):
        self.passed += 1
        print(f"  [PASS] {name}")

    def record_fail(self, name: str, reason: str):
        self.failed += 1
        print(f"  [FAIL] {name}: {reason}")
        self.findings.append({"test": name, "reason": reason})

def run_challenger_tests():
    results = TestResults()
    print("==================================================")
    print("      DreezHub Milestone 1 Challenger Tests       ")
    print("==================================================")

    # Load Lua VM with mock_roblox.lua
    mock_path = TESTS_DIR / "mock_roblox.lua"
    if not mock_path.exists():
        results.record_fail("Setup", f"mock_roblox.lua not found at {mock_path}")
        return results

    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    try:
        lua.execute(mock_path.read_text(encoding="utf-8"))
    except Exception as e:
        results.record_fail("Setup", f"Failed to execute mock_roblox.lua: {e}")
        return results

    # =========================================================================
    # PART 1: CFrame Multiplications & Inverses
    # =========================================================================
    print("\n--- [Suite 1] CFrame Multiplications & Inverses ---")

    # Define helper function in global Lua scope
    lua.execute("""
        function _close_cf(a, b, eps)
            eps = eps or 0.001
            local ax, ay, az, am00, am01, am02, am10, am11, am12, am20, am21, am22 = a:GetComponents()
            local bx, by, bz, bm00, bm01, bm02, bm10, bm11, bm12, bm20, bm21, bm22 = b:GetComponents()
            return math.abs(ax - bx) < eps and math.abs(ay - by) < eps and math.abs(az - bz) < eps
                and math.abs(am00 - bm00) < eps and math.abs(am01 - bm01) < eps and math.abs(am02 - bm02) < eps
                and math.abs(am10 - bm10) < eps and math.abs(am11 - bm11) < eps and math.abs(am12 - bm12) < eps
                and math.abs(am20 - bm20) < eps and math.abs(am21 - bm21) < eps and math.abs(am22 - bm22) < eps
        end
    """)

    # Test 1.1: Identity multiplication
    try:
        lua.execute("""
            local cf = CFrame.new(12, -45, 78) * CFrame.Angles(0.5, -0.2, 1.1)
            local ident = CFrame.new()
            local cf_ident = cf * ident
            local ident_cf = ident * cf
            _cf_ident_pass = _close_cf(cf, cf_ident) and _close_cf(cf, ident_cf)
        """)
        if lua.eval("_cf_ident_pass"):
            results.record_pass("CFrame identity multiplication (cf * ident == ident * cf == cf)")
        else:
            results.record_fail("CFrame identity multiplication", "Identity multiplication deviated from original CFrame")
    except Exception as e:
        results.record_fail("CFrame identity multiplication", str(e))

    # Test 1.2: Associativity (A * B) * C == A * (B * C)
    try:
        lua.execute("""
            local a = CFrame.new(5, 10, -3) * CFrame.Angles(0.3, 0.4, 0.1)
            local b = CFrame.new(-2, 7, 15) * CFrame.Angles(-0.5, 0.2, -0.8)
            local c = CFrame.new(100, -50, 25) * CFrame.Angles(1.0, -1.0, 0.5)
            
            local left = (a * b) * c
            local right = a * (b * c)
            _cf_assoc_pass = _close_cf(left, right, 0.005)
        """)
        if lua.eval("_cf_assoc_pass"):
            results.record_pass("CFrame associativity ((A * B) * C == A * (B * C))")
        else:
            results.record_fail("CFrame associativity", "Multiplication is not associative")
    except Exception as e:
        results.record_fail("CFrame associativity", str(e))

    # Test 1.3: CFrame Inverse Cancellation (cf * cf:Inverse() == Identity)
    try:
        lua.execute("""
            local ident = CFrame.new()
            local cf_cases = {
                CFrame.new(10, 20, 30),
                CFrame.new(-100, 250, -50) * CFrame.Angles(math.rad(45), math.rad(30), math.rad(60)),
                CFrame.new(0, 0, 0) * CFrame.Angles(math.rad(90), 0, math.rad(180)),
                CFrame.lookAt(Vector3.new(15, 20, 30), Vector3.new(50, -10, 100))
            }
            _cf_inv_pass = true
            for _, cf in ipairs(cf_cases) do
                local inv = cf:Inverse()
                local prod1 = cf * inv
                local prod2 = inv * cf
                if not _close_cf(prod1, ident, 0.005) or not _close_cf(prod2, ident, 0.005) then
                    _cf_inv_pass = false
                    break
                end
            end
        """)
        if lua.eval("_cf_inv_pass"):
            results.record_pass("CFrame inverse cancellation (cf * cf:Inverse() == Identity)")
        else:
            results.record_fail("CFrame inverse cancellation", "cf * cf:Inverse() did not produce identity matrix")
    except Exception as e:
        results.record_fail("CFrame inverse cancellation", str(e))

    # Test 1.4: Inverse of product (A * B):Inverse() == B:Inverse() * A:Inverse()
    try:
        lua.execute("""
            local a = CFrame.new(10, -5, 2) * CFrame.Angles(0.2, -0.4, 0.6)
            local b = CFrame.new(-8, 14, 20) * CFrame.Angles(-0.1, 0.5, -0.3)
            local inv_prod = (a * b):Inverse()
            local prod_inv = b:Inverse() * a:Inverse()
            _cf_inv_prod_pass = _close_cf(inv_prod, prod_inv, 0.005)
        """)
        if lua.eval("_cf_inv_prod_pass"):
            results.record_pass("CFrame inverse of product ((A * B):Inverse() == B:Inverse() * A:Inverse())")
        else:
            results.record_fail("CFrame inverse of product", "Inverse of product does not equal reverse product of inverses")
    except Exception as e:
        results.record_fail("CFrame inverse of product", str(e))

    # Test 1.5: High-Stress Chained CFrame Multiplications (100 successive steps)
    try:
        lua.execute("""
            local step = CFrame.new(1, 0.5, -0.2) * CFrame.Angles(0.01, 0.02, -0.01)
            local step_inv = step:Inverse()
            local current = CFrame.new(0, 0, 0)
            for i = 1, 100 do
                current = current * step
            end
            for i = 1, 100 do
                current = current * step_inv
            end
            _stress_cf_pass = _close_cf(current, CFrame.new(), 0.1)
        """)
        if lua.eval("_stress_cf_pass"):
            results.record_pass("CFrame stress: 100 forward and 100 inverse chained multiplications with drift check")
        else:
            results.record_fail("CFrame stress", "Cumulative floating point drift or matrix distortion after 100 chained steps")
    except Exception as e:
        results.record_fail("CFrame stress", str(e))

    # Test 1.6: 12-argument CFrame constructor with full rotation matrix
    try:
        lua.execute("""
            -- 90 deg rotation around Z: R00=0, R01=-1, R02=0, R10=1, R11=0, R12=0, R20=0, R21=0, R22=1
            local cf_12 = CFrame.new(10, 20, 30, 0, -1, 0, 1, 0, 0, 0, 0, 1)
            local x, y, z, m00, m01, m02, m10, m11, m12, m20, m21, m22 = cf_12:GetComponents()
            _cf_12_has_rotation = (m01 == -1 and m10 == 1)
        """)
        if lua.eval("_cf_12_has_rotation"):
            results.record_pass("CFrame 12-argument constructor: Correctly preserved full rotation matrix components")
        else:
            results.record_fail("CFrame 12-argument constructor",
                "Defect: CFrame.new(x,y,z, r00..r22) silently discarded rotation matrix arguments and defaulted to identity")
    except Exception as e:
        results.record_fail("CFrame 12-argument constructor", str(e))

    # =========================================================================
    # PART 2: Camera WorldToViewportPoint Edge Cases
    # =========================================================================
    print("\n--- [Suite 2] Camera WorldToViewportPoint Edge Cases ---")

    # Test 2.1: Point in front of camera (center of screen)
    try:
        lua.execute("""
            local cam = workspace.CurrentCamera
            cam.CFrame = CFrame.new(0, 5, 20)
            cam.FieldOfView = 70
            cam.ViewportSize = Vector2.new(1920, 1080)
            
            -- Look vector is (0, 0, -1) by default when CFrame.new(0, 5, 20)
            local centerWorld = cam.CFrame.Position + cam.CFrame.LookVector * 10
            local screenPos, onScreen = cam:WorldToViewportPoint(centerWorld)
            _w2v_center_onScreen = onScreen
            _w2v_center_x = screenPos.X
            _w2v_center_y = screenPos.Y
            _w2v_center_z = screenPos.Z
        """)
        center_on = lua.eval("_w2v_center_onScreen")
        cx = lua.eval("_w2v_center_x")
        cy = lua.eval("_w2v_center_y")
        cz = lua.eval("_w2v_center_z")
        if center_on and abs(cx - 960) < 5 and abs(cy - 540) < 5 and abs(cz - 10) < 0.1:
            results.record_pass("WorldToViewportPoint: Center point in front (depth=10, screen=(960, 540), onScreen=true)")
        else:
            results.record_fail("WorldToViewportPoint: Center point", f"Expected (960, 540, 10, true), got ({cx}, {cy}, {cz}, {center_on})")
    except Exception as e:
        results.record_fail("WorldToViewportPoint: Center point", str(e))

    # Test 2.2: Point behind camera (depth < 0)
    try:
        lua.execute("""
            local cam = workspace.CurrentCamera
            cam.CFrame = CFrame.new(0, 0, 0)
            -- Camera looks towards -Z. Point at +Z is behind camera.
            local behindWorld = Vector3.new(0, 0, 50)
            local screenPos, onScreen = cam:WorldToViewportPoint(behindWorld)
            _w2v_behind_onScreen = onScreen
            _w2v_behind_z = screenPos.Z
        """)
        behind_on = lua.eval("_w2v_behind_onScreen")
        behind_z = lua.eval("_w2v_behind_z")
        if not behind_on and behind_z < 0:
            results.record_pass("WorldToViewportPoint: Point behind camera (rel.Z=50, depth=-50, onScreen=false)")
        else:
            results.record_fail("WorldToViewportPoint: Point behind camera", f"Expected onScreen=false and depth < 0, got onScreen={behind_on}, depth={behind_z}")
    except Exception as e:
        results.record_fail("WorldToViewportPoint: Point behind camera", str(e))

    # Test 2.3: Point on near plane / zero depth
    try:
        lua.execute("""
            local cam = workspace.CurrentCamera
            cam.CFrame = CFrame.new(0, 0, 0)
            -- Point at (0, 0, 0)
            local planeWorld = Vector3.new(0, 0, 0)
            local screenPos, onScreen = cam:WorldToViewportPoint(planeWorld)
            _w2v_plane_onScreen = onScreen
        """)
        plane_on = lua.eval("_w2v_plane_onScreen")
        if not plane_on:
            results.record_pass("WorldToViewportPoint: Point at camera position (depth=0, onScreen=false)")
        else:
            results.record_fail("WorldToViewportPoint: Point at camera position", f"Expected onScreen=false, got {plane_on}")
    except Exception as e:
        results.record_fail("WorldToViewportPoint: Point at camera position", str(e))

    # Test 2.4: Point in front of camera BUT outside FOV (far to the right)
    # IN ROBLOX: Camera:WorldToViewportPoint returns onScreen = FALSE when point is outside screen bounds!
    try:
        lua.execute("""
            local cam = workspace.CurrentCamera
            cam.CFrame = CFrame.new(0, 0, 0)
            cam.FieldOfView = 70
            cam.ViewportSize = Vector2.new(1920, 1080)
            -- Camera looks towards -Z. Point at depth=10 (Z=-10), but X=10000 (far right)
            local farRightWorld = Vector3.new(10000, 0, -10)
            local screenPos, onScreen = cam:WorldToViewportPoint(farRightWorld)
            _w2v_farRight_onScreen = onScreen
            _w2v_farRight_x = screenPos.X
            _w2v_farRight_y = screenPos.Y
        """)
        fr_on = lua.eval("_w2v_farRight_onScreen")
        fr_x = lua.eval("_w2v_farRight_x")
        fr_y = lua.eval("_w2v_farRight_y")
        # In Roblox, onScreen must be false because screenX is thousands of pixels off screen!
        if fr_on is False:
            results.record_pass("WorldToViewportPoint: Outside FOV horizontally (X=10000, depth=10, onScreen=false)")
        else:
            results.record_fail("WorldToViewportPoint: Outside FOV horizontally",
                f"Defect: onScreen is TRUE for point far outside viewport (screenX={fr_x:.1f}, screenY={fr_y:.1f}, bounds=(0..1920, 0..1080))")
    except Exception as e:
        results.record_fail("WorldToViewportPoint: Outside FOV horizontally", str(e))

    # Test 2.5: Point in front of camera BUT outside FOV (far above)
    try:
        lua.execute("""
            local cam = workspace.CurrentCamera
            cam.CFrame = CFrame.new(0, 0, 0)
            cam.FieldOfView = 70
            cam.ViewportSize = Vector2.new(1920, 1080)
            local farAboveWorld = Vector3.new(0, 10000, -10)
            local screenPos, onScreen = cam:WorldToViewportPoint(farAboveWorld)
            _w2v_farAbove_onScreen = onScreen
            _w2v_farAbove_y = screenPos.Y
        """)
        fa_on = lua.eval("_w2v_farAbove_onScreen")
        fa_y = lua.eval("_w2v_farAbove_y")
        if fa_on is False:
            results.record_pass("WorldToViewportPoint: Outside FOV vertically (Y=10000, depth=10, onScreen=false)")
        else:
            results.record_fail("WorldToViewportPoint: Outside FOV vertically",
                f"Defect: onScreen is TRUE for point far above viewport (screenY={fa_y:.1f}, bounds=(0..1080))")
    except Exception as e:
        results.record_fail("WorldToViewportPoint: Outside FOV vertically", str(e))

    # =========================================================================
    # PART 3: Signal Lifecycle & Stress
    # =========================================================================
    print("\n--- [Suite 3] Signal Lifecycle & Stress ---")

    # Test 3.1: 1,000 rapid connects, verify all fire, disconnect in reverse order
    try:
        lua.execute("""
            local sig = MockRoblox.createSignal()
            local total_fired = 0
            local connections = {}
            for i = 1, 1000 do
                local conn = sig:Connect(function()
                    total_fired = total_fired + 1
                end)
                table.insert(connections, conn)
            end
            sig:Fire()
            _sig_1000_fired = total_fired
            
            -- Disconnect all 1000 in reverse order
            for i = #connections, 1, -1 do
                connections[i]:Disconnect()
            end
            total_fired = 0
            sig:Fire()
            _sig_1000_after_disconn = total_fired
            _sig_1000_remaining_listeners = #sig._listeners
        """)
        f1 = lua.eval("_sig_1000_fired")
        f2 = lua.eval("_sig_1000_after_disconn")
        rem = lua.eval("_sig_1000_remaining_listeners")
        if f1 == 1000 and f2 == 0 and rem == 0:
            results.record_pass("Signal: 1,000 connections created, fired, and disconnected in reverse order (all listeners cleaned)")
        else:
            results.record_fail("Signal: 1,000 connections", f"f1={f1} (expected 1000), f2={f2} (expected 0), listeners_remaining={rem} (expected 0)")
    except Exception as e:
        results.record_fail("Signal: 1,000 connections", str(e))

    # Test 3.2: Rapid alternating connect/disconnect in tight loop (10,000 iterations)
    try:
        lua.execute("""
            local sig = MockRoblox.createSignal()
            local fired_count = 0
            for i = 1, 10000 do
                local c = sig:Connect(function() fired_count = fired_count + 1 end)
                if i % 2 == 0 then
                    c:Disconnect()
                end
            end
            sig:Fire()
            _sig_alternating_fired = fired_count
            _sig_alternating_listeners = #sig._listeners
        """)
        f_alt = lua.eval("_sig_alternating_fired")
        l_alt = lua.eval("_sig_alternating_listeners")
        if f_alt == 5000 and l_alt == 5000:
            results.record_pass("Signal: 10,000 alternating connect/disconnect in tight loop (5,000 remaining active)")
        else:
            results.record_fail("Signal: 10,000 alternating loop", f"Fired={f_alt} (expected 5000), listeners={l_alt} (expected 5000)")
    except Exception as e:
        results.record_fail("Signal: 10,000 alternating loop", str(e))

    # Test 3.3: Re-entrant Signal Fire: Listener disconnects self during Fire
    try:
        lua.execute("""
            local sig = MockRoblox.createSignal()
            local order = {}
            local conn1, conn2
            conn1 = sig:Connect(function()
                table.insert(order, 1)
                conn1:Disconnect()
            end)
            conn2 = sig:Connect(function()
                table.insert(order, 2)
            end)
            sig:Fire()
            sig:Fire()
            _sig_reentrant_order = table.concat(order, ",")
        """)
        order = lua.eval("_sig_reentrant_order")
        # In fire 1: 1 fires, disconnects self, 2 fires.
        # In fire 2: 1 is disconnected, only 2 fires.
        # Expected order: "1,2,2"
        if order == "1,2,2":
            results.record_pass("Signal re-entrancy: Listener disconnects self during Fire (subsequent Fire excludes it)")
        else:
            results.record_fail("Signal re-entrancy: Listener self-disconnect", f"Expected order '1,2,2', got '{order}'")
    except Exception as e:
        results.record_fail("Signal re-entrancy: Listener self-disconnect", str(e))

    # Test 3.4: Re-entrant Signal Fire: Listener connects another listener during Fire
    try:
        lua.execute("""
            local sig = MockRoblox.createSignal()
            local order = {}
            sig:Connect(function()
                table.insert(order, "A")
                sig:Connect(function()
                    table.insert(order, "B")
                end)
            end)
            sig:Fire() -- Fire 1: A fires and adds B; B should NOT fire in this same Fire call
            _sig_fire1_order = table.concat(order, ",")
            sig:Fire() -- Fire 2: A fires and adds another B; original B also fires
            _sig_fire2_order = table.concat(order, ",")
        """)
        f1_order = lua.eval("_sig_fire1_order")
        f2_order = lua.eval("_sig_fire2_order")
        if f1_order == "A" and "B" in f2_order:
            results.record_pass("Signal re-entrancy: Listener connected during Fire does not execute until next Fire")
        else:
            results.record_fail("Signal re-entrancy: Listener connected during Fire", f"Fire 1 gave '{f1_order}', expected 'A'")
    except Exception as e:
        results.record_fail("Signal re-entrancy: Listener connected during Fire", str(e))

    # Test 3.5: Idempotent Disconnect() calls
    try:
        lua.execute("""
            local sig = MockRoblox.createSignal()
            local conn = sig:Connect(function() end)
            local ok1 = pcall(function() conn:Disconnect() end)
            local ok2 = pcall(function() conn:Disconnect() end)
            local ok3 = pcall(function() conn:Disconnect() end)
            _sig_idempotent = ok1 and ok2 and ok3 and (#sig._listeners == 0)
        """)
        if lua.eval("_sig_idempotent"):
            results.record_pass("Signal: Multiple Disconnect() calls are safely idempotent (no error, listeners remain 0)")
        else:
            results.record_fail("Signal: Multiple Disconnect() calls", "Error thrown or listener list corrupted on repeated Disconnect()")
    except Exception as e:
        results.record_fail("Signal: Multiple Disconnect() calls", str(e))

    # Test 3.6: Error isolation across signal listeners (Roblox behavior: one failing listener does not abort others)
    try:
        lua.execute("""
            local sig = MockRoblox.createSignal()
            local second_fired = false
            sig:Connect(function()
                error("Simulated callback failure")
            end)
            sig:Connect(function()
                second_fired = true
            end)
            pcall(function() sig:Fire() end)
            _sig_error_isolation = second_fired
        """)
        if lua.eval("_sig_error_isolation"):
            results.record_pass("Signal: Error isolation (failing listener did not abort subsequent listeners)")
        else:
            results.record_fail("Signal: Error isolation",
                "Defect: Listener error aborted sig:Fire() iteration; subsequent listeners were starved")
    except Exception as e:
        results.record_fail("Signal: Error isolation", str(e))

    # =========================================================================
    # PART 4: verify_syntax.py AST Validator Probes
    # =========================================================================
    print("\n--- [Suite 4] verify_syntax.py AST Validator Probes ---")

    # Helper function to test verify_file
    def check_code(code_str: str) -> tuple[bool, str]:
        with tempfile.NamedTemporaryFile("w", suffix=".lua", delete=False, encoding="utf-8") as f:
            f.write(code_str)
            tpath = Path(f.name)
        try:
            return verify_syntax.verify_file(tpath)
        finally:
            tpath.unlink(missing_ok=True)

    # Test 4.1: Valid standard Lua 5.1 constructs
    valid_lua_samples = [
        ("Functions, closures & varargs", "local function add(a, ...) local s = a for _, v in ipairs({...}) do s = s + v end return s end"),
        ("Metatables & OOP", "local MT = {} MT.__index = MT function MT.new(v) return setmetatable({val = v}, MT) end"),
        ("Repeat-until & conditionals", "local x = 10 repeat x = x - 1 until x == 0 if x == 0 then x = 1 else x = 2 end"),
        ("Multiline strings & comments", "--[[ Block comment ]]\nlocal str = [[ Multiline \n text ]]\n-- line comment"),
    ]
    for desc, code in valid_lua_samples:
        ok, msg = check_code(code)
        if ok:
            results.record_pass(f"verify_syntax (Valid): {desc}")
        else:
            results.record_fail(f"verify_syntax (Valid): {desc}", f"False positive syntax error: {msg}")

    # Test 4.2: Valid Luau continue constructs
    valid_luau_samples = [
        ("continue in numeric for loop", "for i = 1, 10 do if i % 2 == 0 then continue end print(i) end"),
        ("continue in generic for loop", "for k, v in pairs({a=1, b=2}) do if k == 'a' then continue end end"),
        ("continue in while loop", "local i = 0 while i < 5 do i = i + 1 if i == 3 then continue end end"),
        ("continue in repeat-until loop", "local i = 0 repeat i = i + 1 if i == 2 then continue end until i == 5"),
    ]
    for desc, code in valid_luau_samples:
        ok, msg = check_code(code)
        if ok:
            results.record_pass(f"verify_syntax (Valid Luau): {desc}")
        else:
            results.record_fail(f"verify_syntax (Valid Luau): {desc}", f"Failed to handle valid Luau continue: {msg}")

    # Test 4.3: Edge case: "continue" as substring or identifier in valid code
    edge_case_samples = [
        ("Variable named continue_count", "local continue_count = 10\nprint(continue_count)"),
        ("String literal containing word continue", 'local msg = "Press continue to start playing"\nlocal log = "continue"'),
        ("Table field access with continue: tbl.continue", 'local tbl = {}\ntbl.continue = 123'),
        ("Function named continueAction", 'local function continueAction() return true end'),
    ]
    for desc, code in edge_case_samples:
        ok, msg = check_code(code)
        if ok:
            results.record_pass(f"verify_syntax (Edge Case): {desc}")
        else:
            results.record_fail(f"verify_syntax (Edge Case): {desc}", f"False positive on identifier/string with 'continue': {msg}")

    # Test 4.4: Intentionally invalid Lua code (Must be detected as invalid!)
    invalid_samples = [
        ("Missing function end", "local function broken()\n    local x = 1\n-- missing end"),
        ("Unclosed string literal", 'local broken_str = "hello world\nprint(broken_str)'),
        ("Invalid token character", 'local x = 10 @@ 20'),
        ("Missing then in if statement", 'if x == 1\n    print("no then")\nend'),
        ("Invalid assignment target", '123 = local_var'),
        ("Malformed binary expression", 'local res = 10 + * 20'),
        ("Mismatched parentheses", 'local val = ((10 + 20) * 3'),
    ]
    for desc, code in invalid_samples:
        ok, msg = check_code(code)
        if not ok:
            results.record_pass(f"verify_syntax (Catch Invalid): {desc} correctly rejected ({msg[:40]}...)")
        else:
            results.record_fail(f"verify_syntax (Catch Invalid): {desc}", "False negative! Invalid code was reported as OK")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n==================================================")
    print(f"Challenger Test Results: {results.passed} passed, {results.failed} failed.")
    print("==================================================")
    return results

if __name__ == "__main__":
    res = run_challenger_tests()
    sys.exit(0 if res.failed == 0 else 1)
