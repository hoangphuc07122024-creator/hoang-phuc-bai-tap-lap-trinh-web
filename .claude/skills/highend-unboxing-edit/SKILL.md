---
name: highend-unboxing-edit
description: Dựng/edit video dọc 9:16 theo phong cách "Unboxing Highend Beauty" (TikTok/Reels mỹ phẩm cao cấp) — hook montage cắt nhanh, title serif 3 tầng (Unboxing / Highend / Beauty), nhãn sản phẩm logo + tên, sticker nguyên liệu nhảy theo lời nói, jump cut talking-head, chuyển cảnh cắt cứng. Dùng khi người dùng muốn edit video review/unboxing mỹ phẩm, nước hoa, đồ luxury, hoặc nói "edit theo style highend", "chữ nhảy như video mẫu", "làm video unboxing sang chảnh". Có script ffmpeg để tự render từ footage, và công thức làm tay trong CapCut.
---

# Highend Unboxing Edit

Phong cách học từ video mẫu (TikTok 50s, 576×1024, 30fps, review Dior/Chanel/Guerlain).
Chi tiết từng giây của video mẫu: `references/reference-breakdown.md`.

## Tinh thần của style (đọc trước khi làm)

1. **Sang nhờ sự tiết chế.** Không transition, không zoom, không fade, không chữ chạy. Mọi
   cú cắt là *hard cut*; mọi chữ/sticker **"nhảy" vào và biến mất đúng 1 khung hình** —
   đó chính là "hiệu ứng nhảy chữ" của video mẫu: chữ bật lên đúng lúc người nói nhắc tới.
2. **Nhịp 2 tốc độ.** Mở đầu cực nhanh (cảnh 0.2–0.4s) để giữ người xem, sau đó chậm hẳn
   (talking-head 2–6s/đoạn) để tạo cảm giác tin cậy, sang trọng.
3. **Chữ luôn ở 1/4 trên khung hình**, phía trên đầu người nói, căn giữa, không che mặt/sản phẩm.
4. **Typography kiểu tạp chí thời trang:** serif tương phản cao + sans gọn cho thông tin.
5. **Màu tự nhiên, ánh sáng ban ngày, tông be/kem ấm**, hơi giảm bão hoà. Không filter nặng.

## Cấu trúc timeline (template ~50s)

| Đoạn | Thời lượng | Nội dung | Cách cắt |
|---|---|---|---|
| Hook montage 1 | 0 → ~1.8s | 6–7 cảnh B-roll mở hộp, cầm hộp lên khoe | mỗi cảnh **0.2–0.33s**, hard cut, ưu tiên cắt khi tay đang chuyển động |
| Teaser A-roll | ~1.8 → 4.5s | Người nói dùng thử sản phẩm (đánh má, thoa son) + nói câu hook | 1 cảnh liền |
| Hook montage 2 | ~4.5 → 6.7s | 5–6 cảnh B-roll khác (mở nắp, xé giấy, cận hộp) | mỗi cảnh **0.2–0.45s** |
| Title card | ~6.9 → 9.5s | Talking-head + **TITLE 3 tầng** | title bật vào cứng, giữ ~2.6s |
| Sản phẩm #1 | 9.6 → … | Nhãn **LOGO + tên sản phẩm** giữ ~3s ngay khi bắt đầu nói về sản phẩm | nhãn thay title *ngay frame kế* (không khoảng trống) |
| Review | … | Talking-head cầm sản phẩm, xoay, mở nắp | jump cut mỗi 1–6s, cắt bỏ khoảng ngừng; **không** punch-in zoom |
| Nhắc nguyên liệu/mùi | 0.25–0.45s mỗi cái | **Sticker PNG** (chai nước hoa, hoa hồng, hoa nhài…) bật lên đúng từ khoá | chuỗi sticker liên tiếp, cách nhau 0.1–0.3s |
| Sản phẩm #2, #3… | ~3s nhãn | Lặp lại: nhãn LOGO + tên ngay frame cắt sang sản phẩm mới | nhãn xuất hiện trùng frame cắt |

## Thông số chữ (tính theo % khung 9:16, đo từ video mẫu)

**Title 3 tầng** (trắng, không viền, bóng đổ rất mờ):
- Dòng 1 `Unboxing` — serif thường, nét mảnh (Playfair Display 400), rộng ≈ **34%** khung, tâm y ≈ 12%.
- Dòng 2 `Highend` — serif **đậm nghiêng** tương phản cao (Playfair Display Italic 700–800), rộng ≈ **55%**, tâm y ≈ 17–19%. Sát dòng 1, gần như chạm.
- Dòng 3 `Beauty` — serif thường, nhỏ (~60% cỡ dòng 1), **căn phải, lấn nhẹ ra ngoài mép phải "Highend" và đè lên chân chữ** — chi tiết tạo cảm giác editorial.

**Nhãn sản phẩm:**
- Wordmark/logo thương hiệu màu **than đậm (#28 26 24)**, rộng ≈ **40%**, tâm y ≈ 11–12%. Dùng file logo PNG người dùng cung cấp; nếu không có thì gõ tên thương hiệu bằng font Didone (Bodoni Moda).
- Tên sản phẩm: **sans-serif SemiBold trắng** (Be Vietnam Pro — hỗ trợ đủ dấu tiếng Việt), cỡ ≈ 4.5% chiều rộng khung, ngay dưới logo, bóng đổ mềm. Viết tiếng Việt + tên gốc: *"Son Dưỡng Dior Addict Lip Glow Butter"*.
- Logo xuất hiện **trước tên 0–1 frame**, cả hai biến mất cùng lúc.

**Sticker:** ảnh PNG nền trong suốt (cắt nền sạch), rộng 15–22% khung, đặt ở vùng trống phía trên/cạnh đầu, gần tay đang chỉ. Không viền, không bóng, không animation.

Font gợi ý trong CapCut nếu không có Playfair: *Bodoni*, *Didot*, *Gloock*, *DM Serif Display* (title); *Montserrat SemiBold*, *SVN-Gilroy* (tên SP).

## Quy trình khi người dùng đưa footage

1. **Xem footage:** dựng contact sheet để chọn cảnh
   `ffmpeg -i in.mov -vf "fps=2,scale=180:-1,drawtext=text='%{pts\:flt}':fontcolor=red:fontsize=14,tile=8x6" sheet_%02d.jpg`
   rồi đọc ảnh. Xác định: cảnh B-roll mở hộp (cho hook), đoạn talking-head, thời điểm nhắc tên từng sản phẩm/nguyên liệu.
2. **Hỏi/thu thập** (nếu chưa có): tên thương hiệu + tên sản phẩm (tiếng Việt), logo PNG (nếu có), ảnh sticker nguyên liệu, nhạc nền.
   Không tự tải logo thương hiệu từ Internet; dùng font Didone gõ tên nếu thiếu logo.
3. **Jump cut talking-head:** `python3 scripts/suggest_cuts.py talking.mov` → in ra các đoạn giữ lại (cắt khoảng lặng > 0.35s). Video có nhạc nền to thì tăng `--noise -28` hoặc cắt tay theo transcript.
4. **Viết plan JSON** (mẫu: `scripts/example_plan.json`): danh sách `clips` (nguồn, in, out) theo đúng cấu trúc timeline trên, và `overlays` với thời gian **trên timeline đầu ra**.
   - Thời gian overlay = tổng thời lượng các clip trước đó + vị trí trong clip. Căn sticker đúng lúc nói từ khoá (dùng transcript/nghe audio nếu được, nếu không thì ước lượng và báo người dùng kiểm tra).
5. **Render:** `python3 scripts/render.py plan.json --preview` → ra `out.mp4` 1080×1920 + `out_sheet.jpg` để tự kiểm tra (đọc ảnh sheet: chữ có che mặt không, có đúng 1/4 trên không, hook có đủ nhanh không).
6. Gửi video cho người dùng, kèm danh sách mốc thời gian chữ/sticker để họ tinh chỉnh.

### Plan JSON — các loại overlay

```json
{"type": "title",   "start": 6.9, "end": 9.5, "top": "Unboxing", "main": "Highend", "bottom": "Beauty"}
{"type": "product", "start": 9.6, "end": 12.7, "brand": "Maison", "name": "Kem Dưỡng Tay Le Baume", "logo": "logo.png"}
{"type": "sticker", "start": 43.2, "end": 43.6, "image": "rose.png", "x": 0.3, "y": 0.12, "w": 0.18}
{"type": "caption", "start": 20, "end": 22, "text": "Mùi hương hoa nhài", "y": 0.2}
```
Tuỳ chọn plan: `width/height/fps` (mặc định 1080×1920@30), `music` + `music_volume` (mặc định 0.12),
`loudnorm` (mặc định bật, chuẩn −14 LUFS cho TikTok), `hflip` (lật gương toàn bộ),
`voiceovers` (lồng tiếng), mỗi clip có `speed`, `mute`, `hflip`, `grade: false` (tắt màu be ấm).
Overlay có `"shadow": "strong"` khi nền sáng/rối (trần nhà sáng, kệ cửa hàng). Đường dẫn tương đối tính từ file plan.

```json
"voiceovers": [{"src": "talking.mov", "in": 0.82, "out": 2.62, "start": 0.0, "volume": 1.0}]
```

### Kinh nghiệm từ các lần dựng thực tế
- **Footage quay camera trước thường bị lật gương** (chữ trên hộp/túi đọc ngược). Luôn kiểm tra
  chữ trên sản phẩm trong contact sheet; nếu ngược → `"hflip": true`.
- **Montage bị im lặng là lỗi lớn khi không có nhạc nền.** Dùng J-cut: tắt tiếng clip montage,
  lấy chính câu nói của đoạn talking-head kế tiếp làm `voiceovers` chạy dưới montage, rồi clip
  talking-head bắt đầu từ `in + thời lượng montage` để khẩu hình khớp tiếng.
- **Có nhiều take giống nhau:** transcript tất cả (faster-whisper `medium`, `language="vi"`,
  `word_timestamps=True`), chọn câu nói trôi nhất cho từng ý, cắt theo mốc từng từ. Nếu mô hình
  bị lặp câu (hallucination), chạy lại với `condition_on_previous_text=False` và bỏ `initial_prompt`.
  Tải model bằng `curl` từ `huggingface.co/Systran/faster-whisper-medium/resolve/main/{config.json,model.bin,tokenizer.json,vocabulary.txt}`
  nếu thư viện tải bị treo; nạp audio bằng numpy (đọc file wav 16kHz) nếu PyAV lỗi.
- **Thiếu ảnh sticker:** vẽ sticker phẳng đơn giản bằng Pillow (quả, hoa, ánh lấp lánh) theo đúng từ khoá
  trong lời nói — vẫn đúng tinh thần hơn là bỏ trống.
- Cắt overlay theo **mốc thời gian trên clip nguồn** rồi quy đổi sang timeline đầu ra bằng script
  sinh plan (cộng dồn thời lượng các clip trước) — tránh tính tay sai lệch.

## Công thức làm tay trong CapCut (nếu người dùng tự edit)

1. Canvas 9:16. Kéo B-roll vào, Split cắt mỗi đoạn 6–10 frame (0.2–0.33s), xếp 6–7 đoạn đầu video.
2. Chèn đoạn dùng thử sản phẩm ~2.5s, rồi thêm montage 5–6 cảnh nhanh nữa.
3. Talking-head: dùng *Auto cut / Remove pauses* hoặc cắt tay mọi khoảng ngừng. Không thêm zoom.
4. Text: 3 lớp text riêng (Unboxing / Highend / Beauty) theo thông số trên, **Animation = None** cả In/Out. Bật đúng frame cắt, giữ ~2.5–3s.
5. Nhãn sản phẩm: logo (Overlay PNG) + text tên SP, bắt đầu đúng frame chuyển sang sản phẩm mới, giữ ~3s.
6. Sticker nguyên liệu: Overlay PNG, dài 8–13 frame, đặt đúng từ khoá. Không animation.
7. Không dùng transition nào giữa các clip. Filter: giảm saturation ~-8, nhiệt độ +3–5.
8. Nhạc: nhạc nền nhẹ (lo-fi/acoustic/jazz sang), để thấp dưới giọng nói.

## Những điều KHÔNG làm (sẽ phá style)
- Transition (dissolve, slide, zoom, glitch), chữ typewriter/bounce/scale-in, chữ có viền dày/nền màu.
- Phụ đề chạy liên tục dưới màn hình (video mẫu không có), emoji, chữ màu neon.
- Đặt chữ giữa hoặc 1/3 dưới khung (vùng UI TikTok + che sản phẩm).
- Hook dài hơn ~0.5s/cảnh.

Font kèm theo trong `assets/fonts/` (Playfair Display, Bodoni Moda, Be Vietnam Pro) đều theo giấy phép SIL OFL 1.1.
