# Phân tích video mẫu (frame-by-frame)

Nguồn: TikTok review mỹ phẩm, 50.2s, 576×1024, 30fps, H.264 + AAC. Âm thanh liên tục
(không có khoảng lặng > 0.4s ở −35 dB) → giọng nói được cắt sát và/hoặc có nhạc nền.

## Mốc cắt cảnh (scene detection)
0.30 · 0.50 · 0.77 · 1.03 · 1.27 · 1.60 · 1.83 · 4.47 · 4.67 · 4.83 · 5.07 · 5.40 · 5.60 · 5.90 ·
6.33 · 6.70 · 9.57 · 21.87 · 23.73 · 26.47 · 32.27 · 33.17 · 39.80 · 40.87 · 44.63 · 46.87

## Timeline
| Thời gian | Hình | Chữ / overlay |
|---|---|---|
| 0.00–0.30 | Kéo hộp ra khỏi túi giấy | — |
| 0.30–0.50 | Xé dải ruy băng đỏ | — |
| 0.50–0.77 | (chuyển động tay) | — |
| 0.77–1.03 | Cầm hộp Chanel Les Beiges khoe | — |
| 1.03–1.27 | Mở nắp hộp | — |
| 1.27–1.60 | Hộp phấn phủ đen nghiêng | — |
| 1.60–1.83 | Hộp phấn đen thẳng | — |
| 1.83–4.47 | Talking-head đánh má hồng bằng cọ, nói câu mở đầu | — |
| 4.47–6.70 | 6 cảnh nhanh: thỏi son, hộp Chanel, hộp Guerlain, bông phấn… | — |
| 6.70–6.87 | Talking-head bắt đầu | — |
| **6.87–9.47** | Talking-head | **TITLE**: "Unboxing" / "*Highend*" / "Beauty" — bật vào 1 frame, giữ 2.6s |
| 9.47–9.57 | (3 frame trống) cắt sang cảnh mới | — |
| **9.57–12.73** | Cầm hộp Dior tròn | **Logo Dior + "Dior Le Baume Hand Cream Limited"** — hiện cùng frame cắt, giữ ~3.2s, biến mất cùng lúc |
| 12.73–43.2 | Talking-head review, mở nắp, xoay sản phẩm; jump cut ở 21.87, 23.73, 26.47, 32.27, 33.17, 39.80, 40.87 | — |
| **43.17–43.60** | Giơ ngón tay "thứ nhất" | **Sticker chai nước hoa** (13 frame) cạnh trái đầu |
| 44.63 | jump cut | — |
| **45.30–45.53** | Nói về hương | **Sticker hoa hồng đỏ** (~7 frame) |
| **45.90–46.23** | | **Sticker hoa trắng 5 cánh** (~10 frame) |
| **46.40–46.83** | | **Sticker cành hoa nhài** (~13 frame) |
| **46.83–49.80** | Cắt sang cầm thỏi son | **Logo Dior** (frame 46.83) → **"Son Dưỡng Dior Addict Lip Glow Butter"** (frame 46.87) — lệch 1 frame, giữ đến hết |

## Quan sát typography
- Title: chữ trắng, "Unboxing" serif mảnh ≈34% bề ngang; "Highend" serif đậm nghiêng kiểu Didone ≈55%;
  "Beauty" serif mảnh nhỏ, căn phải, lấn ra khỏi mép phải và đè lên chân chữ "Highend".
- Nhãn sản phẩm: wordmark thương hiệu màu than đậm ≈40% bề ngang, tâm y ≈12%;
  tên sản phẩm sans-serif đậm vừa, trắng, bóng mềm, tâm y ≈19%, viết tiếng Việt có dấu.
- Không chữ nào có animation: không fade, không trượt, không scale. Toàn bộ là pop in/out cứng.
- Không có phụ đề chạy theo lời nói.

## Quan sát hình ảnh
- Quay điện thoại cố định, góc thấp ngang ngực, nền tường kem + tủ gỗ, ánh sáng cửa sổ tự nhiên.
- Sản phẩm + túi giấy thương hiệu xếp tiền cảnh làm "set" luxury.
- Không zoom/punch-in khi jump cut; không speed ramp.
