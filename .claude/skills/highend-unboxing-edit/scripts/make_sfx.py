#!/usr/bin/env python3
"""Synthesise the soft UI sounds used when text / stickers pop in (no third-party samples needed).
  pop.wav     - short bubbly pop for stickers
  ding.wav    - soft two-tone chime for title cards and product labels
  whoosh.wav  - airy swipe, alternative for title cards
Usage: python3 make_sfx.py [out_dir]"""
import os, sys, wave
import numpy as np

SR = 48000

def save(path, x):
    x = x / (np.abs(x).max() + 1e-9) * 0.8
    st = np.repeat((x * 32767).astype(np.int16)[:, None], 2, axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())

def pop():
    t = np.arange(int(0.14 * SR)) / SR
    f = 420 + 900 * np.exp(-t / 0.018)          # quick upward-then-settling pitch = "bloop"
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = (1 - np.exp(-t / 0.002)) * np.exp(-t / 0.035)
    return np.sin(ph) * env

def ding():
    t = np.arange(int(0.9 * SR)) / SR
    env = (1 - np.exp(-t / 0.003)) * np.exp(-t / 0.22)
    x = (np.sin(2 * np.pi * 1318.5 * t) + 0.55 * np.sin(2 * np.pi * 1975.5 * t)
         + 0.2 * np.sin(2 * np.pi * 2637 * t)) * env
    return x

def whoosh():
    n = int(0.45 * SR); t = np.arange(n) / SR
    noise = np.random.default_rng(1).standard_normal(n)
    # sweep a simple one-pole low-pass cutoff up then down
    cut = 0.02 + 0.25 * np.sin(np.pi * t / t[-1]) ** 2
    y = np.zeros(n); acc = 0.0
    for i in range(n):
        acc += cut[i] * (noise[i] - acc); y[i] = acc
    return y * np.sin(np.pi * t / t[-1]) ** 1.5

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "sfx")
    os.makedirs(out, exist_ok=True)
    for name, fn in [("pop", pop), ("ding", ding), ("whoosh", whoosh)]:
        save(os.path.join(out, name + ".wav"), fn()); print("wrote", name)
