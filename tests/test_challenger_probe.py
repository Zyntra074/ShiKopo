#!/usr/bin/env python3
"""
tests/test_challenger_probe.py
Adversarial stress harness for mock Roblox engine:
1. HttpService:JSONEncode / JSONDecode deep nesting, primitives, Unicode, syntax error rejection, and string escape character fidelity.
2. VFS (writefile, readfile, listfiles, delfile, makefolder, isfile, isfolder) path normalization, isolation, 100-file stress, 100KB payload roundtrip.
3. Drawing API lifecycle: 50 object allocation across all types (Square, Text, Line, Circle), multi-property mutation, partial removal invariance, double-removal safety, :Destroy() alias, and rapid 200-object churn.
"""

import sys
import os
from pathlib import Path
import lupa

REPO_ROOT = Path(__file__).resolve().parent.parent

class ProbeResults:
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

def run_challenger_probes():
    results = ProbeResults()
    print("==================================================")
    print("   DreezHub Challenger 2 Adversarial Probe Suite  ")
    print("==================================================")

    # Initialize Lupa environment
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    mock_path = REPO_ROOT / "tests" / "mock_roblox.lua"
    mock_code = mock_path.read_text(encoding="utf-8")
    lua.execute(mock_code)

    # =========================================================================
    # Suite 1: HttpService JSON Serialization & Parsing
    # =========================================================================
    print("\n--- Suite 1: HttpService JSON Serialization & Parsing ---")

    # JSON 1.1: Primitive types roundtrip
    try:
        lua.execute("""
            local hs = HttpService
            local payload = {
                num = 42.5,
                int = 100,
                negative = -17,
                str = "hello world",
                bool_true = true,
                bool_false = false
            }
            local encoded = hs:JSONEncode(payload)
            local decoded = hs:JSONDecode(encoded)
            _json_1_1_pass = (decoded.num == 42.5 and decoded.int == 100 and decoded.negative == -17 and decoded.str == "hello world" and decoded.bool_true == true and decoded.bool_false == false)
        """)
        if lua.eval("_json_1_1_pass"):
            results.record_pass("JSON 1.1: Primitive types roundtrip")
        else:
            results.record_fail("JSON 1.1: Primitive types roundtrip", "Decoded values do not match original")
    except Exception as e:
        results.record_fail("JSON 1.1: Primitive types roundtrip", str(e))

    # JSON 1.2: 5-level deep nesting fidelity
    try:
        lua.execute("""
            local hs = HttpService
            local deep = { l1 = { l2 = { l3 = { l4 = { l5 = "deep_value" } } } } }
            local enc = hs:JSONEncode(deep)
            local dec = hs:JSONDecode(enc)
            _json_1_2_pass = (dec.l1 and dec.l1.l2 and dec.l1.l2.l3 and dec.l1.l2.l3.l4 and dec.l1.l2.l3.l4.l5 == "deep_value")
        """)
        if lua.eval("_json_1_2_pass"):
            results.record_pass("JSON 1.2: 5-level deep nesting fidelity")
        else:
            results.record_fail("JSON 1.2: 5-level deep nesting fidelity", "Failed to preserve 5-level hierarchy")
    except Exception as e:
        results.record_fail("JSON 1.2: 5-level deep nesting fidelity", str(e))

    # JSON 1.3: Array of 20 objects roundtrip
    try:
        lua.execute("""
            local hs = HttpService
            local arr = {}
            for i = 1, 20 do
                table.insert(arr, { id = i, name = "item_" .. i, active = (i % 2 == 0) })
            end
            local enc = hs:JSONEncode(arr)
            local dec = hs:JSONDecode(enc)
            _json_1_3_pass = (#dec == 20 and dec[1].id == 1 and dec[20].name == "item_20" and dec[20].active == true)
        """)
        if lua.eval("_json_1_3_pass"):
            results.record_pass("JSON 1.3: Array of 20 objects roundtrip")
        else:
            results.record_fail("JSON 1.3: Array of 20 objects roundtrip", "Array elements corrupted or count mismatch")
    except Exception as e:
        results.record_fail("JSON 1.3: Array of 20 objects roundtrip", str(e))

    # JSON 1.4: Empty object and array handling
    try:
        lua.execute("""
            local hs = HttpService
            local obj = {}
            local enc = hs:JSONEncode(obj)
            local dec = hs:JSONDecode(enc)
            _json_1_4_pass = (type(dec) == "table" and next(dec) == nil)
        """)
        if lua.eval("_json_1_4_pass"):
            results.record_pass("JSON 1.4: Empty object and array handling")
        else:
            results.record_fail("JSON 1.4: Empty object and array handling", "Empty table not returned as empty table")
    except Exception as e:
        results.record_fail("JSON 1.4: Empty object and array handling", str(e))

    # JSON 1.5: Unicode and Brazilian Portuguese strings
    try:
        lua.execute("""
            local hs = HttpService
            local data = { msg1 = "Atenção", msg2 = "Não perturbe", msg3 = "Configurações avançadas" }
            local enc = hs:JSONEncode(data)
            local dec = hs:JSONDecode(enc)
            _json_1_5_pass = (dec.msg1 == "Atenção" and dec.msg2 == "Não perturbe" and dec.msg3 == "Configurações avançadas")
        """)
        if lua.eval("_json_1_5_pass"):
            results.record_pass("JSON 1.5: Unicode and Brazilian Portuguese strings")
        else:
            results.record_fail("JSON 1.5: Unicode and Brazilian Portuguese strings", "PT-BR characters corrupted")
    except Exception as e:
        results.record_fail("JSON 1.5: Unicode and Brazilian Portuguese strings", str(e))

    # JSON 1.6: String escape sequences (quotes, newlines, slashes)
    try:
        lua.execute("""
            local hs = HttpService
            local esc_obj = {
                quote = 'He said "Hello"',
                nl = "Line1\\nLine2",
                slash = "C:\\\\Roblox\\\\Scripts"
            }
            local enc = hs:JSONEncode(esc_obj)
            local dec = hs:JSONDecode(enc)
            _json_1_6_quote = dec.quote
            _json_1_6_nl = dec.nl
            _json_1_6_slash = dec.slash
            _json_1_6_pass = (dec.quote == 'He said "Hello"' and dec.nl == "Line1\\nLine2" and dec.slash == "C:\\\\Roblox\\\\Scripts")
        """)
        if lua.eval("_json_1_6_pass"):
            results.record_pass("JSON 1.6: String escape sequences (quotes, newlines, slashes)")
        else:
            q = lua.eval("_json_1_6_quote")
            results.record_fail("JSON 1.6: String escape sequences (quotes, newlines, slashes)",
                                f"Escaped quote mismatch: '{q}'")
    except Exception as e:
        results.record_fail("JSON 1.6: String escape sequences (quotes, newlines, slashes)", str(e))

    # JSON 1.7: Full realistic DreezHub config serialization
    try:
        lua.execute("""
            local hs = HttpService
            local cfg = {
                Aimbot = { Enabled = true, FOV = 120, Smoothness = 0.5, TargetPart = "Head", TeamCheck = true },
                ESP = { Boxes = true, Tracers = false, Names = true, Distance = true, MaxDistance = 1000 },
                Hitbox = { Enabled = false, Size = 15, Transparency = 0.7 },
                Keybinds = { AimbotKey = "Enum.KeyCode.E", ESPToggle = "Enum.KeyCode.F" }
            }
            local enc = hs:JSONEncode(cfg)
            local dec = hs:JSONDecode(enc)
            _json_1_7_pass = (dec.Aimbot.Enabled == true and dec.Aimbot.FOV == 120 and dec.ESP.Boxes == true and dec.Keybinds.AimbotKey == "Enum.KeyCode.E")
        """)
        if lua.eval("_json_1_7_pass"):
            results.record_pass("JSON 1.7: Full realistic DreezHub config serialization")
        else:
            results.record_fail("JSON 1.7: Full realistic DreezHub config serialization", "Config mismatch after roundtrip")
    except Exception as e:
        results.record_fail("JSON 1.7: Full realistic DreezHub config serialization", str(e))

    # JSON 1.8: Syntax error rejection on malformed JSON
    try:
        lua.execute("""
            local hs = HttpService
            local ok, err = pcall(function()
                hs:JSONDecode('{"unclosed": "string')
            end)
            _json_1_8_pass = (not ok)
        """)
        if lua.eval("_json_1_8_pass"):
            results.record_pass("JSON 1.8: Syntax error rejection on malformed JSON")
        else:
            results.record_fail("JSON 1.8: Syntax error rejection on malformed JSON", "Failed to reject malformed JSON")
    except Exception as e:
        results.record_fail("JSON 1.8: Syntax error rejection on malformed JSON", str(e))

    # =========================================================================
    # Suite 2: Virtual File System (VFS) Operations
    # =========================================================================
    print("\n--- Suite 2: Virtual File System (VFS) Operations ---")

    # VFS 2.1: Basic writefile and readfile
    try:
        lua.execute("""
            writefile("test_basic.txt", "Hello VFS")
            local content = readfile("test_basic.txt")
            _vfs_2_1_pass = (content == "Hello VFS" and isfile("test_basic.txt"))
        """)
        if lua.eval("_vfs_2_1_pass"):
            results.record_pass("VFS 2.1: Basic writefile and readfile")
        else:
            results.record_fail("VFS 2.1: Basic writefile and readfile", "Content mismatch or file not found")
    except Exception as e:
        results.record_fail("VFS 2.1: Basic writefile and readfile", str(e))

    # VFS 2.2: Path normalization (./, \\, /)
    try:
        lua.execute("""
            writefile(".\\\\dir\\\\sub\\\\norm.txt", "normalized")
            local r1 = readfile("dir/sub/norm.txt")
            local r2 = readfile("./dir/sub/norm.txt")
            _vfs_2_2_pass = (r1 == "normalized" and r2 == "normalized" and isfile("dir/sub/norm.txt"))
        """)
        if lua.eval("_vfs_2_2_pass"):
            results.record_pass("VFS 2.2: Path normalization (./, \\, /)")
        else:
            results.record_fail("VFS 2.2: Path normalization", "Different path formats did not resolve to same file")
    except Exception as e:
        results.record_fail("VFS 2.2: Path normalization (./, \\, /)", str(e))

    # VFS 2.3: makefolder and isfolder hierarchy
    try:
        lua.execute("""
            makefolder("ConfigDir")
            _vfs_2_3_pass = isfolder("ConfigDir") and not isfile("ConfigDir")
        """)
        if lua.eval("_vfs_2_3_pass"):
            results.record_pass("VFS 2.3: makefolder and isfolder hierarchy")
        else:
            results.record_fail("VFS 2.3: makefolder and isfolder hierarchy", "isfolder returned false for created folder")
    except Exception as e:
        results.record_fail("VFS 2.3: makefolder and isfolder hierarchy", str(e))

    # VFS 2.4: delfile cleanup and readfile error on missing file
    try:
        lua.execute("""
            writefile("to_delete.txt", "bye")
            delfile("to_delete.txt")
            local exists = isfile("to_delete.txt")
            local ok, err = pcall(function() readfile("to_delete.txt") end)
            _vfs_2_4_pass = (not exists and not ok)
        """)
        if lua.eval("_vfs_2_4_pass"):
            results.record_pass("VFS 2.4: delfile cleanup and readfile error on missing file")
        else:
            results.record_fail("VFS 2.4: delfile cleanup", "File still exists or readfile did not error")
    except Exception as e:
        results.record_fail("VFS 2.4: delfile cleanup and readfile error on missing file", str(e))

    # VFS 2.5: listfiles with directory isolation
    try:
        lua.execute("""
            makefolder("IsolatedDir")
            writefile("IsolatedDir/f1.txt", "1")
            writefile("IsolatedDir/f2.txt", "2")
            writefile("IsolatedDir/f3.txt", "3")
            writefile("IsolatedDir/Sub/nested.txt", "nested")
            local list = listfiles("IsolatedDir")
            _vfs_2_5_pass = (#list == 3)
        """)
        if lua.eval("_vfs_2_5_pass"):
            results.record_pass("VFS 2.5: listfiles with directory isolation")
        else:
            cnt = lua.eval("#listfiles('IsolatedDir')")
            results.record_fail("VFS 2.5: listfiles with directory isolation", f"Expected 3 files, got {cnt}")
    except Exception as e:
        results.record_fail("VFS 2.5: listfiles with directory isolation", str(e))

    # VFS 2.6: Stress test 100 files create/read/list/delete
    try:
        lua.execute("""
            makefolder("StressDir")
            for i = 1, 100 do
                writefile("StressDir/stress_" .. i .. ".txt", "data_" .. i)
            end
            local list100 = listfiles("StressDir")
            local all_read = true
            for i = 1, 100 do
                if readfile("StressDir/stress_" .. i .. ".txt") ~= "data_" .. i then
                    all_read = false
                    break
                end
            end
            for i = 1, 50 do
                delfile("StressDir/stress_" .. i .. ".txt")
            end
            local list50 = listfiles("StressDir")
            _vfs_2_6_pass = (#list100 == 100 and all_read and #list50 == 50)
        """)
        if lua.eval("_vfs_2_6_pass"):
            results.record_pass("VFS 2.6: Stress test 100 files create/read/list/delete")
        else:
            results.record_fail("VFS 2.6: Stress test 100 files create/read/list/delete", "Count mismatch during stress test")
    except Exception as e:
        results.record_fail("VFS 2.6: Stress test 100 files create/read/list/delete", str(e))

    # VFS 2.7: Large 100KB payload write and read
    try:
        lua.execute("""
            local chunk = string.rep("0123456789abcdef", 64) -- 1024 bytes
            local big = string.rep(chunk, 100) -- 102,400 bytes (100KB)
            writefile("large_payload.bin", big)
            local read_back = readfile("large_payload.bin")
            _vfs_2_7_pass = (#read_back == 102400 and read_back == big)
        """)
        if lua.eval("_vfs_2_7_pass"):
            results.record_pass("VFS 2.7: Large 100KB payload write and read")
        else:
            results.record_fail("VFS 2.7: Large 100KB payload write and read", "Payload length or content corrupted")
    except Exception as e:
        results.record_fail("VFS 2.7: Large 100KB payload write and read", str(e))

    # VFS 2.8: listfiles on root, ./, and . paths
    try:
        lua.execute("""
            writefile("root_a.txt", "A")
            writefile("root_b.txt", "B")
            local l_empty = listfiles("")
            local l_dot_slash = listfiles("./")
            local l_dot = listfiles(".")
            _vfs_2_8_cnt_dot = #l_dot
            _vfs_2_8_pass = (#l_empty >= 2 and #l_dot_slash >= 2 and #l_dot >= 2)
        """)
        if lua.eval("_vfs_2_8_pass"):
            results.record_pass("VFS 2.8: listfiles on root, ./, and . paths")
        else:
            cnt = lua.eval("_vfs_2_8_cnt_dot")
            results.record_fail("VFS 2.8: listfiles on root, ./, and . paths", f"listfiles('.') failed: {cnt}")
    except Exception as e:
        results.record_fail("VFS 2.8: listfiles on root, ./, and . paths", str(e))

    # VFS 2.9: Deep folder hierarchy & recursive parent resolution
    try:
        lua.execute("""
            makefolder("Level1/Level2/Level3")
            writefile("AutoParent/Sub/deep.txt", "content")
            local l3 = isfolder("Level1/Level2/Level3")
            local l2 = isfolder("Level1/Level2")
            local l1 = isfolder("Level1")
            local ap = isfolder("AutoParent")
            local aps = isfolder("AutoParent/Sub")
            _vfs_2_9_pass = (l3 and l2 and l1 and ap and aps)
        """)
        if lua.eval("_vfs_2_9_pass"):
            results.record_pass("VFS 2.9: Deep folder hierarchy & recursive parent resolution")
        else:
            results.record_fail("VFS 2.9: Deep folder hierarchy & recursive parent resolution",
                                "Intermediate ancestor folders do not exist")
    except Exception as e:
        results.record_fail("VFS 2.9: Deep folder hierarchy & recursive parent resolution", str(e))

    # =========================================================================
    # Suite 3: Drawing API Lifecycles & Mutation Invariance
    # =========================================================================
    print("\n--- Suite 3: Drawing API Lifecycles & Mutation Invariance ---")

    # Drawing 3.1: Allocate 50 drawings, mutate properties, check state
    try:
        lua.execute("""
            local types = { "Square", "Text", "Line", "Circle" }
            local drawings = {}
            for i = 1, 50 do
                local t = types[(i % 4) + 1]
                local d = Drawing.new(t)
                d.Visible = true
                d.Color = Color3.fromRGB(i, i * 2, i * 3)
                d.Transparency = 0.5
                table.insert(drawings, d)
            end
            local valid = (#drawings == 50)
            for i, d in ipairs(drawings) do
                if not d.Visible or d.Transparency ~= 0.5 then
                    valid = false
                    break
                end
            end
            for _, d in ipairs(drawings) do
                d:Remove()
            end
            _draw_3_1_pass = valid
        """)
        if lua.eval("_draw_3_1_pass"):
            results.record_pass("Drawing 3.1: Allocate 50 drawings, mutate properties, check state")
        else:
            results.record_fail("Drawing 3.1: Allocate 50 drawings", "Property mutation or count mismatch")
    except Exception as e:
        results.record_fail("Drawing 3.1: Allocate 50 drawings, mutate properties, check state", str(e))

    # Drawing 3.2: Removal invariance, double-removal safety, Destroy alias
    try:
        lua.execute("""
            local dlist = {}
            for i = 1, 30 do
                table.insert(dlist, Drawing.new("Line"))
            end
            -- Remove odd items
            for i = 1, 30, 2 do
                dlist[i]:Remove()
                -- Safe double-remove
                pcall(function() dlist[i]:Remove() end)
            end
            local active_count = 0
            for _, d in ipairs(Drawing._activeObjects) do
                active_count = active_count + 1
            end
            -- Destroy remaining with :Destroy() alias
            for i = 2, 30, 2 do
                dlist[i]:Destroy()
            end
            local final_count = 0
            for _, d in ipairs(Drawing._activeObjects) do
                final_count = final_count + 1
            end
            _draw_3_2_pass = (active_count == 15 and final_count == 0)
        """)
        if lua.eval("_draw_3_2_pass"):
            results.record_pass("Drawing 3.2: Removal invariance, double-removal safety, Destroy alias")
        else:
            results.record_fail("Drawing 3.2: Removal invariance", "Active count mismatch after removals")
    except Exception as e:
        results.record_fail("Drawing 3.2: Removal invariance, double-removal safety, Destroy alias", str(e))

    # Drawing 3.3: Rapid 200-object allocation and reverse removal
    try:
        lua.execute("""
            local bulk = {}
            for i = 1, 200 do
                table.insert(bulk, Drawing.new("Square"))
            end
            local count200 = 0
            for _, d in ipairs(Drawing._activeObjects) do count200 = count200 + 1 end
            for i = 200, 1, -1 do
                bulk[i]:Remove()
            end
            local count0 = 0
            for _, d in ipairs(Drawing._activeObjects) do count0 = count0 + 1 end
            _draw_3_3_pass = (count200 == 200 and count0 == 0)
        """)
        if lua.eval("_draw_3_3_pass"):
            results.record_pass("Drawing 3.3: Rapid 200-object allocation and reverse removal")
        else:
            results.record_fail("Drawing 3.3: Rapid 200-object allocation and reverse removal",
                                "Bulk churn count invariant failed")
    except Exception as e:
        results.record_fail("Drawing 3.3: Rapid 200-object allocation and reverse removal", str(e))

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n==================================================")
    print(f"Results: {results.passed} passed, {results.failed} failed out of {results.passed + results.failed} tests.")
    if results.failed > 0:
        print("Failures:")
        for f in results.failures:
            print(f"  - {f}")
    print("==================================================")
    return results

if __name__ == "__main__":
    res = run_challenger_probes()
    sys.exit(0 if res.failed == 0 else 1)
