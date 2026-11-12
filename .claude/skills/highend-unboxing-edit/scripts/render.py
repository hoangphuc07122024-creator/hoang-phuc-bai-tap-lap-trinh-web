#!/usr/bin/env python3
"""Render a 9:16 "highend unboxing" style video from a JSON edit plan.

Style rules baked in (see ../SKILL.md):
  * every cut is a HARD cut (no crossfade, no zoom transition)
  * every overlay pops in / out on an exact frame (no fade, no slide)
  * text sits in the top ~25% of the frame, above the speaker's head

Usage:
  python3 render.py plan.json            # render
  python3 render.py plan.json --preview  # also writes a contact sheet PNG of the result

Requires: ffmpeg, ffprobe, Pillow.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "assets", "fonts")
SERIF = os.path.join(FONTS, "PlayfairDisplay.ttf")
SERIF_ITALIC = os.path.join(FONTS, "PlayfairDisplay-Italic.ttf")
DIDONE = os.path.join(FONTS, "BodoniModa.ttf")
SANS = os.path.join(FONTS, "BeVietnamPro-SemiBold.ttf")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(" ".join(cmd) + "\n" + r.stderr[-3000:])
        sys.exit(r.returncode)
    return r.stdout


def has_audio(path):
    out = run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
               "stream=index", "-of", "csv=p=0", path])
    return bool(out.strip())


def font(path, size, weight=None):
    f = ImageFont.truetype(path, int(size))
    if weight is not None:
        try:
            axes = f.get_variation_axes()
            vals = []
            for a in axes:
                name = a.get("name", b"")
                name = name.decode() if isinstance(name, bytes) else str(name)
                if name.lower().startswith("weight"):
                    vals.append(max(a["minimum"], min(a["maximum"], weight)))
                else:
                    vals.append(a.get("default", a["minimum"]))
            f.set_variation_by_axes(vals)
        except Exception:
            pass
    return f


def fit_font(path, text, target_w, weight=None, start=400):
    """Largest font size whose rendered width <= target_w."""
    size = start
    while size > 8:
        f = font(path, size, weight)
        l, t, r, b = f.getbbox(text)
        if r - l <= target_w:
            return f
        size -= 2
    return font(path, 8, weight)


def draw_centered(layer, text, f, cx, cy, fill, shadow=None):
    d = ImageDraw.Draw(layer)
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    x = cx - (r - l) / 2 - l
    y = cy - (b - t) / 2 - t
    if shadow:
        sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((x, y + shadow["dy"]), text, font=f, fill=shadow["color"])
        sh = sh.filter(ImageFilter.GaussianBlur(shadow["blur"]))
        layer.alpha_composite(sh)
        d = ImageDraw.Draw(layer)
    d.text((x, y), text, font=f, fill=fill)
    return (x + l, y + t, x + r, y + b)


SOFT = {"dy": 3, "blur": 6, "color": (0, 0, 0, 90)}
# for bright/busy backgrounds (light ceilings, shop shelves): plan "shadow": "strong"
STRONG = {"dy": 3, "blur": 9, "color": (0, 0, 0, 170)}


def shadow_of(o):
    return STRONG if o.get("shadow") == "strong" else SOFT


def overlay_title(W, H, o):
    """3-tier editorial title: light serif / BIG bold-italic serif / small serif tucked bottom-right."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    color = tuple(o.get("color", [255, 255, 255, 255]))
    y = o.get("y", 0.175)  # vertical centre of the main word, as fraction of H
    main_f = fit_font(SERIF_ITALIC, o["main"], W * o.get("main_width", 0.55), weight=800)
    box = draw_centered(img, o["main"], main_f, W / 2, H * y, color, shadow_of(o))
    mh = box[3] - box[1]
    if o.get("top"):
        top_f = fit_font(SERIF, o["top"], W * o.get("top_width", 0.34), weight=400)
        draw_centered(img, o["top"], top_f, W / 2, box[1] - mh * 0.30, color, shadow_of(o))
    if o.get("bottom"):
        bot_f = font(SERIF, top_f.size * 0.62 if o.get("top") else mh * 0.3, 400)
        d = ImageDraw.Draw(img)
        l, t, r, b = d.textbbox((0, 0), o["bottom"], font=bot_f)
        # right edge pokes slightly past "Highend", sitting on its baseline (overlap is intended)
        x = box[2] + W * 0.075 - (r - l) - l
        yy = box[3] - (b - t) * 0.85 - t
        sh = shadow_of(o)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((x, yy + sh["dy"]), o["bottom"], font=bot_f, fill=sh["color"])
        img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(sh["blur"])))
        d = ImageDraw.Draw(img)
        d.text((x, yy), o["bottom"], font=bot_f, fill=color)
    return img


def overlay_product(W, H, o, part="both"):
    """Brand wordmark (dark, centred) + white sans product name below it."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    y_logo = o.get("y", 0.115)
    logo_bottom = H * y_logo
    # layout is computed on a scratch layer so the name sits in the same place
    # whether the logo is drawn on this layer or on its own (staggered) layer
    scratch = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if o.get("logo"):
        logo = Image.open(o["logo"]).convert("RGBA")
        w = int(W * o.get("logo_width", 0.40))
        logo = logo.resize((w, int(logo.height * w / logo.width)), Image.LANCZOS)
        x, yy = (W - w) // 2, int(H * y_logo - logo.height / 2)
        scratch.alpha_composite(logo, (x, yy))
        logo_bottom = yy + logo.height
    elif o.get("brand"):
        f = fit_font(DIDONE, o["brand"], W * o.get("logo_width", 0.40), weight=500)
        box = draw_centered(scratch, o["brand"], f, W / 2, H * y_logo,
                            tuple(o.get("brand_color", [40, 38, 36, 255])))
        logo_bottom = box[3]
    if part in ("both", "logo"):
        img.alpha_composite(scratch)
    if part in ("both", "name") and o.get("name"):
        size = W * o.get("name_size", 0.045)
        f = font(SANS, size)
        if f.getbbox(o["name"])[2] > W * 0.9:
            f = fit_font(SANS, o["name"], W * 0.9, start=int(size))
        draw_centered(img, o["name"], f, W / 2, logo_bottom + H * 0.028,
                      (255, 255, 255, 255), shadow_of(o))
    return img


def overlay_sticker(W, H, o):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s = Image.open(o["image"]).convert("RGBA")
    w = int(W * o.get("w", 0.2))
    s = s.resize((w, int(s.height * w / s.width)), Image.LANCZOS)
    cx, cy = W * o.get("x", 0.3), H * o.get("y", 0.12)
    img.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))
    return img


def overlay_caption(W, H, o):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = font(SANS, W * o.get("size", 0.045))
    draw_centered(img, o["text"], f, W / 2, H * o.get("y", 0.2),
                  tuple(o.get("color", [255, 255, 255, 255])), shadow_of(o))
    return img


def build_overlays(plan, W, H, fps, tmp):
    """Returns list of (png_path, start, end)."""
    out = []
    frame = 1.0 / fps
    for i, o in enumerate(plan.get("overlays", [])):
        s, e = float(o["start"]), float(o["end"])
        t = o["type"]
        if t == "title":
            imgs = [(overlay_title(W, H, o), s, e)]
        elif t == "product":
            st = o.get("stagger_frames", 1) * frame  # logo lands 1 frame before the name
            imgs = [(overlay_product(W, H, o, "logo"), s, e),
                    (overlay_product(W, H, o, "name"), s + st, e)]
        elif t == "sticker":
            imgs = [(overlay_sticker(W, H, o), s, e)]
        elif t == "caption":
            imgs = [(overlay_caption(W, H, o), s, e)]
        else:
            sys.exit(f"unknown overlay type: {t}")
        for j, (im, a, b) in enumerate(imgs):
            p = os.path.join(tmp, f"ov_{i}_{j}.png")
            im.save(p)
            out.append((p, a, b))
    return out


def normalize_clip(c, idx, W, H, fps, tmp):
    src = c["src"]
    t_in, t_out = float(c.get("in", 0)), c.get("out")
    dst = os.path.join(tmp, f"clip_{idx:04d}.mov")
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
          f"setsar=1,fps={fps}")
    if c.get("hflip"):
        vf = "hflip," + vf  # selfie-camera footage is mirrored: un-mirror so logos read correctly
    if c.get("speed"):
        vf += f",setpts=PTS/{float(c['speed'])}"
    if c.get("grade", True):
        # soft warm-neutral "beige daylight" look of the reference
        vf += ",eq=contrast=0.97:saturation=0.92:brightness=0.01,colorbalance=rm=0.03:bm=-0.03"
    # Every segment is cut to an exact whole number of frames, and its audio to exactly the
    # same length in PCM. (AAC intermediates get ~20 ms of padding per segment; across dozens of
    # 0.25 s montage shots that drifts the voice 0.5 s+ out of lip-sync.)
    speed = float(c.get("speed") or 1.0)
    src_dur = (float(t_out) if t_out is not None else float(run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src]))) - t_in
    n_frames = max(1, round(src_dur / speed * fps))
    n_samples = round(n_frames / fps * 48000)
    cmd = ["ffmpeg", "-y", "-v", "error", "-ss", str(t_in), "-t", f"{src_dur + 0.2:.3f}", "-i", src]
    audio = has_audio(src) and not c.get("mute")
    if not audio:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    af = []
    if audio and speed != 1.0:
        af.append(f"atempo={speed}")
    af += ["aresample=48000", "aformat=channel_layouts=stereo", "apad",
           f"atrim=end_sample={n_samples}", "asetpts=PTS-STARTPTS"]
    cmd += ["-vf", vf, "-af", ",".join(af), "-map", "0:v:0", "-map", "0:a:0" if audio else "1:a:0",
            "-frames:v", str(n_frames), "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
            "-pix_fmt", "yuv420p", "-video_track_timescale", str(fps * 512), "-c:a", "pcm_s16le", dst]
    run(cmd)
    return dst


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    plan_path = sys.argv[1]
    preview = "--preview" in sys.argv
    with open(plan_path) as fh:
        plan = json.load(fh)
    base_dir = os.path.dirname(os.path.abspath(plan_path))

    def p(x):
        return x if os.path.isabs(x) else os.path.join(base_dir, x)

    for c in plan["clips"]:
        c["src"] = p(c["src"])
        c.setdefault("hflip", plan.get("hflip", False))
    for v in plan.get("voiceovers", []):
        v["src"] = p(v["src"])
    # "sfx" on an overlay = a sound the moment it pops in ("pop", "ding", "whoosh" or a file path)
    SFX = os.path.join(HERE, "..", "assets", "sfx")
    for o in plan.get("overlays", []):
        if o.get("sfx"):
            f = o["sfx"]
            f = os.path.join(SFX, f + ".wav") if os.path.exists(os.path.join(SFX, f + ".wav")) else p(f)
            plan.setdefault("voiceovers", []).append(
                {"src": f, "in": 0, "out": 5, "start": float(o["start"]) + float(o.get("sfx_offset", 0)),
                 "volume": o.get("sfx_volume", 0.35)})
    for o in plan.get("overlays", []):
        for k in ("logo", "image"):
            if o.get(k):
                o[k] = p(o[k])

    W, H = plan.get("width", 1080), plan.get("height", 1920)
    fps = plan.get("fps", 30)
    output = p(plan.get("output", "out.mp4"))
    tmp = tempfile.mkdtemp(prefix="hue_")
    try:
        parts = [normalize_clip(c, i, W, H, fps, tmp) for i, c in enumerate(plan["clips"])]
        lst = os.path.join(tmp, "list.txt")
        with open(lst, "w") as fh:
            fh.writelines(f"file '{x}'\n" for x in parts)
        base = os.path.join(tmp, "base.mov")
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
             "-c", "copy", base])

        ovs = build_overlays(plan, W, H, fps, tmp)
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", base]
        for png, _, _ in ovs:
            cmd += ["-loop", "1", "-framerate", str(fps), "-i", png]
        music = plan.get("music")
        if music:
            cmd += ["-stream_loop", "-1", "-i", p(music)]
        # voiceovers: audio taken from a source file and laid over muted montage clips
        vos = plan.get("voiceovers", [])
        for v in vos:
            cmd += ["-ss", str(v["in"]), "-to", str(v["out"]), "-i", p(v["src"])]
        chain, last = [], "0:v"
        for k, (_, a, b) in enumerate(ovs, start=1):
            nxt = f"v{k}"
            chain.append(f"[{last}][{k}:v]overlay=0:0:shortest=1:"
                         f"enable='between(t,{a:.3f},{b:.3f})'[{nxt}]")
            last = nxt
        if not chain:
            chain.append("[0:v]null[v0]")
            last = "v0"
        mix = ["[0:a]"]
        nxt_in = len(ovs) + 1
        if music:
            vol = plan.get("music_volume", 0.12)
            chain.append(f"[{nxt_in}:a]volume={vol}[bg]")
            mix.append("[bg]")
            nxt_in += 1
        for k, v in enumerate(vos):
            ms = int(round(float(v["start"]) * 1000))
            chain.append(f"[{nxt_in + k}:a]aresample=48000,aformat=channel_layouts=stereo,"
                         f"volume={v.get('volume', 1.0)},adelay={ms}|{ms}[vo{k}]")
            mix.append(f"[vo{k}]")
        if len(mix) > 1:
            chain.append("".join(mix) + f"amix=inputs={len(mix)}:duration=first:"
                         "dropout_transition=0:normalize=0[amx]")
        else:
            chain.append("[0:a]anull[amx]")
        # TikTok/Reels play back around -14 LUFS; phone voice recordings are often far quieter
        if plan.get("loudnorm", True):
            chain.append("[amx]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
        else:
            chain.append("[amx]anull[aout]")
        amap = "[aout]"
        cmd += ["-filter_complex", ";".join(chain), "-map", f"[{last}]", "-map", amap,
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", output]
        run(cmd)
        print("wrote", output)
        if preview:
            sheet = os.path.splitext(output)[0] + "_sheet.jpg"
            run(["ffmpeg", "-y", "-v", "error", "-i", output, "-vf",
                 "fps=2,scale=180:-1,drawtext=text='%{pts\\:flt}':fontcolor=red:fontsize=14:x=4:y=4,"
                 "tile=8x6", "-frames:v", "1", sheet])
            print("wrote", sheet)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
