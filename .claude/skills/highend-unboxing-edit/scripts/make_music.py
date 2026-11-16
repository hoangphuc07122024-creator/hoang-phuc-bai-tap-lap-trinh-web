#!/usr/bin/env python3
"""Soft 'luxury boutique' background bed, synthesised (no third-party music, no licensing issue).
Warm electric-piano chords (Cmaj9 - Am9 - Fmaj9 - G6) + airy pad + soft sub, 72 bpm, gentle reverb.
Optionally ducked under a voice track (lower when someone is speaking).

  python3 make_music.py out.wav SECONDS [voice.wav] [--upbeat]
  --upbeat : vui tươi, 112 bpm, D major, pluck + bass + kick/snap/shaker (quà tặng, sale, mua sắm)
  (mặc định): calm - êm, chậm, piano điện (sang trọng, cảm xúc)
"""
import sys, wave
import numpy as np

SR = 44100
BPM = 72
BEAT = 60 / BPM
CHORDS = [  # MIDI notes
    [48, 55, 59, 62, 64],   # Cmaj9
    [45, 52, 55, 59, 60],   # Am9
    [41, 48, 52, 55, 57],   # Fmaj9 (F A C E G)
    [43, 50, 52, 55, 59],   # G6/add9
]
hz = lambda m: 440 * 2 ** ((m - 69) / 12)


def ep(f, dur, vel=0.5):
    """soft electric piano: sine + bell partial, quick attack, long decay, slow tremolo"""
    t = np.arange(int(dur * SR)) / SR
    env = (1 - np.exp(-t / 0.006)) * np.exp(-t / 1.6)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.4) \
        + 0.08 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t / 0.15)
    return x * env * vel * (1 + 0.08 * np.sin(2 * np.pi * 4.2 * t))


def pad(freqs, dur):
    t = np.arange(int(dur * SR)) / SR
    x = sum(np.sin(2 * np.pi * f * (1 + d) * t + p) for f in freqs for d, p in ((-0.003, 0), (0.003, 1.3)))
    env = np.minimum(1, t / 1.2) * np.minimum(1, (dur - t) / 1.2)
    # crude low-pass: moving average
    k = 40; x = np.convolve(x, np.ones(k) / k, "same")
    return x * env / len(freqs)


def reverb(x, secs=2.2, wet=0.28):
    n = int(secs * SR); rng = np.random.default_rng(3)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / (SR * secs / 6.9))
    ir = np.convolve(ir, np.ones(30) / 30, "same"); ir /= np.abs(ir).sum() ** 0.5 * 30
    L = len(x) + n; N = 1 << (L - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[:len(x)]
    return x * (1 - wet) + y * wet / (np.abs(y).max() + 1e-9) * np.abs(x).max()


def make(total):
    n = int((total + 3) * SR); out = np.zeros(n)
    bar = 4 * BEAT; k = 0; t0 = 0.0
    rng = np.random.default_rng(11)
    while t0 < total + 2:
        ch = CHORDS[k % 4]
        # chord on beat 1 (rolled), two light melody-ish notes on beats 3 and 4
        for j, m in enumerate(ch[1:]):
            s = int((t0 + j * 0.03) * SR); x = ep(hz(m), bar * 1.6, 0.18)
            out[s:s + len(x)] += x[:max(0, n - s)]
        for b, m in ((2, ch[-1] + 12), (3, ch[-2] + 12)):
            s = int((t0 + b * BEAT) * SR); x = ep(hz(m), BEAT * 2.5, 0.07 + 0.03 * rng.random())
            out[s:s + len(x)] += x[:max(0, n - s)]
        # sub + pad
        s = int(t0 * SR); x = pad([hz(ch[0]), hz(ch[0] + 12)], bar + 1.0)
        out[s:s + len(x)] += 0.35 * x[:max(0, n - s)]
        s2 = pad([hz(ch[0] - 12)], bar + 0.5); out[s:s + len(s2)] += 0.25 * s2[:max(0, n - s)]
        t0 += bar; k += 1
    out = reverb(out)[: int(total * SR)]
    fade = int(2.5 * SR); out[-fade:] *= np.linspace(1, 0, fade); out[: int(0.8 * SR)] *= np.linspace(0, 1, int(0.8 * SR))
    return out / (np.abs(out).max() + 1e-9) * 0.7


def pluck(f, dur, vel=0.3, bright=1.0):
    """plucky synth (like a muted guitar / marimba-ish): fast decay, a little harmonic sparkle"""
    t = np.arange(int(dur * SR)) / SR
    env = (1 - np.exp(-t / 0.003)) * np.exp(-t / 0.18)
    x = np.sin(2 * np.pi * f * t) + 0.45 * bright * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.08) \
        + 0.2 * bright * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / 0.05)
    return x * env * vel


def kick(vel=0.9):
    t = np.arange(int(0.35 * SR)) / SR
    f = 50 + 90 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12) * vel


def snap(vel=0.4):
    rng = np.random.default_rng(5); t = np.arange(int(0.12 * SR)) / SR
    n = rng.standard_normal(len(t))
    n = np.convolve(n, np.ones(4) / 4, "same") - np.convolve(n, np.ones(40) / 40, "same")   # ~1-5 kHz band
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.03)
    return (0.6 * n + 0.5 * body) * np.exp(-t / 0.03) * vel


def shaker(vel=0.12, seed=0):
    rng = np.random.default_rng(seed); t = np.arange(int(0.07 * SR)) / SR
    n = rng.standard_normal(len(t))
    n = np.convolve(n, np.ones(3) / 3, "same") - np.convolve(n, np.ones(12) / 12, "same")
    return n * np.sin(np.pi * t / t[-1]) * vel


def make_upbeat(total, bpm=112):
    """bright, happy 'shopping / gift' groove: D major I-V-vi-IV, plucks on 8ths, bass, kick-snap-shaker"""
    beat = 60 / bpm; bar = 4 * beat
    prog = [[62, 66, 69, 74], [57, 61, 64, 69], [59, 62, 66, 71], [55, 59, 62, 67]]   # D A Bm G
    bass = [38, 33, 35, 31]
    n = int((total + 3) * SR); out = np.zeros(n); drums = np.zeros(n)
    rng = np.random.default_rng(21)
    def put(buf, s, x):
        s = int(s * SR); e = min(n, s + len(x))
        if s < n:
            buf[s:e] += x[:e - s]
    t0, k = 0.0, 0
    patt = [0, 2, 1, 3, 2, 1, 3, 2]        # arpeggio order over 8 eighth-notes
    while t0 < total + 2:
        ch = prog[k % 4]
        for i in range(8):                  # 8th-note pluck arpeggio, accent on the beat
            m = ch[patt[i]] + (12 if i in (3, 7) else 0)
            put(out, t0 + i * beat / 2, pluck(hz(m), 0.5, 0.20 if i % 2 == 0 else 0.13))
        for b in (0, 1.5, 2, 3.5):          # bouncy bass
            put(out, t0 + b * beat, pluck(hz(bass[k % 4]), 0.45, 0.32, bright=0.4))
        if k % 2 == 1:                      # small melody hook every 2nd bar
            for j, (b, m) in enumerate(((0, ch[3] + 12), (0.5, ch[2] + 12), (1, ch[3] + 12), (2.5, ch[1] + 24))):
                put(out, t0 + b * beat, ep(hz(m), 0.9, 0.09))
        if t0 >= bar:                       # drums come in after the first bar
            for b in range(4):
                put(drums, t0 + b * beat, kick(0.45 if b in (0, 2) else 0.0))
                if b in (1, 3):
                    put(drums, t0 + b * beat, snap(0.16))
                for h in (0, 0.5):
                    put(drums, t0 + (b + h) * beat, shaker(0.022 if h else 0.016, int(rng.integers(1e6))))
        t0 += bar; k += 1
    mix = reverb(out, 1.4, 0.18) + drums
    mix = mix[: int(total * SR)]
    fade = int(2.0 * SR); mix[-fade:] *= np.linspace(1, 0, fade); mix[: int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))
    return mix / (np.abs(mix).max() + 1e-9) * 0.7


def duck(music, voice_wav, depth_db=7):
    w = wave.open(voice_wav); sr = w.getframerate(); ch = w.getnchannels()
    v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, ch).mean(1) / 32768
    hop = sr // 50; nfr = len(v) // hop
    e = np.sqrt((v[:nfr * hop].reshape(nfr, hop) ** 2).mean(1))
    on = (20 * np.log10(e + 1e-9) > np.percentile(20 * np.log10(e + 1e-9), 35)).astype(float)
    on = np.convolve(on, np.ones(15) / 15, "same")             # ~300 ms smoothing
    g = 10 ** (-depth_db * np.clip(on * 1.5, 0, 1) / 20)
    gi = np.interp(np.arange(len(music)) / SR, np.arange(len(g)) / 50, g)
    return music * gi


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    style = "upbeat" if "--upbeat" in sys.argv else "calm"
    out, secs = args[0], float(args[1])
    m = make_upbeat(secs) if style == "upbeat" else make(secs)
    if len(args) > 2:
        m = duck(m, args[2])
    st = np.stack([m, np.roll(m, 220)], 1)                     # tiny stereo width
    w = wave.open(out, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    print("wrote", out)
