---
name: radar-khoang-trong
description: Chạy trọn radar khoảng trống độc giả 7 bước (hiện tượng → nhu cầu → ai thắng → quy mô → soi Việt Nam → khoảng trống → cơ hội kênh). Dùng khi Linh nói "tìm khoảng trống độc giả", "chủ đề nào nên chiếm trước", "quét Medium Substack xem VN thiếu gì", "radar topic".
---

# Radar khoảng trống độc giả (điều phối)

Script: `${CLAUDE_PLUGIN_ROOT}/scripts/gapscan.py` (Python chuẩn). Adapter: `${CLAUDE_PLUGIN_ROOT}/scripts/adapters/`.
Kho mặc định: `D:\LINHX\LAB\LAB029-KHOANG-TRONG-DOC-GIA\chay\`. Mỗi lượt một thư mục `chay/<YYYY-MM-DD>-<chủ-đề>/`, chạy mọi lệnh trong thư mục đó (hoặc `--thu-muc`).

## Trước khi quét: hỏi Linh tối đa 3 câu (bỏ qua câu đã rõ)
1. Toàn cảnh hay một chủ đề? (mặc định toàn cảnh)
2. Viết cho ai ở Việt Nam? (mặc định người đi làm 25 đến 50 tuổi ở thành phố)
3. Nền tảng Việt Nam nào Linh cho mở bằng Chrome của Linh? (mặc định: Substack, Spiderum, YouTube, podcast, Fahasa; Facebook và LinkedIn chỉ trang Linh chỉ định)
Linh không trả lời trong 10 phút thì đi theo mặc định.

## 7 bước, mỗi bước một skill
| Bước | Skill | Ra tệp | Cổng |
|---|---|---|---|
| B1 | `hien-tuong` | `01-hien-tuong.jsonl` | `gapscan.py kiem b1` |
| B2 | `nhu-cau-doc-gia` | `02-cum.json`, `02-nhu-cau.json` | `kiem b2` |
| B3 | `nguoi-thang` | `03-nguoi-thang.md` | `kiem b3` |
| B4 | `quy-mo-thi-truong` | `04-quy-mo.json` | `kiem b4` |
| B5 | `soi-viet-nam` | `05-viet-nam.json` | `kiem b5` (độ phủ dữ liệu ≥ 60%) |
| B6 | `cham-khoang-trong` | `06-khoang-trong.md` | `kiem b6` |
| B7 | `co-hoi-kenh` | `07-co-hoi.md` | Linh duyệt |

Không sang bước sau khi cổng chưa qua, trừ khi Linh đồng ý chạy bản nháp (ghi rõ "BẢN NHÁP" ở đầu mọi tệp sau đó).

## Báo Linh
Khi xong B6: 3 cụm điểm cao nhất, mỗi cụm một câu "vì sao" kèm 1 số đo và 1 link; độ phủ dữ liệu VN; cụm nào cần Linh quyết. Khi xong B7: đính kèm `07-co-hoi.md`. Không chép lại cả bảng.

## Luật
- Chỉ đọc. Không follow, like, comment, subscribe, nhắn tin, đăng bài thay Linh.
- Nhịp chậm, chỉ dữ liệu công khai, chỉ cho nghiên cứu cá nhân (Substack, Medium, LinkedIn đều cấm thu thập hàng loạt).
- Mọi nhận định có link bằng chứng; số làm tròn ghi là làm tròn; chỗ đoán ghi "suy luận".
- Không gợi ý làm kênh tổng hợp lại bài báo (Nghị định 174/2026).
- Ghi thời gian và token ước tính của lượt vào `nhat-ky.md` trong thư mục lượt.
- Xong lượt: nối sang LAB024 (mài góc, tít) hoặc LAB025 (viết bài) nếu Linh muốn.
