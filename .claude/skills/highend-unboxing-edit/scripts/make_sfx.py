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


# ---- money / payment sounds (intro "lương về") ----
def _bell(f, dur, decay, partials=((1, 1), (2.76, .45), (5.4, .25), (8.9, .12))):
    t = np.arange(int(dur * SR)) / SR
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (decay / (1 + r * 0.35))) for r, a in partials)
    return x * (1 - np.exp(-t / 0.002))

def _place(total, parts):
    out = np.zeros(int(total * SR))
    for start, x, g in parts:
        i = int(start * SR); n = min(len(x), len(out) - i); out[i:i + n] += x[:n] * g
    return out

def ting_ting():          # bank-app style double "ting"
    a = _bell(1760, 0.9, 0.35); b = _bell(2349, 0.9, 0.45)
    return _place(1.25, [(0, a, 1.0), (0.17, b, 1.0)])

def coins():              # scatter of small metallic pings
    rng = np.random.default_rng(7); parts = []
    for k in range(14):
        f = rng.uniform(3500, 6500); parts.append((rng.uniform(0, 0.55), _bell(f, 0.25, 0.05, ((1, 1), (1.5, .5))), rng.uniform(.3, .8)))
    return _place(0.9, parts)

def kaching():            # cash-register: drawer clunk + bright bell + coins
    t = np.arange(int(0.12 * SR)) / SR
    clunk = np.random.default_rng(2).standard_normal(len(t)) * np.exp(-t / 0.02)
    clunk = np.convolve(clunk, np.ones(25) / 25, "same")
    return _place(1.2, [(0, clunk, 1.2), (0.06, _bell(2637, 1.0, 0.5), 1.0), (0.06, _bell(3951, 0.8, 0.35), 0.5), (0.1, coins(), 0.5)])

def pay_beep():           # POS card reader: two short beeps then rising success chime
    t = np.arange(int(0.09 * SR)) / SR
    beep = np.sin(2 * np.pi * 2700 * t) * np.minimum(1, np.minimum(t, t[-1] - t) / 0.004)
    chime = [(0.32 + i * 0.09, _bell(f, 0.6, 0.25, ((1, 1), (2, .3))), 0.8) for i, f in enumerate((1047, 1319, 1568, 2093))]
    return _place(1.2, [(0, beep, 0.7), (0.14, beep, 0.7)] + chime)

def whoosh_fast():
    n = int(0.3 * SR); t = np.arange(n) / SR
    noise = np.random.default_rng(5).standard_normal(n); y = np.zeros(n); acc = 0.0
    cut = 0.03 + 0.5 * np.sin(np.pi * t / t[-1]) ** 2
    for i in range(n):
        acc += cut[i] * (noise[i] - acc); y[i] = acc
    return y * np.sin(np.pi * t / t[-1])

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "sfx")
    for name, fn in [("ting_ting", ting_ting), ("coins", coins), ("kaching", kaching), ("pay_beep", pay_beep), ("whoosh_fast", whoosh_fast)]:
        save(os.path.join(out, name + ".wav"), fn()); print("wrote", name)
