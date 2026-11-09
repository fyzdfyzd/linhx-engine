# Bổ sung vòng 2 (cloud, 9/11) · WF14 Nhân vật ảo

Không sửa NGHIEN-CUU.md. File này lấp ba chỗ mỏng: ngưỡng ArcFace có trích dẫn, thử máy đo thật, nguồn ngoài đọc thêm.

## 1. Chốt ngưỡng giữ mặt
| Mức | Cosine ArcFace (buffalo_l) | Làm gì |
|---|---|---|
| Đạt | **≥ 0,45** mỗi ảnh nhìn thẳng / 3/4 | giữ |
| Cờ xem | 0,32 – 0,45 | Claude nhìn lại; lỗi thật thì vẽ lại |
| Trượt | **< 0,32** | vẽ lại, không cần nhìn |
| Không thấy mặt | (nghiêng hẳn, mặt nhỏ, tranh vẽ) | không tính đạt; chấm bằng mắt |
| Bám mặt tham chiếu | ảnh vẽ so với ảnh Unsplash ≥ 0,45 | cờ "bám quá sát" (luật -1,5 trần 6 đã có) |

Căn cứ:
- Mốc trượt 0,32: DeepFace đặt ngưỡng ArcFace là khoảng cách cosine 0,68, tức độ giống 0,32 (`"ArcFace": {"cosine": 0.68, ...}` trong [deepface/config/threshold.py](https://github.com/serengil/deepface/blob/master/deepface/config/threshold.py), đọc code bản 7/11/2026). [đọc]
- InsightFace: "Typical 1:1 thresholds for InsightFace recognition packs land in the 0.30-0.45 cosine range at FMR = 1e-4 to 1e-5" ([guide](https://insightface.ai/guides/choose-face-recognition-model-and-evaluate)). Lấy đầu trên 0,45 làm mức đạt vì nhân vật ảo cần chắc chắn hơn xác minh ảnh thật. [đọc]
- Trần thực tế của máy vẽ giữ mặt: PuLID báo "Face Sim" trung bình 0,733 (PuLID), 0,725 (InstantID), 0,619 (IP-Adapter) trên DivID-120 ([PuLID bảng 1](https://arxiv.org/html/2404.16022)). Lưu ý họ dùng CurricularFace, không phải ArcFace, nên chỉ để hình dung: ảnh tốt nằm khoảng 0,6–0,75, không kỳ vọng 0,9. [đọc]
- Mức "0.45–0.60 same person, other pose / light / age" của [AlchemicaFaceMatch](https://comfy.icu/node/AlchemicaFaceMatch) khớp với mức đạt trên (bản máy đã dẫn).
- Vẫn phải hiệu chỉnh: "Pick the threshold from a validation split, freeze it" ([InsightFace guide](https://insightface.ai/guides/choose-face-recognition-model-and-evaluate)). Việc trên máy cty: chạy `do_mat.py` với ảnh LAB066 (Luna, Trần AI, Cẩm Nhi, Gusto, KAI), cặp cùng người lấy phân vị 5% làm mức đạt, cặp khác người lấy max làm mức trượt. Nếu khác bảng trên quá 0,05 thì sửa bảng.

## 2. Thử máy đo trên mẫu có sẵn
`may-do/do_mat.py` (InsightFace 2.1, buffalo_l, CPU). Cài trên cloud trong 2 phút, chạy được. Kết quả `may-do/kq-thu-0911.json`, mốc là ảnh Emily (LAB026, ảnh thư ký):

| Ảnh | Điểm | Đọc |
|---|---|---|
| Emily khung hẹp (cùng cảnh) | 0,878 | đạt |
| Emily lật gương | 0,963 | đạt |
| Emily thu nhỏ còn 342 px | 0,850 | đạt, mặt nhỏ vẫn đo được |
| 6 người thật khác nhau (ảnh mẫu InsightFace) | -0,06 – 0,07 | trượt rõ |
| Avatar toon Chu Du (LAB100) | -0,095 | trượt |
| Tranh vẽ Lê Bích (LAB045) | không thấy mặt | máy không đo tranh nét |

Kết luận: máy tách cùng người / khác người rất rõ, chạy CPU vài giây một ảnh. **Chưa thử** vùng khó: cùng nhân vật nhưng hai lần vẽ khác nhau, góc 3/4, nghiêng. Ảnh LAB066 chỉ có trên máy (D:), cloud không có.

## 3. Giấy phép (rủi ro cần Linh quyết)
- InsightFace: code MIT, nhưng mô hình: "available for non-commercial research purposes only"; với buffalo_l "please contact recognition-oss-pack@insightface.ai for licensing" ([README](https://github.com/deepinsight/insightface)).
- Thay thế: [AuraFace-v1](https://huggingface.co/fal/AuraFace-v1), giấy phép apache-2.0, "trained on commercially and publicly available data sources to enable its usage in commercial setting", LFW 0,99650. `do_mat.py --model` để đổi. Chưa thử, chưa có ngưỡng riêng (phải hiệu chỉnh lại, theo luật InsightFace "never carry over a threshold across model versions").
- Khuyến nghị: dùng buffalo_l trong LAB (nghiên cứu), trước khi bán dịch vụ nhân vật thì chuyển AuraFace hoặc mua phép.

## 4. Nguồn ngoài đọc thêm trên cloud (bổ sung NGOAI.md)
| Nguồn | Lấy | Bỏ |
|---|---|---|
| [fal-ai-community character-sheet](https://github.com/fal-ai-community/skills/tree/main/skills/character-sheet) | thử lại đổi MỘT nấc (neo → ảnh mốc → chế độ sửa ảnh → máy khác), tối đa 3 lần; manifest.json ghi prompt, máy, seed | API fal |
| [magichourhq character-consistency](https://github.com/magichourhq/skills/tree/main/skills/magic-hour-character-consistency) | vẽ cảnh mới từ ảnh mốc đã duyệt, không từ cảnh trước; đếm chi tiết lặp; chi tiết chưa từng thấy (lưng) là "đề xuất" | MCP Magic Hour |
| [runware character-consistency](https://github.com/runware/runware-skills/tree/main/skills/character-consistency) | "the same … from the reference", chỉ tả phần đổi | API |
| [vargHQ varg-character-design](https://github.com/vargHQ/skills/tree/main/varg-character-design) (MIT) | một chi tiết chữ ký đọc được cỡ điện thoại; thẻ JSON có `never_change`; bible có chữ cho người, bản không chữ cho máy; nền xám nhạt; "unbranded, no logos" | số viral từ X |
| [seedance-characters](https://github.com/Emily2040/seedance-2.0) (MIT) | thẻ nhân vật tag ổn định; luật chân dung người thật cần phép | phần video nhiều người |
Ghi chú đầy đủ: `/mnt/project-files/WF-CHUAN/WF14-nhan-vat-ao/GHI-CHU-CLOUD-0911.md`.

## 5. Sửa vào skill (thêm vào mục của NGHIEN-CUU)
- `casting-mat` bước 5 và `phat-trien-nhan-vat` giai đoạn G: chạy `do_mat.py` mỗi round, bảng ngưỡng ở mục 1; thay luật "lệch mặt -1.5 trần 6" bằng: < 0,32 trừ -1.5 trần 6, 0,32–0,45 giám khảo nhìn lại.
- Casting 3b: đo ảnh vẽ với ảnh Unsplash đã bầu để bắt "bám mặt tham chiếu" bằng số, bổ trợ Lens.
- Chép `do_mat.py` vào `skills/bo/linhx-casting/skills/casting-mat/scripts/` sau khi hiệu chỉnh trên ảnh LAB066.
