"""The camera MCP server through a real MCP client session (stdio): python tests/test_mcp_server.py"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "agent"))
from mcp_bridge import MCPBridge  # noqa: E402


def main():
    out = tempfile.mkdtemp(prefix="cam_mcp_")
    br = MCPBridge(out, seed=2, limits={"max_exposure_us": 100000, "max_frames": 8})
    try:
        names = br.tool_names()
        print("tools:", names)
        assert {"camera_info", "set_exposure", "set_gain", "set_roi", "reset_roi", "set_illumination", "capture",
                "analyze_frame"} <= set(names)
        info = br.call("camera_info")
        assert info["ok"] and info["max_dn"] == 4095 and info["lab_limits"]["max_exposure_us"] == 100000
        assert br.call("set_exposure", {"exposure_us": 250})["exposure_us"] == 250
        refused = br.call("set_exposure", {"exposure_us": 200000})
        assert refused["ok"] is False and "lab limit" in refused["error"], refused
        cap = br.call("capture", {"n_frames": 2, "label": "test", "regions": [{"name": "c", "x": 300, "y": 236, "width": 40, "height": 40}]})
        assert cap["ok"] and cap["settings"]["exposure_us"] == 250 and "temporal_noise" in cap and os.path.exists(cap["frame_file"])
        print("capture:", json.dumps({k: cap[k] for k in ("settings", "stats")})[:400])
        an = br.call("analyze_frame", {"frame_file": cap["frame_file"], "black_level_dn": 40,
                                       "region": {"name": "c", "x": 270, "y": 206, "width": 100, "height": 100}})
        assert an["ok"] and 0.8 < an["speckle"]["contrast"] < 1.2
        print("analyze:", an["speckle"])
        se = br.call("capture_series", {"n_frames": 4, "interval_s": 0.2, "label": "stab"})
        assert se["ok"] and len(se["series"]["mean_dn"]) == 4 and se["duration_s"] >= 0.55 and os.path.exists(se["series_file"])
        print("series:", se["summary"], f"{se['duration_s']} s")
        assert br.call("capture_series", {"n_frames": 100, "interval_s": 10})["ok"] is False      # above max_series_s
        lc = {t.name: t for t in br.langchain_tools()}
        r = json.loads(lc["set_gain"].invoke({"gain_db": 6}))
        assert r["ok"] and r["gain_db"] == 6.0
        assert json.loads(lc["camera_info"].invoke({}))["gain_db"] == 6.0          # state kept in the one session
        calls = [json.loads(line) for line in open(os.path.join(out, "calls.jsonl"), encoding="utf-8")]
        print(f"calls.jsonl: {len(calls)} records, tools {[c['tool'] for c in calls]}")
        assert len(calls) == 9
    finally:
        br.close()
    print("ALL MCP SERVER CHECKS PASSED")


if __name__ == "__main__":
    main()
