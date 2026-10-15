# PhotonicsAI — Homework 3 (hardware in the loop)

Erik Mirzoyan. Course: PhotonicsAI — AI-Driven Science and Autonomous Laboratories.

A lab camera, the **Hikrobot MV-CS028-10UM** (monochrome, USB3 Vision), is connected to the agent system of Homeworks 1
and 2 through its SDK (Hikrobot MVS) and an MCP server. Only the executor holds the camera's tools, and a hardware turn in
the LangGraph graph runs the loop *decide → command the camera → read the measurement → decide again*. From a
plain-language request the system sets the exposure, measures the camera's noise model and stability, finds a
flicker-free exposure, and puts the measured numbers into the camera model of the Homework 2 focusing bench to predict
the focusing enhancement with this camera.

```
hw3.py         one entry point: tests, camera check, tool list, runs, live view, demo, MCP client config
camera/        connector layer: base.py (the camera interface), hikrobot_camera.py (MVS SDK), sim_camera.py
               (simulated camera: laser-speckle or room-light scene), stats.py (image statistics)
mcp_server/    camera_server.py: MCP server (stdio) exposing the camera's controls as 13 tools; logs every call
agent/         agent_v3.py (the HW1/HW2 graph + the hardware turn), mcp_bridge.py (MCP client), run_hw3.py (runs a
               request), bench.py (the HW2 simulated bench and focusing tool), coding_tool.py, claude_cli.py,
               render_hw3.py / render_tools.py (report tables and sequence diagrams), live_view.py, demo_real.py
agent/runs/    every run: request, transcript, events, analysis scripts, camera/calls.jsonl, frame previews
               (real_* = the lab camera, uc* = dry runs on the simulated camera)
tests/         offline tests (no model, no camera), SDK check, real-camera connection check and its logs
report/        LaTeX source and PDF of the Homework 3 report
video/         the two demo screen recordings
```

## Setup
Python 3.11–3.13. On Windows (PowerShell, or the PyCharm terminal):
```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```
(Linux/macOS: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.)

* **Language model:** an API key (`ANTHROPIC_API_KEY`, `--model anthropic:claude-sonnet-5-5`), or without a key the
  Claude Code CLI logged in with a Claude subscription and `--model claude-cli:claude-sonnet-5-5`. All runs in the report
  used the CLI.
* **The real camera:** install Hikrobot **MVS** (free, Hikrobot download centre) with its SDK; the connector finds the SDK
  and its Python wrapper (`MvImport`) through the MVS installation. Plug the camera into a USB 3 port and **close the MVS
  client** before a run (the connector opens the camera exclusively). The simulated camera needs nothing extra.

## One command
```
python hw3.py test           # all offline tests in one go, with a summary
python hw3.py check-camera   # MVS SDK, then the plugged-in camera
python hw3.py tools          # the 13 MCP tools as a client sees them
python hw3.py run --thread t1 --camera hikrobot --request "..."
python hw3.py live           # live view of the agent's captures
python hw3.py mcp-config     # the entry that adds the camera server to any MCP client (e.g. Claude Desktop)
```

## Tests (no model needed)
```
python tests/test_camera.py          # simulated camera physics and statistics (photon transfer recovers gain and read noise)
python tests/test_mcp_server.py      # the MCP server through a real MCP client session
python tests/test_agent_offline.py   # graph mechanics with a scripted model and the real MCP server
python tests/check_mvs_sdk.py        # the MVS SDK on this PC (no camera needed)
python tests/check_real_camera.py --dark   # connector check on the plugged-in camera (asks you to cover the lens)
```

## Runs
```
cd agent
python run_hw3.py --thread my_run --camera hikrobot --model claude-cli:claude-sonnet-5-5 --request "Set the camera so that the white surface uses most of the camera's range without saturating, and report the exposure and gain you chose."
python run_hw3.py --thread my_run2 --camera hikrobot --human --model claude-cli:claude-sonnet-5-5 --request "..."   # the graph stops and asks you
python render_hw3.py runs/my_run --tex ../report/runs/my_run.tex --title "..."   # tool-call table and sequence diagram
```
`--camera sim` (default) and `--camera sim-room` use the simulated camera; `--camera hikrobot` the lab camera. When the
graph pauses (a hard decision, or a request to block the light), type the reply in the terminal; a paused thread can also
be resumed later with `--reply "..."`. `python demo_real.py --thread my_demo` opens the live camera view
(`live_view.py`), waits for Enter and then runs a request on the lab camera, as used for the demo videos.

## Results (lab session, 14 October 2026)
* Connector check: the camera was digitising with 8 bits and its default black level clipped the dark noise at 0 DN; the
  connector now selects the 12-bit ADC and a black level about 60 DN above zero (logs in `tests/real_camera_check/`).
* Auto-exposure: 9.4 ms at 0 dB, brightest part at 87.7 % of full scale, no saturated pixel.
* Flicker: the LED room lights hardly flicker (0.14 % frame-to-frame at 1 ms, 0.05 % at 10 ms).
* Stability: −3.4 %/min over 2 min (most likely the fading daylight from the window).
* Noise model: conversion gain 6.14 e⁻/DN, read noise 5.8 e⁻, full well ≥ 24 800 e⁻ (ADC-limited).
* Focusing prediction at the Homework 2 settings (256 segments): enhancement 30.6 with this camera against 33.6 with the
  bench's default camera.
* Human stops: the graph asked for approval and for the light to be blocked; when the light was not blocked, the agent
  noticed that the "dark" frames were bright and did not use them.

Demo videos: `video/hw3_demo_real_camera.mp4` (the agent sets the exposure of the real camera through MCP) and
`video/hw3_demo_human_stop.mp4` (the graph stops twice for the person's approval). Raw camera frames (`.npy`) are not in
the repository because of their size; each capture has a `.png` preview and is listed in `calls.jsonl`.

## Additions after the deadline extension (October 2026)
* **Four new MCP tools** (13 in total): `set_black_level` and `set_adc_bit_depth` (the two settings that the lab session
  showed matter for noise measurements: an 8-bit ADC hides the read noise, a black level at 0 DN clips the dark noise),
  `read_temperature` (device temperature; dark current depends on it) and `save_tiff` (a capture as a 16-bit multi-page
  TIFF for ImageJ/Fiji). They are in the connector interface (`camera/base.py`), the Hikrobot connector (GenICam nodes
  `BlackLevel`, `ADCBitDepth`, `DeviceTemperature`) and the simulated camera (which models the 8-bit ADC's coarse
  levels). A restarted server restores them from `calls.jsonl` like the other settings; the hardware turn's VERIFIED
  record includes temperatures and TIFF files.
* **`hw3.py`**: one entry point for tests, camera check, runs, live view, demo and the MCP client configuration.
* **Token meter**: every model call through the Claude Code CLI is counted (calls, input/output tokens, the CLI's cost
  estimate), and `model@low` lowers the model's thinking effort (about 40 % fewer output tokens in a test).
* The MCP client always uses the Windows proactor event loop, so the camera server also starts inside other apps.
* Tests: `test_mcp_server.py` checks the new tools (8-bit levels, dark level at a new black level, TIFF pages equal to
  the frames, settings restored after a server restart); `tests/check_real_camera.py` checks them on the lab camera.

## Report
```
cd agent && python render_tools.py && cd ../report
pdflatex homework3.tex
pdflatex homework3.tex
```
