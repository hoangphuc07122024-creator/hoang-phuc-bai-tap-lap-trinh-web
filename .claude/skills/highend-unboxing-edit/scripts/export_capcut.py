#!/usr/bin/env python3
"""Export a render plan as a CapCut-ready package, so the user can keep editing by hand.

  python3 export_capcut.py plan.json out_dir [clean_video.mp4]

out_dir gets:
  video_sach_khong_chu.mp4   cut + retouched + voice-mixed video WITHOUT any text (render the plan with
                             "overlays": [] to make it, then pass it as the 3rd argument)
  phu_de.srt                 every caption, importable in CapCut (Text > Local captions / Import captions)
  lop_chu/NN_<start>-<end>_<type>.png   each title / label / sticker as a full 1080x1920 transparent PNG:
                             drop on an overlay track at <start>, stretch to <end>, no positioning needed
  sticker_goc/               the raw sticker images (to resize / move freely)
  am_thanh/                  the SFX files used
  moc_thoi_gian.csv          timeline of every overlay
  HUONG_DAN_CAPCUT.txt       step-by-step instructions in Vietnamese
"""
import csv, json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render  # noqa: E402


def ts(t, sep=","):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def main():
    plan_path, out = sys.argv[1], sys.argv[2]
    clean = sys.argv[3] if len(sys.argv) > 3 else None
    plan = json.load(open(plan_path))
    base_dir = os.path.dirname(os.path.abspath(plan_path))
    p = lambda x: x if os.path.isabs(x) else os.path.join(base_dir, x)
    W, H = plan.get("width", 1080), plan.get("height", 1920)
    os.makedirs(os.path.join(out, "lop_chu"), exist_ok=True)
    os.makedirs(os.path.join(out, "sticker_goc"), exist_ok=True)
    os.makedirs(os.path.join(out, "am_thanh"), exist_ok=True)
    if clean and os.path.abspath(clean) != os.path.abspath(os.path.join(out, "video_sach_khong_chu.mp4")):
        shutil.copy(clean, os.path.join(out, "video_sach_khong_chu.mp4"))

    ovs = sorted(plan.get("overlays", []), key=lambda o: o["start"])
    caps = [o for o in ovs if o["type"] == "caption"]
    with open(os.path.join(out, "phu_de.srt"), "w", encoding="utf-8") as fh:
        for i, o in enumerate(caps, 1):
            fh.write(f"{i}\n{ts(o['start'])} --> {ts(o['end'])}\n{o['text'].replace('*', '')}\n\n")

    rows, n = [], 0
    for o in ovs:
        if o["type"] == "caption":
            continue
        o = dict(o)
        for k in ("logo", "image"):
            if o.get(k):
                o[k] = p(o[k])
        if o["type"] == "title":
            im, what = render.overlay_title(W, H, o), " / ".join(x for x in (o.get("top"), o.get("main"), o.get("bottom")) if x)
        elif o["type"] == "product":
            im, what = render.overlay_product(W, H, o, "both"), f"{o.get('brand', '')} - {o.get('name', '')}"
        elif o["type"] == "sticker":
            im, what = render.overlay_sticker(W, H, o), os.path.basename(o["image"])
            shutil.copy(o["image"], os.path.join(out, "sticker_goc", os.path.basename(o["image"])))
        else:
            continue
        n += 1
        name = f"{n:02d}_{o['start']:07.2f}-{o['end']:07.2f}_{o['type']}.png"
        im.save(os.path.join(out, "lop_chu", name))
        sfx = o.get("sfx", "")
        if sfx:
            f = os.path.join(HERE, "..", "assets", "sfx", sfx + ".wav")
            if os.path.exists(f):
                shutil.copy(f, os.path.join(out, "am_thanh", sfx + ".wav"))
        rows.append([n, ts(o["start"], "."), ts(o["end"], "."), round(o["end"] - o["start"], 2), o["type"], what, name, sfx])
    with open(os.path.join(out, "moc_thoi_gian.csv"), "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["#", "bat_dau", "ket_thuc", "do_dai_s", "loai", "noi_dung", "file_png", "tieng"])
        w.writerows(rows)
    if not os.listdir(os.path.join(out, "am_thanh")):
        os.rmdir(os.path.join(out, "am_thanh"))

    guide = f"""HƯỚNG DẪN SỬA TIẾP TRONG CAPCUT
================================
Khung hình: 9:16, 1080x1920, 30fps.

1. Tạo dự án mới > Nhập "video_sach_khong_chu.mp4" (đã cắt, đã chỉnh mặt, đã có tiếng nói, CHƯA có chữ).
   Kéo vào dòng thời gian chính, bắt đầu ở 00:00.

2. Phụ đề ({len(caps)} dòng): Văn bản (Text) > Phụ đề cục bộ / Nhập phụ đề (Import captions) > chọn "phu_de.srt".
   Sau đó chọn tất cả phụ đề để đổi kiểu chữ một lần (gợi ý: Be Vietnam Pro / Montserrat SemiBold, trắng,
   bóng đổ mềm, vị trí ngang ngực ~53% chiều cao). Từ khoá có thể tô màu hồng nhạt #FFB6DE thủ công.

3. Tiêu đề, nhãn sản phẩm, sticker: thư mục "lop_chu".
   Mỗi file là ảnh PNG trong suốt full khung 1080x1920 -> kéo vào track Lớp phủ (Overlay), để "Vừa khung" (Fit),
   KHÔNG cần căn vị trí. Tên file ghi sẵn giây bắt đầu và kết thúc, ví dụ
   "02_0010.07-0013.47_product.png" = đặt ở 10.07s, kéo dài tới 13.47s.
   Animation vào/ra: KHÔNG (để giữ kiểu chữ "bật" cứng như video mẫu).
   Muốn tự đổi chữ: dùng moc_thoi_gian.csv để biết nội dung và gõ lại bằng Text của CapCut.

4. Sticker gốc (để tự phóng to/di chuyển): thư mục "sticker_goc".

5. Tiếng hiệu ứng: bản này đang TẮT. Nếu muốn thêm, kéo file trong "am_thanh" (nếu có) vào track âm thanh
   đúng giây bắt đầu của lớp chữ/sticker, âm lượng ~20%.

6. Xuất: 1080p, 30fps.
"""
    open(os.path.join(out, "HUONG_DAN_CAPCUT.txt"), "w", encoding="utf-8").write(guide)
    print(f"exported {n} overlays, {len(caps)} captions -> {out}")


if __name__ == "__main__":
    main()
