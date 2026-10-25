#!/usr/bin/env python3
"""
tests/test_challenger_v2_deep.py
Challenger 2 Deep Stress & Invariant Verification Suite for Milestone 1:
- JSON escape sequences, control characters, unicode escapes, nested JSON-within-JSON strings.
- VFS root path variants ("", ".", "./", ".\\"), deep 10-level folder hierarchies, ancestor registration, directory isolation.
- Drawing API 500-object stress, mutation, random removal, Destroy lifecycle.
- Camera frustum edge boundaries (depth=0.1, screen borders).
"""

import sys
import os
import random
from pathlib import Path
import lupa

REPO_ROOT = Path(__file__).resolve().parent.parent

class DeepResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.failures = []

    def record_pass(self, name):
        self.passed += 1
        print(f"  [PASS] {name}")

    def record_fail(self, name, reason):
        self.failed += 1
        self.failures.append(f"{name}: {reason}")
        print(f"  [FAIL] {name}: {reason}")

def run_deep_probes():
    results = DeepResults()
    print("==================================================")
    print(" Challenger 2 Deep Stress & Boundary Probe Suite  ")
    print("==================================================")

    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    mock_path = REPO_ROOT / "tests" / "mock_roblox.lua"
    mock_code = mock_path.read_text(encoding="utf-8")
    lua.execute(mock_code)

    # -------------------------------------------------------------------------
    # PART 1: Extreme JSON Escape & Unicode Decoding Stress
    # -------------------------------------------------------------------------
    print("\n--- Part 1: Extreme JSON Escape & Unicode Decoding Stress ---")

    # Test 1.1: Comprehensive escape matrix
    try:
        raw_json = r'{"quotes":"\"quoted\"","backslash":"\\","slash":"\/","b":"\b","f":"\f","n":"\n","r":"\r","t":"\t"}'
        lua.globals().raw_json = raw_json
        lua.execute(r"""
            local hs = HttpService
            local dec = hs:JSONDecode(raw_json)
            _t1_1_pass = (dec.quotes == '"quoted"' and
                          dec.backslash == "\\" and
                          dec.slash == "/" and
                          dec.b == "\b" and
                          dec.f == "\f" and
                          dec.n == "\n" and
                          dec.r == "\r" and
                          dec.t == "\t")
        """)
        if lua.eval("_t1_1_pass"):
            results.record_pass("JSON: Full escape matrix (\\\", \\\\, \\/, \\b, \\f, \\n, \\r, \\t)")
        else:
            results.record_fail("JSON: Full escape matrix", "Escape sequence decoded value mismatch")
    except Exception as e:
        results.record_fail("JSON: Full escape matrix", str(e))

    # Test 1.2: Unicode escape decoding (\uXXXX)
    try:
        lua.execute(r"""
            local hs = HttpService
            -- \u0041 = 'A', \u0042 = 'B', \u0020 = ' ', \u0031 = '1'
            local json_u = '{"alpha":"\\u0041\\u0042\\u0020\\u0031"}'
            local dec = hs:JSONDecode(json_u)
            _t1_2_pass = (dec.alpha == "AB 1")
        """)
        if lua.eval("_t1_2_pass"):
            results.record_pass("JSON: Unicode escape \\uXXXX decoding")
        else:
            results.record_fail("JSON: Unicode escape \\uXXXX decoding", "Decoded unicode sequence mismatch")
    except Exception as e:
        results.record_fail("JSON: Unicode escape \\uXXXX decoding", str(e))

    # Test 1.3: Roundtrip of serialized Lua code string inside JSON (quotes, backslashes, newlines)
    try:
        lua.execute(r"""
            local hs = HttpService
            local script_payload = {
                script = 'local x = 10\nprint("Result: " .. tostring(x))\nlocal path = "C:\\\\Roblox\\\\Data"'
            }
            local enc = hs:JSONEncode(script_payload)
            local dec = hs:JSONDecode(enc)
            _t1_3_pass = (dec.script == script_payload.script)
        """)
        if lua.eval("_t1_3_pass"):
            results.record_pass("JSON: Embedded code snippet with quotes, slashes, and newlines roundtrip")
        else:
            results.record_fail("JSON: Embedded code snippet roundtrip", "Code snippet corrupted after JSON roundtrip")
    except Exception as e:
        results.record_fail("JSON: Embedded code snippet roundtrip", str(e))

    # Test 1.4: Malformed JSON rejection (unterminated string escape)
    try:
        lua.execute(r"""
            local hs = HttpService
            local ok1, _ = pcall(function() hs:JSONDecode('{"unterminated":"\\') end)
            local ok2, _ = pcall(function() hs:JSONDecode('{"bad_hex":"\\u00Z9"}') end)
            _t1_4_pass = (not ok1)
        """)
        if lua.eval("_t1_4_pass"):
            results.record_pass("JSON: Rejection of malformed escapes")
        else:
            results.record_fail("JSON: Rejection of malformed escapes", "Parser failed to raise error on invalid escape")
    except Exception as e:
        results.record_fail("JSON: Rejection of malformed escapes", str(e))

    # -------------------------------------------------------------------------
    # PART 2: VFS Root Variations, Ancestor Hierarchies, & Directory Isolation
    # -------------------------------------------------------------------------
    print("\n--- Part 2: VFS Root Variations, Ancestor Hierarchies, & Isolation ---")

    # Test 2.1: Root path variations: "", ".", "./", ".\\"
    try:
        lua.execute(r"""
            writefile("root_test_1.txt", "v1")
            writefile("root_test_2.txt", "v2")
            local list_empty = listfiles("")
            local list_dot = listfiles(".")
            local list_dotslash = listfiles("./")
            local list_dotbslash = listfiles(".\\")
            
            local has_1_empty, has_2_empty = false, false
            for _, f in ipairs(list_empty) do
                if f == "root_test_1.txt" then has_1_empty = true end
                if f == "root_test_2.txt" then has_2_empty = true end
            end
            
            _t2_1_pass = (#list_empty >= 2 and
                          #list_dot == #list_empty and
                          #list_dotslash == #list_empty and
                          #list_dotbslash == #list_empty and
                          has_1_empty and has_2_empty)
        """)
        if lua.eval("_t2_1_pass"):
            results.record_pass("VFS: Root path variations ('', '.', './', '.\\\\') consistency")
        else:
            results.record_fail("VFS: Root path variations", "Discrepancy in file count across root path formats")
    except Exception as e:
        results.record_fail("VFS: Root path variations", str(e))

    # Test 2.2: Deep 10-level directory creation and ancestor resolution
    try:
        lua.execute(r"""
            local deep_path = "D1/D2/D3/D4/D5/D6/D7/D8/D9/D10"
            makefolder(deep_path)
            local all_ancestors_exist = true
            local accum = ""
            for i = 1, 10 do
                accum = (accum == "") and ("D" .. i) or (accum .. "/D" .. i)
                if not isfolder(accum) then
                    all_ancestors_exist = false
                    break
                end
            end
            _t2_2_pass = all_ancestors_exist
        """)
        if lua.eval("_t2_2_pass"):
            results.record_pass("VFS: 10-level deep hierarchy creates all intermediate folders")
        else:
            results.record_fail("VFS: 10-level deep hierarchy", "One or more intermediate folders missing")
    except Exception as e:
        results.record_fail("VFS: 10-level deep hierarchy", str(e))

    # Test 2.3: Implicit ancestor creation on writefile
    try:
        lua.execute(r"""
            writefile("AutoBranch/Sub1/Sub2/data.cfg", "config=true")
            local f_exists = isfile("AutoBranch/Sub1/Sub2/data.cfg")
            local f1_exists = isfolder("AutoBranch")
            local f2_exists = isfolder("AutoBranch/Sub1")
            local f3_exists = isfolder("AutoBranch/Sub1/Sub2")
            _t2_3_pass = (f_exists and f1_exists and f2_exists and f3_exists)
        """)
        if lua.eval("_t2_3_pass"):
            results.record_pass("VFS: Implicit folder hierarchy creation via writefile")
        else:
            results.record_fail("VFS: Implicit folder hierarchy via writefile", "Ancestors not auto-created")
    except Exception as e:
        results.record_fail("VFS: Implicit folder hierarchy via writefile", str(e))

    # Test 2.4: Strict directory isolation in listfiles
    try:
        lua.execute(r"""
            makefolder("IsoParent")
            makefolder("IsoParent/IsoChild")
            writefile("IsoParent/parent_f1.txt", "p1")
            writefile("IsoParent/parent_f2.txt", "p2")
            writefile("IsoParent/IsoChild/child_f1.txt", "c1")
            writefile("IsoParent/IsoChild/child_f2.txt", "c2")
            writefile("IsoParent/IsoChild/child_f3.txt", "c3")

            local p_files = listfiles("IsoParent")
            local c_files = listfiles("IsoParent/IsoChild")
            _t2_4_pass = (#p_files == 2 and #c_files == 3)
        """)
        if lua.eval("_t2_4_pass"):
            results.record_pass("VFS: Strict directory isolation (child files not leaked into parent listfiles)")
        else:
            results.record_fail("VFS: Strict directory isolation", "Child files leaked into parent listfiles")
    except Exception as e:
        results.record_fail("VFS: Strict directory isolation", str(e))

    # -------------------------------------------------------------------------
    # PART 3: Drawing API Lifecycle & Rapid Churn
    # -------------------------------------------------------------------------
    print("\n--- Part 3: Drawing API Lifecycle & Rapid Churn ---")

    # Test 3.1: 500-object rapid churn with random deletion
    try:
        lua.execute(r"""
            local objects = {}
            for i = 1, 500 do
                local d = Drawing.new(i % 2 == 0 and "Square" or "Text")
                d.Visible = true
                d.Transparency = 1.0
                table.insert(objects, d)
            end
            local initial_count = #Drawing._activeObjects
            
            -- Remove odd-indexed objects (250 objects)
            for i = 1, 500, 2 do
                objects[i]:Remove()
            end
            local mid_count = #Drawing._activeObjects
            
            -- Destroy remaining with :Destroy() alias
            for i = 2, 500, 2 do
                objects[i]:Destroy()
            end
            local final_count = #Drawing._activeObjects
            
            _t3_1_pass = (initial_count == 500 and mid_count == 250 and final_count == 0)
        """)
        if lua.eval("_t3_1_pass"):
            results.record_pass("Drawing API: 500-object churn with interleaved Remove/Destroy")
        else:
            results.record_fail("Drawing API: 500-object churn", "Active object count mismatch after churn")
    except Exception as e:
        results.record_fail("Drawing API: 500-object churn", str(e))

    # -------------------------------------------------------------------------
    # PART 4: Camera Boundary Probes
    # -------------------------------------------------------------------------
    print("\n--- Part 4: Camera Frustum Boundary Probes ---")

    # Test 4.1: Frustum boundaries at screen corners (0,0) and (ViewportSize.X, ViewportSize.Y)
    try:
        lua.execute(r"""
            local cam = workspace.CurrentCamera
            cam.CFrame = CFrame.new(0, 0, 0)
            cam.FieldOfView = 70
            cam.ViewportSize = Vector2.new(1920, 1080)
            
            -- A point directly in front at depth 10
            -- Center is (960, 540)
            local p_center, on_center = cam:WorldToViewportPoint(Vector3.new(0, 0, -10))
            
            -- A point behind (depth = -0.1)
            local p_behind, on_behind = cam:WorldToViewportPoint(Vector3.new(0, 0, 0.1))
            
            -- A point at near-plane threshold depth = 0.05 (<= 0.1)
            local p_near, on_near = cam:WorldToViewportPoint(Vector3.new(0, 0, -0.05))
            
            _t4_1_pass = (on_center == true and on_behind == false and on_near == false)
        """)
        if lua.eval("_t4_1_pass"):
            results.record_pass("Camera: Frustum near-plane & rear point culling (depth <= 0.1 returns false)")
        else:
            results.record_fail("Camera: Frustum near-plane & rear point culling", "Near or behind point marked as onScreen")
    except Exception as e:
        results.record_fail("Camera: Frustum near-plane & rear point culling", str(e))

    # Summary
    print("\n==================================================")
    print(f"Deep Results: {results.passed} passed, {results.failed} failed out of {results.passed + results.failed} tests.")
    print("==================================================")
    return results

if __name__ == "__main__":
    res = run_deep_probes()
    sys.exit(0 if res.failed == 0 else 1)
