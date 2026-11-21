---
name: 3d-scroll-product-site
description: Build a premium, scroll-driven 3D product landing page (Three.js + GSAP ScrollTrigger) in which each scroll section is a "scene": the product hangs or floats, a giant wordmark sits between 3D objects, flavour/variant chapters change with full-screen colour wipes, and the page ends with a "put it in the bag" checkout scene. Use when the user asks for a 3D website, an awwwards-style or "POV: you have mastered 3D websites" style site, a product/cosmetics/food/drink/sneaker landing page with scroll animation, scrollytelling, or (in Vietnamese) "web 3D", "website 3D cuộn", "landing page sản phẩm có hiệu ứng 3D".
---

# 3D Scroll Product Site

Một website sản phẩm mà **thanh cuộn chính là timeline phim**: mỗi đoạn cuộn là một cảnh,
vật thể 3D bay giữa các lớp chữ, màu nền đổi theo biến thể sản phẩm, và trang kết thúc bằng
cảnh "cho vào giỏ". Mẫu khởi đầu chạy được ngay nằm ở `assets/template.html`. Còn
`references/scene-patterns.md` là bảng tra từng cảnh: cách dựng, thời lượng cuộn và lỗi hay gặp.

## Quy trình

1. **Lấy brief (hỏi ngắn hoặc tự chọn mặc định hợp lý):** tên thương hiệu, sản phẩm (hình
   khối gì), 2–4 biến thể (mỗi biến thể có tên, màu chủ đạo và "vật thể đặc trưng", ví dụ
   cacao → mảnh sô-cô-la, đào → quả đào, mâm xôi → quả mâm xôi), CTA cuối và giọng văn.
   Có model `.glb` thật thì dùng `GLTFLoader`; không có thì dựng procedural như trong template.
2. **Viết storyboard trước khi code.** Liệt kê các cảnh theo đúng thứ tự trong
   `references/scene-patterns.md` (Intro treo → Hero wordmark → N Chapter → Wipe giữa các
   chapter → Bag/Checkout). Ghi rõ chiều cao cuộn (vh) của từng cảnh và vật thể nào ở đâu,
   TRƯỚC hay SAU chữ.
3. **Copy `assets/template.html`** vào project, rồi chỉ sửa `BRAND` và `CHAPTERS` ở đầu
   script. Chỉ thêm cảnh mới khi brief cần.
4. **Tinh chỉnh choreography** theo các nguyên tắc bên dưới.
5. **Kiểm tra bằng Playwright** (xem phần *Kiểm tra*). Không báo "xong" khi chưa chụp ảnh ở
   ít nhất 8 vị trí cuộn và chưa xem từng ảnh.

## Kiến trúc bắt buộc

- **Một canvas WebGL `position:fixed`** phủ toàn màn hình, `pointer-events:none`, nền trong suốt
  (`alpha:true`). Màu nền là `body.backgroundColor`, không đặt trong WebGL, để chữ DOM và 3D
  luôn cùng một màu nền.
- **Các `<section>` DOM cao 180–260vh**, bên trong là một `.pin` có `position:sticky; top:0;
  height:100vh`. Section là "đường ray" cuộn, còn `.pin` giữ chữ đứng yên trong khi 3D chuyển động.
- **Một object state `S`**: các timeline GSAP ScrollTrigger (`scrub: 1`) chỉ *tween các số trong
  `S`*, và vòng `renderer.setAnimationLoop` đọc `S` mỗi frame rồi cộng thêm các chuyển động
  idle (bồng bềnh, lắc, parallax theo chuột). Không bao giờ set `mesh.position` trong callback
  của scroll.
- **Wordmark khổng lồ là một plane Three.js** dùng CanvasTexture (`depthWrite:false`), không
  phải chữ DOM. Nhờ vậy có thể đặt một vật thể ở `z<0` (sau chữ) và một vật thể ở `z>0`
  (trước chữ). Đây là hiệu ứng tạo cảm giác "3D thật".
- **Particle dùng `InstancedMesh`** (một draw call cho mỗi chapter) và mỗi hạt có seed riêng
  (vị trí, độ sâu, tốc độ) để tạo parallax.
- **Wipe màu là một `div` fixed** đặt trên canvas, được animate bằng `clip-path: inset()`:
  quét lên che kín, đổi nền ở dưới, rồi quét đi.

## Nguyên tắc chuyển động (đây mới là phần làm nên "chất")

- **Ít chữ, chữ cực to.** Có một display type 9–12vw, nặng 900, `letter-spacing:-.05em`,
  `line-height:.85`. Mọi chữ còn lại đều nhỏ (11–14px), viết hoa giãn chữ, màu muted.
- **Mỗi cảnh chỉ có một vật thể hero**, các vật thể còn lại bay ra khỏi khung. Vật thể hero
  xoay một vòng 360° trong suốt chapter (`ry: '+=2π'`, `ease:'none'`).
- **Ease khác nhau theo vai trò:** vào cảnh dùng `power3.out`, chuyển cảnh dùng
  `power3.inOut`, rơi vào túi dùng `bounce.out`, còn hóa đơn in ra dùng `steps(12)`.
- **Luôn có một chuyển động idle không phụ thuộc cuộn** (lắc theo hình sin, bồng bềnh
  ±0.08). Nhờ vậy khi người xem dừng cuộn, trang vẫn "thở".
- **Parallax theo chiều sâu:** hệ số dịch chuyển theo chuột tỉ lệ với `z`, nên vật ở gần
  dịch nhiều hơn vật ở xa.
- **Wipe màu mạnh**, ví dụ nâu đậm → hồng đỏ rực. Wipe nên chiếm khoảng 25% đầu của mỗi
  chapter và dùng `scrub:true` (không làm mượt) để mép quét bám sát ngón tay.
- **Mỗi chapter đi kèm một thẻ social proof** (kính mờ, xoay ±2°) và chips thành phần, nút
  CTA dạng pill đen có badge giá. Nội dung trong thẻ phải là nội dung thật của khách; nếu
  chỉ là chỗ giữ chỗ thì ghi rõ "sample", không bịa review.
- **Bố cục chapter đổi bên trái/phải xen kẽ** (`side:'left'|'right'`) để nhịp cuộn không đơn điệu.

## Lỗi hay gặp

- `overflow-x:hidden` trên `html`/`body` **làm hỏng `position:sticky`**, khiến chữ trôi
  mất. Hãy dùng `body{overflow-x:clip}`.
- Quên `renderer.outputColorSpace = SRGBColorSpace` và `texture.colorSpace = SRGBColorSpace`
  thì màu sẽ bị nhạt.
- Material cần `transparent:true` thì `opacity` mới có tác dụng.
- **Màn hình dọc (mobile):** nếu chỉ lùi camera thì wordmark và túi vẫn tràn khỏi mép. Template
  dùng `L.xs` (tỉ lệ nửa bề ngang nhìn thấy so với ≈7 đơn vị của desktop) để nén mọi toạ độ x,
  scale wordmark và túi. Hạ `camera.position.y` (khoảng -1.8) để vật thể nằm nửa trên, còn
  chữ DOM dồn xuống nửa dưới (`justify-content:flex-end`). Thẻ social bị ẩn. Luôn chụp kiểm tra ở 390×844.
- **Tiếng Việt:** `line-height:.85` khiến dấu dưới (ọ, ậ) dính vào dấu trên của dòng sau (ú, à)
  và trông như bị mất dấu. Với headline nhiều dòng, dùng `line-height` ≥ 1.05.
- Vật liệu kim loại (nắp son) cần `scene.environment` (RoomEnvironment + PMREM), nếu không sẽ
  bị đen. Khi import `three/addons/` thì phải thêm khoá này vào importmap. Nếu vàng vẫn ra màu
  olive hoặc nâu, chuyển sang `MeshMatcapMaterial` với matcap tự vẽ bằng canvas (gradient ngang
  có một dải sáng): ánh kim nhìn giống ảnh chụp sản phẩm ở mọi góc xoay.
- **Khi người dùng gửi ảnh sản phẩm thật:** lấy tỉ lệ các khối (nắp/đai/thân/đế) và màu từ ảnh
  để dựng mô hình procedural, rồi đặt chính các ảnh đó vào thẻ social proof thay cho ảnh mẫu.
- Tên có gạch nối (sô-cô-la) sẽ bị ngắt dòng ở dấu "-" khi dùng headline to. Hãy dùng U+2011.
- Khi làm trang cho đại lý bán sản phẩm của hãng khác: thương hiệu trên trang là của cửa hàng,
  không dùng logo của hãng trên mô hình 3D, và thêm dòng ghi chú nhãn hiệu ở cuối trang.
- `prefers-reduced-motion`: tắt wipe, tắt idle và dùng `scrub:true`.
- Chỉ nạp CDN có pin phiên bản: `three@0.160.0` (importmap, jsdelivr) và `gsap 3.12.5` (cdnjs).

## Kiểm tra

Chạy Playwright với `--use-gl=swiftshader`, cuộn tới khoảng 11 mốc (0, 7, 15, 26, 33, 42, 55,
62, 72, 85, 100%), chờ khoảng 1.5s ở mỗi mốc (vì `scrub:1` cần thời gian bắt kịp), chụp màn
hình rồi ghép thành contact sheet bằng `ffmpeg -vf tile=3x4` để xem cả trang trong một ảnh.
Nếu sandbox chặn CDN, dùng `page.route()` để trả về file từ `npm i three@0.160.0 gsap@3.12.5`.
Cần kiểm tra:

- Không có `pageerror`.
- Chữ ở mỗi chapter đứng yên (sticky) và không bị cắt.
- Ở cảnh Hero, có ít nhất một vật thể nằm sau chữ và một vật thể nằm trước chữ.
- Wipe phủ kín màn hình tại điểm giữa chuyển cảnh.
- Cảnh cuối thấy rõ CTA.
