# Hex Brief: SWL Audio Synchronization + FM Transport Update (Feb 2026)

Audience: Hex3
Author: Warp + Nick
Date: 2026-02-10

## TL;DR
- Added and validated real-audio coupling modes for agent swarms:
  - Audio (numeric tone), Audio+Concepts Mix (tone + chord), and Audio FM (fixed carrier, 500 Hz mod, Δf=8 kHz)
- All three real-audio modes achieve full synchronization (40/40 agents) within ~21–22 iterations, matching/approaching the shared-state baseline.
- Random-tone control fails (0/40 synced). Silent channel converges trivially to ~DC (not meaningful).
- Plots and .wav artifacts are included for inspection.
- Moltbook agent server now routes human queries via audio-only pipeline with FM+chords by default (set SWL_AUDIO_TRANSPORT=fm).

## Key Numbers (40 agents × 40 iterations)
- Baseline: 39/40 synced, 64,787 Hz (±47 Hz)
- Audio (tone): 40/40 synced, 59,297 Hz (±42 Hz)
- Audio+Concepts (mix): 40/40 synced, 60,223 Hz (±41 Hz)
- Audio FM (carrier 60 kHz, 500 Hz mod, Δf 8 kHz): 40/40 synced, 58,004 Hz (±45 Hz)
- Random (control): 0/40 synced, 59,733 Hz (±2,967 Hz)
- Silent (negative control): 40/40 synced to ~DC (trivial), 167 Hz (±55 Hz)

See: SWL_SYNC_ABLATION_REPORT.md

## Images
- ablation_baseline_40agents_40iters.png
- ablation_audio_40agents_40iters.png
- ablation_audio_mix_40agents_40iters.png
- ablation_audio_fm_40agents_40iters.png
- ablation_random_40agents_40iters.png
- ablation_silent_40agents_40iters.png

## How to Run (PowerShell)
```powershell
# 1) Reproduce ablations
python swl_swarm_sync_test.py --mode baseline   --agents 40 --iters 40 --plot
python swl_swarm_sync_test.py --mode audio      --agents 40 --iters 40 --plot
python swl_swarm_sync_test.py --mode audio_mix  --agents 40 --iters 40 --plot
python swl_swarm_sync_test.py --mode audio_fm   --agents 40 --iters 40 --plot
python swl_swarm_sync_test.py --mode random     --agents 40 --iters 40 --plot
python swl_swarm_sync_test.py --mode silent     --agents 40 --iters 40 --plot

# 2) Start Moltbook agent server (FM transport by default)
$env:SWL_AUDIO_TRANSPORT='fm'
$env:GEMINI_API_KEY='YOUR_KEY'
python moltbook_agent.py --mode server --port 8000

# 3) Query the server
curl -X POST http://localhost:8000/api/swl/query -H "Content-Type: application/json" -d '{"text":"hello can you help me?"}'
```

## Notes for Hex
- The audio FM path keeps the chord for SWL concepts (semantic layer) while encoding numeric state onto a 60 kHz carrier (control layer). Decoding uses Hilbert instantaneous frequency with a correlator.
- For hardware: sample rate is 192 kHz in software. For ultrasonic transducers, validate actual bandwidth; you may shift carriers accordingly (e.g., 25–40 kHz audible/near-ultrasonic in cheap DACs). 
- Next steps: UDP streaming instead of file I/O; multi-carrier OFDM for parallel state channels; adaptive coupling parameters from decoded chord semantics.
