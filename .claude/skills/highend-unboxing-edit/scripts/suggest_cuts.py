#!/usr/bin/env python3
"""Talking-head jump-cut helper: find pauses in the speech and print the
"keep" ranges as clip entries ready to paste into a render plan.

Usage:
  python3 suggest_cuts.py talking.mov [--noise -32] [--min-pause 0.35] [--pad 0.06]

--noise      silence threshold in dB (raise to -28 for noisy rooms)
--min-pause  pauses shorter than this are kept (natural breathing)
--pad        seconds of audio kept on each side of a cut so words aren't clipped
"""
import argparse
import json
import re
import subprocess


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--noise", type=float, default=-32)
    ap.add_argument("--min-pause", type=float, default=0.35)
    ap.add_argument("--pad", type=float, default=0.06)
    a = ap.parse_args()

    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.src],
        capture_output=True, text=True).stdout)
    log = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", a.src, "-vn", "-af",
         f"silencedetect=n={a.noise}dB:d={a.min_pause}", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    silences = list(zip(starts, ends + [dur] * (len(starts) - len(ends))))

    keep, cur = [], 0.0
    for s, e in silences:
        if s - cur > 0.15:
            keep.append((max(0.0, cur - (a.pad if cur else 0)), min(dur, s + a.pad)))
        cur = e
    if dur - cur > 0.15:
        keep.append((max(0.0, cur - a.pad), dur))

    clips = [{"src": a.src, "in": round(s, 3), "out": round(e, 3)} for s, e in keep]
    total = sum(e - s for s, e in keep)
    print(json.dumps(clips, indent=2, ensure_ascii=False))
    print(f"# {len(clips)} segments, {total:.1f}s kept of {dur:.1f}s "
          f"({len(clips) - 1} jump cuts)", flush=True)


if __name__ == "__main__":
    main()
