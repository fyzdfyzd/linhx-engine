Bản vàng: mẫu top tier đã được Linh duyệt, dùng làm mốc chấm.

## Bản vàng đề xuất (máy cty 9/11, chờ Linh duyệt)
| # | Mẫu | Ở đâu | Vì sao làm mốc |
|---|---|---|---|
| 1 | Cổng tag theo uid + đệm tin nhóm của goclaw | https://github.com/nextlevelbuilder/goclaw `internal/channels/zalo/personal/{handlers,policy}.go` (commit 5790d34). Giấy phép CC BY-NC 4.0: chỉ để link, không chép | Đúng việc WF20 cần nhất: chỉ nhận khi tag đúng uid, bỏ @all, tin không tag vẫn ghi làm ngữ cảnh |
| 2 | Bộ eval chạy model thật của zalo-agent | `zalo-agent-evals/` (MIT, bản chép từ https://github.com/vuhai2002/zalo-agent commit 4346f29) | Chấm trên hành vi (gọi/không gọi tool, tham số tool), chặn "lượt hỏng mà chấm đạt", API Zalo giả để không nhắn người thật |
| 3 | Bộ lọc trả lời của zalo-agent | `zalo-agent-evals/allowlist-filter.ts` | Thứ tự lọc rõ: tin của mình → rỗng → nhóm cần tag → allowlist → công tắc tắt theo nhóm; lọc trước khi tốn token |
| 4 | Khuôn đội + quy chuẩn của markus | `markus-content-team/` (Apache-2.0, https://github.com/markus-global/markus commit dfc5f4d) | Một file JSON vai + một NORMS: mỗi việc có người làm và người duyệt, cổng chất lượng mỗi chặng, sản phẩm đăng ký để đếm |
| 5 | Hướng dẫn agent trong nhóm chat của Microsoft Teams | https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/channel-and-group-conversations | Chuẩn nghề của một nền chat lớn: mặc định chỉ nhận khi @nhắc, không tin chữ trong tin mà dùng thực thể mention, không chào từng người |
