---
name: "Bespoke Image Generator"
description: "Skill sinh ảnh chuyên nghiệp bằng Gemini API. Sử dụng khi cần tạo ảnh, poster, banner, đồ họa. Tích hợp Forensic Analyzer để phân tích ref, đánh giá output, và tự refine prompt. Hỗ trợ browser agent tìm reference, brand guideline, API key rotation."
---

# Bespoke Image Generator

Skill sinh ảnh chuyên nghiệp end-to-end. Mỗi lần chạy tạo **1 folder runtime** chứa toàn bộ quy trình.

## Pipeline

```
Đề bài (brief)
  → Xây dựng prompt chi tiết
    → Tìm reference (browser agent) → DOWNLOAD VÀO runtime/references/
      → Analyze refs bằng Forensic Analyzer → JSON chi tiết
        → Kiểm tra brand assets
          → Gọi Gemini API sinh ảnh (kèm --refs)
            → Analyze output → Evaluate from analysis
              → Nếu score < 7 → Refine prompt → Sinh lại
                → Lưu ảnh output + lessons
```

## Cấu trúc Runtime Folder

```
runtime/<YYYYMMDD_HHMMSS>_image/
├── brief.md                    # Đề bài gốc và phân tích
├── prompt.txt                  # Prompt chi tiết đã xây dựng
├── references/                 # ⚠️ BẮT BUỘC download ref vào đây
│   ├── ref_001.jpg
│   ├── ref_002.png
│   ├── ref_sources.json        # Nguồn gốc từng ref (URL, site, reason)
│   └── ref_analyses.json       # Forensic analysis của từng ref
├── brand_assets/               # Logo, guideline (copy từ references/)
│   ├── logo.png
│   └── brand_colors.txt
├── output_1.png                # Ảnh sinh ra
├── analysis.json               # Forensic analysis của output
├── evaluation.json             # Đánh giá chất lượng từ analysis
├── rebuilt_prompt.txt           # Prompt refined từ analysis (nếu cần)
├── log.json                    # Full log: prompt, response, model, key, timing
└── lessons.md                  # Bài học rút ra
```

## Hướng dẫn chi tiết

### Bước 1: Phân tích đề bài → Xây dựng prompt
1. Xác định **mục đích** (social post, banner, poster, website hero...)
2. Xác định **đối tượng** target audience
3. Xác định **style** (photorealistic, flat design, 3D, watercolor...)
4. Xác định **thông số kỹ thuật**:
   - Aspect ratio: `1:1` (social), `16:9` (banner), `9:16` (story), `4:3`, `3:4`
   - Resolution: `1K` (draft), `2K` (production), `4K` (print) — chỉ Pro model
5. Viết prompt chi tiết bằng **tiếng Anh**
6. Lưu prompt vào `runtime/<folder>/prompt.txt`

### Bước 2: Tìm reference bằng Browser Agent
**Sử dụng browser_subagent để tìm, đánh giá, VÀ DOWNLOAD:**
1. Truy cập Pinterest/Behance/Dribbble
2. Tìm kiếm theo keyword liên quan đến brief
3. Scroll và đánh giá trực quan ảnh nào phù hợp
4. **⚠️ BẮT BUỘC: Download/screenshot ảnh → lưu trực tiếp vào `runtime/<folder>/references/`**
5. Ghi lại nguồn gốc trong `ref_sources.json`:
   ```json
   [
     {"file": "ref_001.jpg", "source": "pinterest.com/pin/xxx", "reason": "Color palette phù hợp"},
     {"file": "ref_002.png", "source": "behance.net/gallery/xxx", "reason": "Layout tương tự brief"}
   ]
   ```

> **KHÔNG BAO GIỜ** lưu ref ở nơi khác rồi quên copy. Ref PHẢI nằm trong `runtime/<folder>/references/` TRƯỚC khi generate.

### Bước 3: Analyze References bằng Forensic Analyzer
Chạy analyzer trên từng ref để hiểu chi tiết style:
```bash
python scripts/analyze_image.py \
  --image runtime/<folder>/references/ref_001.jpg \
  --rebuild-prompt
```
Hoặc analyze nhiều refs cùng lúc:
```bash
python scripts/analyze_image.py \
  --image runtime/<folder>/references/ref_001.jpg \
  --analyze-refs runtime/<folder>/references/ref_002.png runtime/<folder>/references/ref_003.jpg \
  --rebuild-prompt
```
→ Output: `analysis.json` chứa forensic details (color palette, lighting, composition, subjects...)
→ Dùng insights từ analysis để **refine prompt** trước khi generate.

### Bước 4: Kiểm tra Brand Assets
Kiểm tra thư mục `references/` của workspace:
- Logo file → copy vào `runtime/<folder>/brand_assets/`
- Brand guideline (colors, fonts, style) → copy
- Existing visual assets → copy

### Bước 5: Sinh ảnh bằng Gemini API
```bash
# Pro quality (4K, 14 ref images, thinking mode)
python scripts/generate_image.py \
  --prompt "<prompt>" \
  --model gemini-3-pro-image-preview \
  --refs runtime/<folder>/references/*.jpg runtime/<folder>/brand_assets/logo.png \
  --aspect-ratio 16:9 \
  --size 2K \
  --evaluate

# Fast (nhanh, 1024px)
python scripts/generate_image.py \
  --prompt "<prompt>" \
  --model gemini-2.5-flash-image \
  --refs runtime/<folder>/references/*.jpg \
  --aspect-ratio 16:9 \
  --evaluate

# Imagen (photorealistic, standalone — không hỗ trợ refs)
python scripts/generate_image.py \
  --prompt "<prompt>" \
  --model imagen-4.0-generate-001 \
  --aspect-ratio 16:9 \
  --evaluate
```

> **LUÔN dùng `--refs`** nếu có reference images!
> **LUÔN dùng `--evaluate`** để tự đánh giá!

### Bước 6: Analyze + Evaluate Output bằng Forensic Analyzer
Thay vì chỉ evaluate đơn giản, dùng analyzer cho đánh giá sâu:
```bash
python scripts/analyze_image.py \
  --image runtime/<folder>/output_1.png \
  --prompt "<prompt gốc>" \
  --rebuild-prompt
```
→ `analysis.json`: Forensic analysis chi tiết (colors, composition, lighting...)
→ `evaluation.json`: Đánh giá so với prompt gốc (score 1-10, strengths, weaknesses)
→ `rebuilt_prompt.txt`: Prompt refined dựa trên analysis

**Nếu score < 7/10** → dùng `rebuilt_prompt.txt` và chạy lại Bước 5.
**Nếu muốn auto-regenerate:**
```bash
python scripts/analyze_image.py \
  --image runtime/<folder>/output_1.png \
  --prompt "<prompt gốc>" \
  --analyze-refs runtime/<folder>/references/*.jpg \
  --regenerate \
  --model gemini-3-pro-image-preview \
  --aspect-ratio 16:9
```

### Bước 7: Ghi bài học
Tạo `runtime/<folder>/lessons.md` ghi:
- Prompt nào hiệu quả
- Model nào phù hợp nhất
- Ref nào hữu ích nhất
- Lỗi gặp và cách xử lý
- Insights từ forensic analysis

## Model Selection Guide

| Model | Max Refs | Resolution | Speed | Khi nào dùng |
|-------|----------|-----------|-------|-------------|
| `gemini-3-pro-image-preview` | 14 | 1K/2K/4K | ~2min | Professional, poster, banner, text in image |
| `gemini-2.5-flash-image` | 3 | 1024px | ~1.5min | Mockup, A/B test, batch, draft |
| `imagen-4.0-generate-001` | 0 | varies | ~30s | Photorealistic, stock photo (no ref) |

## API Key Rotation
- 18 active keys, tự xoay vòng khi gặp quota error (429)
- Exponential backoff: 2s → 4s → 8s → switch key
- Config: `config/api_keys.json`

## Scripts Reference

| Script | Chức năng |
|--------|----------|
| `scripts/generate_image.py` | Sinh ảnh + evaluate cơ bản |
| `scripts/analyze_image.py` | Forensic analysis + deep evaluate + rebuild prompt + auto regenerate |
| `scripts/gemini_client.py` | Core API client (key rotation, retry, fallback) |

## Tham số generate_image.py

| Param | Default | Mô tả |
|-------|---------|-------|
| `--prompt` / `-p` | (bắt buộc) | Mô tả hình ảnh |
| `--model` / `-m` | auto fallback | Model cụ thể |
| `--refs` / `-r` | none | Paths ảnh tham chiếu |
| `--aspect-ratio` / `-a` | `1:1` | Tỷ lệ khung |
| `--size` / `-s` | none | `1K`/`2K`/`4K` (Pro only) |
| `--evaluate` / `-e` | off | Auto đánh giá |
| `--num` / `-n` | 1 | Số ảnh sinh |
| `--no-fallback` | off | Không dùng fallback chain |

## Tham số analyze_image.py

| Param | Default | Mô tả |
|-------|---------|-------|
| `--image` / `-i` | (bắt buộc) | Ảnh cần phân tích |
| `--prompt` / `-p` | none | Prompt gốc (để evaluate) |
| `--analyze-refs` / `-r` | none | Thêm ref images để analyze |
| `--rebuild-prompt` | off | Xây lại prompt từ analysis |
| `--regenerate` | off | Auto regenerate với refined prompt |
| `--model` / `-m` | auto | Model cho regeneration |
| `--aspect-ratio` / `-a` | `1:1` | AR cho regeneration |
| `--size` / `-s` | none | Size cho regeneration |
