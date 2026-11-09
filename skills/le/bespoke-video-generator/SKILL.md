---
name: "Bespoke Video Generator"
description: "Skill sinh video chuyên nghiệp bằng Veo API (Google). Tích hợp Forensic Analyzer để phân tích starting frame/ref, đánh giá chất lượng. Hỗ trợ text-to-video, image-to-video, browser agent tìm reference, API key rotation."
metadata:
  version: "0.1.0"
---

# Bespoke Video Generator

Skill sinh video end-to-end qua Veo API. Mỗi lần chạy tạo **1 folder runtime** chứa toàn bộ quy trình.

## Pipeline

```
Đề bài (brief)
  → Lên storyboard/script video
    → Tìm reference (browser agent) → DOWNLOAD VÀO runtime/references/
      → Analyze refs bằng Forensic Analyzer (nếu image refs)
        → Chuẩn bị starting frame (gen ảnh hoặc dùng ref)
          → Analyze starting frame → refine prompt
            → Gọi Veo API sinh video
              → Poll chờ complete → download
                → Đánh giá chất lượng
                  → Lưu video + lessons
```

## Cấu trúc Runtime Folder

```
runtime/<YYYYMMDD_HHMMSS>_video/
├── brief.md                    # Đề bài gốc
├── storyboard.md               # Script/storyboard
├── prompt.txt                  # Prompt chi tiết
├── references/                 # ⚠️ BẮT BUỘC download ref vào đây
│   ├── ref_001.jpg
│   ├── ref_sources.json        # Nguồn gốc từng ref
│   └── ref_analyses.json       # Forensic analysis refs (nếu có)
├── input_frame.jpg             # Starting frame (nếu image-to-video)
├── input_frame_analysis.json   # Forensic analysis của starting frame
├── brand_assets/               # Logo, brand colors
├── video_<model>_<time>.mp4    # Video sinh ra
├── log.json                    # Full log
└── lessons.md                  # Bài học
```

## Hướng dẫn chi tiết

### Bước 1: Phân tích đề bài → Lên storyboard
1. Xác định mục đích: quảng cáo, social, presentation, demo
2. Viết script/storyboard:
   - **Cảnh**: wide shot, close-up, aerial drone, tracking...
   - **Chuyển động**: camera pan, zoom in/out, slow motion, timelapse
   - **Ánh sáng**: golden hour, studio, neon, natural
   - **Âm thanh**: dialogue, ambient, music (Veo 3.1 tạo audio tự nhiên)
3. Xác định thông số: aspect ratio, resolution, duration
4. Lưu storyboard vào `runtime/<folder>/storyboard.md`

### Bước 2: Tìm reference bằng Browser Agent
**Sử dụng browser_subagent để tìm VÀ DOWNLOAD:**
1. Tìm video/motion reference trên Pinterest, Behance, Vimeo
2. Tìm style reference (color grading, cinematography)
3. **⚠️ BẮT BUỘC: Download thumbnail/screenshot → trực tiếp vào `runtime/<folder>/references/`**
4. Ghi source URL vào `ref_sources.json`

> **KHÔNG BAO GIỜ** lưu ref ở nơi khác. Ref PHẢI nằm trong `runtime/<folder>/references/`.

### Bước 3: Analyze References (nếu có image refs)
Dùng Forensic Analyzer để hiểu style chi tiết từ refs:
```bash
python scripts/analyze_image.py \
  --image runtime/<folder>/references/ref_001.jpg \
  --analyze-refs runtime/<folder>/references/ref_002.jpg \
  --rebuild-prompt
```
→ Dùng insights từ analysis (color palette, lighting, composition) để refine video prompt.

### Bước 4: Chuẩn bị Starting Frame (nếu Image-to-Video)
Nếu cần video từ ảnh cố định:
1. Dùng `/gen-image` tạo starting frame trước
2. Hoặc dùng ảnh có sẵn trong `references/`
3. Copy vào `runtime/<folder>/input_frame.jpg`
4. **Analyze starting frame** để hiểu chi tiết:
   ```bash
   python scripts/analyze_image.py \
     --image runtime/<folder>/input_frame.jpg \
     --rebuild-prompt
   ```
   → Dùng `rebuilt_prompt.txt` để viết video prompt chính xác hơn cho camera movement.

### Bước 5: Sinh video bằng Veo API
```bash
# Text-to-video: Veo 3.1 (highest quality, có audio)
python scripts/generate_video.py \
  --prompt "A cinematic drone shot..." \
  --model veo-3.1-generate-preview \
  --aspect-ratio 16:9 \
  --resolution 1080p \
  --duration 8 \
  --negative-prompt "blurry, distorted, low quality, text overlay"

# Veo 3.1 Fast (nhanh hơn, vẫn có audio)
python scripts/generate_video.py \
  --prompt "<prompt>" \
  --model veo-3.1-fast-generate-preview \
  --duration 8

# Image-to-video (ảnh → video động)
python scripts/generate_video.py \
  --prompt "Gentle camera zoom in, steam rising" \
  --image runtime/<folder>/input_frame.jpg \
  --model veo-3.1-generate-preview

# Veo 2 fallback
python scripts/generate_video.py \
  --prompt "<prompt>" \
  --model veo-2.0-generate-001
```

### Bước 6: Đánh giá
- Mở video trong `runtime/<folder>/`
- Kiểm tra: chuyển động mượt, audio sync, không artifacts
- Xem `log.json` cho chi tiết API response

### Bước 7: Ghi bài học
Ghi vào `runtime/<folder>/lessons.md`:
- Prompt hiệu quả cho video
- Model/resolution phù hợp
- Tips viết prompt cho audio
- Insights từ forensic analysis refs/starting frame

## Model Selection Guide

| Model | Audio | Duration | Resolution | Speed | Khi nào dùng |
|-------|-------|----------|-----------|-------|-------------|
| `veo-3.1-generate-preview` | Native + dialogue | 4/6/8s | 720p/1080p/4K | 11s-6min | Quảng cáo, professional |
| `veo-3.1-fast-generate-preview` | Native | 4/6/8s | 720p/1080p/4K | Faster | Social media, A/B test |
| `veo-2.0-generate-001` | Không | 5/6/8s | 720p | Stable | Fallback, test nhanh |

## Lưu ý quan trọng
- **Async**: Video gen là async — script tự poll mỗi 10s
- **Latency**: 11 giây → 6 phút tùy model
- **Lưu trữ**: Video trên server Google chỉ 2 ngày → download ngay
- **Audio tips**: Viết dialogue trực tiếp trong prompt cho Veo 3.1
- **Negative prompt**: `"blurry, distorted, low quality"`
- **person_generation**: Dùng `allow_adult`

## Scripts Reference

| Script | Chức năng |
|--------|----------|
| `scripts/generate_video.py` | Sinh video + auto poll + download |
| `scripts/analyze_image.py` | Forensic analysis cho refs/starting frame |
| `scripts/generate_image.py` | Sinh starting frame nếu cần |
| `scripts/gemini_client.py` | Core API client |

## Tham số generate_video.py

| Param | Default | Mô tả |
|-------|---------|-------|
| `--prompt` / `-p` | (bắt buộc) | Mô tả video |
| `--model` / `-m` | auto fallback | Model cụ thể |
| `--image` / `-i` | none | Ảnh starting frame |
| `--refs` / `-r` | none | Ảnh tham chiếu style |
| `--aspect-ratio` / `-a` | `16:9` | `16:9` hoặc `9:16` |
| `--resolution` | `720p` | `720p`/`1080p`/`4k` |
| `--duration` / `-d` | 8 | `4`/`6`/`8` giây |
| `--negative-prompt` | none | Mô tả không muốn |
| `--no-fallback` | off | Không fallback |
| `--poll-interval` | 10 | Giây giữa mỗi poll |
