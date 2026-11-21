# Bảng tra cảnh (scene patterns)

Rút ra từ video tham khảo (site son tint: treo tag → wordmark → Cacao → Pêche → Framboise → túi).
Mỗi cảnh gồm: **mục đích · dựng thế nào · cuộn bao nhiêu · state cần tween**.

| # | Cảnh | Cao | Mục đích |
|---|------|-----|----------|
| 1 | Intro treo | 180vh | Gợi tò mò: trang gần trống, chỉ có một vật thể |
| 2 | Hero wordmark | 220vh | Thương hiệu xuất hiện, thể hiện chiều sâu 3D |
| 3…N | Chapter biến thể | 260vh mỗi chapter | Giới thiệu từng biến thể sản phẩm |
| ↔ | Wipe màu | 25% đầu mỗi chapter | Chuyển cảnh mạnh, đổi nền |
| N+1 | Bag / checkout | 260vh | Chốt đơn: gộp tất cả vào túi, kèm ưu đãi |

## 1. Intro treo (hanging tag)
- **Dựng:** nền giấy (#f4efe9), vật thể hero treo bằng một sợi dây mảnh (Cylinder r=0.008)
  từ ngoài mép trên màn hình. Chuyển động con lắc:
  `sway = sin(t*1.3)*0.12*S.swing; x += sin(sway)*L; y += (1-cos(sway))*L`.
- Chữ duy nhất trên màn hình là "Scroll" nhỏ ở đáy.
- **Tween:** `S.swing 1→0` (dây biến mất, tức là "đứt dây").
- Biến thể của cảnh này: hang tag bằng giấy xoay chậm, hoặc vật thể quay quanh trục y.

## 2. Hero wordmark
- **Dựng:** wordmark rộng khoảng 12 đơn vị world, nằm ở z=0. Ba vật thể rơi vào ở
  `z = +1.5 / -1.5 / +2`, nghiêng ±0.15–0.5 rad. Tagline nhỏ đặt ở góc trên trái.
- **Tween:** `word.o 0→1`, `word.s .85→1`, và vị trí từng vật thể với các offset thời gian
  0.2 / 0.3 / 0.4 để chúng rơi so le.
- Mẹo: một vật thể phải **cắt ngang** chữ (một nửa trước, một nửa sau) để mắt nhận ra chiều sâu.

## 3. Chapter biến thể
- **Bố cục:** khối copy ở một bên (eyebrow "01 — Chocolate", H2 khổng lồ, mô tả, chips, CTA
  "Add to bag €24"). Bên còn lại là vật thể hero scale 1.35 xoay 360°, đè lên một thẻ social
  proof kiểu bài đăng mạng xã hội.
- **Particle theo nguyên liệu:** cacao → tetrahedron bị bóp dẹt (mảnh sô-cô-la vỡ); đào →
  sphere mịn với roughness 0.6; mâm xôi → icosahedron detail 1 với `flatShading`.
  Dùng 20–30 instance, z từ -4 đến 3, trôi lên chậm và quay.
- **Tween:** `field[i] 0→1` (xuất hiện), hero bay vào, các vật thể khác bay ra
  (`y = ±9`), thẻ fade in tại 0.2, rồi `field[i] →0` tại 0.85.
- Nền đổi bằng `ScrollTrigger.onToggle` → `body.style.backgroundColor` (có CSS transition
  0.2s). Màu nền là tông nhạt của màu biến thể.

## ↔ Wipe màu
- `div#wipe` fixed, z trên canvas. Dùng `clip-path: inset(100% 0 0 0) → inset(0) →
  inset(0 0 100% 0)` (quét từ dưới lên rồi rời đi phía trên).
- Màu wipe là tông **đậm/rực** của biến thể (nâu đậm, cam đào, hồng mâm xôi), nghĩa là
  tương phản với nền nhạt của chính chapter đó.
- `scrub:true`, start `top bottom`, end `top 25%`.

## Bag / checkout
- **Dựng:** túi giấy (Box + nửa Torus làm quai + logo dùng wordmark texture) ở bên phải;
  headline "It's in the bag." ở giữa bên trái; hóa đơn DOM ở góc trên trái có mép răng cưa
  bằng `clip-path polygon`, có barcode bằng `repeating-linear-gradient` và số "−15%" to.
- **Tween:** túi đi lên với `power3.out`. Các vật thể lần lượt bay lên trên miệng túi rồi
  rơi vào với `bounce.out`, offset 0.05 mỗi cái. Hóa đơn in ra với
  `translateY(-140%→0)` và `steps(12)`.
- Nền chuyển sang trung tính lạnh (#eef0ec) để báo hiệu "kết thúc, đến lúc mua".

## Thông số mặc định nên giữ
- Camera: Perspective fov 35, z=14. Đèn: Hemisphere 1.6, key Directional 2.2 (4,6,8), rim 1.2 (-6,2,-4).
- Tone mapping ACESFilmic. Vật liệu: MeshPhysical với clearcoat 1, roughness 0.25–0.35, cho cảm giác bóng mỹ phẩm.
- Font Inter 400/500/800/900. Nav 12px, chữ viết hoa màu muted, logo đậm ở bên trái, nút giỏ tròn ở bên phải.
