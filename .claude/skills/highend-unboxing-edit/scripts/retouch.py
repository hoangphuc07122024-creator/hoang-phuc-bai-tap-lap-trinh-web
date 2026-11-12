#!/usr/bin/env python3
"""Natural beauty retouch for talking-head footage, tracked per frame with MediaPipe Face Landmarker.

  * skin smoothing  - edge-preserving blur on the skin only (eyes, brows, lips, nostrils excluded),
                      blended partially so pores/texture stay ("da mịn tự nhiên", not plastic)
  * blemish removal - moles/spots given as positions relative to 3 face landmarks, inpainted every frame
  * hairline fill   - darkens visible scalp at the hair parting / thin hairline toward the hair colour
  * natural makeup  - soft rosy lip tint + light blush + slight under-eye brightening

Usage (as a filter on a rendered base video, BEFORE text overlays are added):
  python3 retouch.py in.mov out.mov config.json
  python3 retouch.py --still in.png out.png config.json      # preview on one frame
  python3 retouch.py --locate frame.png X Y                   # print the landmark-relative "spot" for a blemish at pixel X,Y

config.json (all keys optional):
  {"model": "face_landmarker.task", "smooth": 0.55, "lip_tint": 0.22, "blush": 0.10,
   "hairline": 0.6, "spots": [{"tri": [61, 291, 0], "bary": [a, b, c], "r": 0.075}]}
  r = spot radius as a fraction of mouth width (landmarks 61-291).
"""
import json, os, subprocess, sys
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions, vision

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODEL = os.path.join(HERE, "..", "assets", "models", "face_landmarker.task")

FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377,
             152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
L_EYE = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
R_EYE = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]
L_BROW = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]
R_BROW = [300, 293, 334, 296, 336, 285, 295, 282, 283, 276]
LIPS_OUT = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]
LIPS_IN = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
NOSTRILS = [[98, 97, 2, 326, 327, 294, 278, 344, 440, 275, 4, 45, 220, 115, 48, 64]]


def make_landmarker(model):
    return vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model), running_mode=vision.RunningMode.IMAGE,
        num_faces=1, min_face_detection_confidence=0.5, min_face_presence_confidence=0.5))


def landmarks(lm, bgr):
    H, W = bgr.shape[:2]
    r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)))
    if not r.face_landmarks:
        return None
    return np.array([[p.x * W, p.y * H] for p in r.face_landmarks[0]], np.float32)


def poly_mask(shape, pts, feather):
    m = np.zeros(shape[:2], np.float32)
    cv2.fillPoly(m, [pts.astype(np.int32)], 1.0)
    if feather > 0:
        k = int(feather) * 2 + 1
        m = cv2.GaussianBlur(m, (k, k), feather / 2)
    return m


def spot_xy(P, s):
    a, b, c = s["tri"]
    w = np.array(s["bary"], np.float32)
    return w[0] * P[a] + w[1] * P[b] + w[2] * P[c]


def locate(P, x, y, tri=(61, 291, 0)):
    A = np.array([[P[tri[0]][0], P[tri[1]][0], P[tri[2]][0]],
                  [P[tri[0]][1], P[tri[1]][1], P[tri[2]][1]], [1, 1, 1]], np.float64)
    return np.linalg.solve(A, [x, y, 1]).round(4).tolist()


def retouch(img, P, cfg):
    H, W = img.shape[:2]
    out = img.astype(np.float32)
    mouth_w = float(np.linalg.norm(P[61] - P[291]))
    face_w = float(np.linalg.norm(P[234] - P[454]))
    # work on a padded face box only (speed)
    x0, y0 = np.maximum(P.min(0) - [face_w * 0.35, face_w * 0.6], 0).astype(int)   # extra headroom for the hairline
    x1, y1 = np.minimum(P.max(0) + face_w * 0.35, [W, H]).astype(int)
    if x1 - x0 < 40 or y1 - y0 < 40:
        return img
    roi = out[y0:y1, x0:x1]
    Q = P - [x0, y0]
    f = max(3, face_w * 0.02)

    # 1) blemishes - inpaint before smoothing so the patch gets smoothed with the skin
    spots = cfg.get("spots", [])
    if spots:
        u8 = np.clip(roi, 0, 255).astype(np.uint8)
        mask = np.zeros(u8.shape[:2], np.uint8)
        for s in spots:
            cx, cy = spot_xy(Q, s)
            cv2.circle(mask, (int(round(cx)), int(round(cy))), max(2, int(round(s.get("r", 0.07) * mouth_w))), 255, -1)
        fixed = cv2.inpaint(u8, mask, max(3, int(mouth_w * 0.06)), cv2.INPAINT_TELEA).astype(np.float32)
        soft = cv2.GaussianBlur(mask.astype(np.float32) / 255, (0, 0), max(1.5, mouth_w * 0.02))[..., None]
        soft = np.clip(soft * 1.6, 0, 1)
        roi = roi * (1 - soft) + fixed * soft

    # 2) skin mask
    skin = poly_mask(roi.shape, Q[FACE_OVAL], f * 1.5)
    holes = np.zeros_like(skin)
    for part in (L_EYE, R_EYE, L_BROW, R_BROW, LIPS_OUT):
        holes = np.maximum(holes, poly_mask(roi.shape, Q[part], 0))
    holes = cv2.dilate(holes, np.ones((int(f * 1.2) | 1, int(f * 1.2) | 1), np.uint8))
    holes = cv2.GaussianBlur(holes, (0, 0), f * 0.8)
    skin = np.clip(skin - holes, 0, 1)

    # 3) smoothing: bilateral (edge-preserving) low-pass, keep part of the fine texture
    s = cfg.get("smooth", 0.55)
    if s > 0:
        u8 = np.clip(roi, 0, 255).astype(np.uint8)
        d = int(max(5, face_w * 0.025)) | 1
        smooth = cv2.bilateralFilter(u8, d, 28, d * 0.8).astype(np.float32)
        smooth = cv2.bilateralFilter(np.clip(smooth, 0, 255).astype(np.uint8), d, 18, d * 0.8).astype(np.float32)
        grain = roi - cv2.GaussianBlur(roi, (0, 0), 1.0)        # finest pore detail
        smooth = smooth + grain * 0.35
        roi = roi + (smooth - roi) * (skin[..., None] * s)

    # 4) natural makeup
    lt = cfg.get("lip_tint", 0.22)
    if lt > 0:
        lip = np.clip(poly_mask(roi.shape, Q[LIPS_OUT], f * 0.6) - poly_mask(roi.shape, Q[LIPS_IN], f * 0.3), 0, 1)
        tint = np.array(cfg.get("lip_color", [96, 86, 206]), np.float32)  # BGR: soft rosy pink
        lum = roi.mean(2, keepdims=True) / 255
        colored = tint * (0.55 + 0.6 * lum)                   # keep lip shading
        roi = roi + (colored - roi) * (lip[..., None] * lt)
    bl = cfg.get("blush", 0.10)
    if bl > 0:
        bm = np.zeros(roi.shape[:2], np.float32)
        for c_idx, e_idx in ((50, 117), (280, 346)):
            c = (Q[c_idx] * 0.7 + Q[e_idx] * 0.3)
            cv2.ellipse(bm, (int(c[0]), int(c[1])), (int(face_w * 0.11), int(face_w * 0.075)), 0, 0, 360, 1.0, -1)
        bm = cv2.GaussianBlur(bm, (0, 0), face_w * 0.05) * skin
        pink = np.array(cfg.get("blush_color", [150, 140, 235]), np.float32)
        roi = roi + (roi * pink / 255 * 1.12 - roi) * (bm[..., None] * bl * 3)
    ue = cfg.get("under_eye", 0.06)
    if ue > 0:
        um = np.zeros(roi.shape[:2], np.float32)
        for a, b in ((145, 119), (374, 348)):
            c = (Q[a] + Q[b]) / 2
            cv2.ellipse(um, (int(c[0]), int(c[1])), (int(face_w * 0.07), int(face_w * 0.03)), 0, 0, 360, 1.0, -1)
        um = cv2.GaussianBlur(um, (0, 0), face_w * 0.025) * skin
        roi = roi + (255 - roi) * (um[..., None] * ue)

    # 5) hairline / parting fill: find where hair starts above the forehead, then fill visible
    #    scalp only INSIDE the hair (above that line) - never touches forehead skin
    hl = cfg.get("hairline", 0.6)
    if hl > 0:
        g = cv2.cvtColor(np.clip(roi, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
        up = Q[10] - Q[152]; face_h = float(np.linalg.norm(up)); up /= (face_h + 1e-6)
        r = max(2, int(face_w * 0.02))
        def lum(pt):
            x, y = int(pt[0]), int(pt[1])
            if not (r <= x < g.shape[1] - r and r <= y < g.shape[0] - r):
                return None
            return float(np.median(g[y - r:y + r, x - r:x + r]))
        skin_l = lum(Q[151]) or 200
        h0, run = None, 0
        for k in range(1, 60):
            pt = Q[10] + up * face_h * 0.01 * k
            v = lum(pt)
            if v is None:
                break
            run = run + 1 if v < skin_l * 0.62 else 0
            if run >= 2:
                h0 = Q[10] + up * face_h * 0.01 * (k - 1)
                break
        if h0 is not None:
            c = h0 + up * face_h * cfg.get("hairline_up", 0.07)
            ang = float(np.degrees(np.arctan2(up[1], up[0]))) + 90
            zone = np.zeros(g.shape, np.float32)
            cv2.ellipse(zone, (int(c[0]), int(c[1])), (int(face_w * cfg.get("hairline_w", 0.28)), int(face_h * cfg.get("hairline_h", 0.10))),
                        ang, 0, 360, 1.0, -1)
            # keep only the side of the hairline that is hair
            yy, xx = np.mgrid[0:g.shape[0], 0:g.shape[1]]
            dist_up = (xx - h0[0]) * up[0] + (yy - h0[1]) * up[1]
            zone *= np.clip(dist_up / (face_h * 0.02) , 0, 1)
            zone = cv2.GaussianBlur(zone, (0, 0), face_w * 0.012)
            zb = zone > 0.3
            if zb.sum() > 50:
                hair_l = np.percentile(g[zb], 15)
                hair_col = np.median(roi[zb & (g <= np.percentile(g[zb], 25))], 0)
                # "inside the head" per column: from the top edge of the main hair mass down to the
                # hairline. Thin stray hairs / lamps on the wall are removed by an opening first, so
                # the parting "V" and thin spots get filled but the background never does.
                thr = hair_l + 0.45 * max(skin_l - hair_l, 20)
                hair = ((g < thr) & (zone > 0.02)).astype(np.uint8)
                # cut flyaways/lamps loose from the hair mass, keep the main mass, then close it so the
                # parting "V" and thin spots become part of it; fill = bright pixels in that region
                ko = max(3, int(face_w * cfg.get("hair_open", 0.035))) | 1
                hair = cv2.morphologyEx(hair, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ko, ko)))
                n, lab, st, _ = cv2.connectedComponentsWithStats(hair, 8)
                inside = np.zeros(g.shape, np.float32)
                if n > 1:
                    main = (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
                    kc = max(5, int(face_w * cfg.get("hair_close", 0.12))) | 1
                    closed = cv2.morphologyEx(main, cv2.MORPH_CLOSE,
                                              cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kc, kc))).astype(np.float32)
                    # and never above the (smoothed) top edge of the head: closing can bridge the
                    # concavity between a flyaway and the head, which is background
                    has = main.any(0)
                    top_row = np.where(has, main.argmax(0), g.shape[0]).astype(np.float32)
                    w = max(5, int(face_w * cfg.get("hair_top_window", 0.5))) | 1
                    med = np.array([np.median(top_row[max(0, i - w // 2):i + w // 2 + 1]) for i in range(len(top_row))])
                    top_row = np.maximum(top_row, med) + face_w * 0.01
                    inside = closed * (yy >= top_row[None, :])
                # scalp shows up clearly brighter than both hair and shadowed background
                rng = max(skin_l - hair_l, 20)
                lo, hi = cfg.get("scalp_lo", 0.3), cfg.get("scalp_hi", 0.6)
                bright = np.clip((g - (hair_l + lo * rng)) / ((hi - lo) * rng), 0, 1)
                scalp = cv2.GaussianBlur(inside * bright, (0, 0), max(1.0, face_w * 0.006))
                strand = np.clip(g / (skin_l + 1e-6), 0, 1)[..., None]
                target = hair_col * (0.9 + 0.25 * strand)
                a = (zone * scalp * hl)[..., None]
                roi = roi * (1 - a) + target * a

    out[y0:y1, x0:x1] = roi
    return np.clip(out, 0, 255).astype(np.uint8)


class Smoother:
    """EMA on landmarks to kill jitter; resets on cuts / big jumps."""
    def __init__(self, a=0.55):
        self.a, self.prev = a, None

    def __call__(self, P):
        if P is None:
            self.prev = None
            return None
        if self.prev is None or np.abs(P - self.prev).mean() > 12:
            self.prev = P
        else:
            self.prev = self.a * P + (1 - self.a) * self.prev
        return self.prev


def process_video(src, dst, cfg):
    W, H = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                    "stream=width,height", "-of", "csv=p=0", src],
                                   capture_output=True, text=True).stdout.strip().split(","))
    fps = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=r_frame_rate", "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip()
    rd = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                          stdout=subprocess.PIPE)
    wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                           "-r", fps, "-i", "-", "-i", src, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264",
                           "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
                           "-video_track_timescale", str(int(eval(fps)) * 512), "-c:a", "copy", dst],
                          stdin=subprocess.PIPE)
    lm = make_landmarker(cfg.get("model", DEFAULT_MODEL))
    sm = Smoother()
    n = 0
    scale = cfg.get("detect_scale", 0.5)
    while True:
        buf = rd.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        small = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        P = landmarks(lm, small)
        P = sm(None if P is None else P / scale)
        out = retouch(img, P, cfg) if P is not None else img
        wr.stdin.write(out.tobytes())
        n += 1
        if n % 300 == 0:
            print(f"retouch: {n} frames", flush=True)
    wr.stdin.close(); wr.wait(); rd.wait()
    print(f"retouch: done, {n} frames")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--locate":
        img = cv2.imread(a[1]); lm = make_landmarker(DEFAULT_MODEL)
        P = landmarks(lm, img)
        print(json.dumps({"tri": [61, 291, 0], "bary": locate(P, float(a[2]), float(a[3]))}))
    elif a and a[0] == "--still":
        cfg = json.load(open(a[3])) if len(a) > 3 else {}
        img = cv2.imread(a[1]); lm = make_landmarker(cfg.get("model", DEFAULT_MODEL))
        P = landmarks(lm, img)
        cv2.imwrite(a[2], retouch(img, P, cfg) if P is not None else img)
    else:
        process_video(a[0], a[1], json.load(open(a[2])) if len(a) > 2 else {})
