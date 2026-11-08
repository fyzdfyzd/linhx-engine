---
name: architecture-patterns-and-design-rules
description: Quy chuẩn kiến trúc & nguyên tắc thiết kế mã nguồn chuẩn cho React, Next.js, Node.js, NestJS theo Antigravity Global Architecture Patterns & Design Rules. Bao gồm phân tách Dumb vs Smart component, giới hạn kích thước code, phân cấp State Management, kiểm soát Native Type Casting PostgreSQL/Prisma, Transactions và Evidence-Based Debugging.
---
# QUY CHUẨN KIẾN TRÚC & NGUYÊN TẮC THIẾT KẾ MÃ NGUỒN (ARCHITECTURE PATTERNS & DESIGN RULES)
**Áp dụng:** Toàn bộ Dự án React / Next.js / Node.js / NestJS thuộc URAH & UNIKON  
**Nguồn quy chuẩn:** Antigravity Global Architecture Patterns & Design Rules  

---

## 1. CẤU TRÚC THƯ MỤC CHUẨN (STANDARD STRUCTURE)

### 1.1. Chuẩn Cấu trúc Frontend (React / Next.js App Router)
```
/src
├── /app
│   ├── App.tsx                    # Main component (hoặc layout.tsx)
│   ├── routes.ts                  # Cấu hình Routing tập trung
│   ├── /components
│   │   ├── /layout               # Header, Sidebar, Footer, Layout Wrappers
│   │   ├── /ui                   # Button, Card, Input, Modal, Spinner (Dumb / Pure UI)
│   │   └── /features             # Feature-specific components (Smart / Container UI)
│   ├── /pages                     # Route components (nếu dùng router ngoài)
│   ├── /hooks                     # Custom hooks dùng chung (>= 2 places)
│   ├── /context                   # Context providers (Theme, Auth, Language)
│   ├── /lib                       # Configs, Constants, API Client
│   ├── /utils                     # Utility functions thuần túy
│   └── /types                     # TypeScript interfaces & types
├── /styles
│   ├── theme.css                 # CSS variables & design tokens
│   ├── fonts.css                 # Font imports duy nhất
│   └── index.css                 # Global base styles
└── /public                        # Static assets (images, icons)
```

### 1.2. Quy tắc Tạo Thư mục Mới (KISS & YAGNI)
* `/pages`: Chỉ tạo khi dự án có từ 4+ routes. Ứng dụng 1-2 trang dùng Conditional Rendering.
* `/hooks`: Chỉ tạo khi có từ 2 custom hooks trở lên tái sử dụng logic.
* `/context`: Chỉ tạo khi cần chia sẻ state toàn cục (Auth, Theme). Không lạm dụng làm state server.
* `/utils`: Chỉ tạo khi có từ 3 hàm tiện ích độc lập trở lên.

---

## 2. NGUYÊN TẮC THIẾT KẾ COMPONENT (COMPONENT PATTERNS)

### 2.1. Phân Tách Dumb UI vs Smart Container
* **Presentational (Dumb / Pure):** Chỉ nhận dữ liệu qua `props`, không chứa logic gọi API, khả năng tái sử dụng cao (`Button`, `Card`, `Modal`).
* **Container (Smart):** Đảm nhiệm fetch dữ liệu, quản lý trạng thái, liên kết sự kiện (`UserDashboard`, `ProductListPage`).

### 2.2. Giới Hạn Quy Mô Component (Size Limits)
* File component: Tối đa **300 dòng** $\rightarrow$ Quá 300 dòng bắt buộc tách file con.
* Một hàm xử lý: Tối đa **50 dòng**.
* JSX return: Tối đa **150 dòng** $\rightarrow$ Tách sub-components.
* Số lượng Props: Tối đa **10 props** $\rightarrow$ Dùng Composition (`children`).
* Số lượng `useState`: Tối đa **5 useState** $\rightarrow$ Chuyển sang `useReducer`.
* Số lượng `useEffect`: Tối đa **3 useEffect** $\rightarrow$ Trích xuất sang custom hooks.

---

## 3. KIẾN TRÚC QUẢN TRỊ TRẠNG THÁI (STATE MANAGEMENT HIERARCHY)

Nguyên tắc: **Sử dụng cấp độ đơn giản nhất đáp ứng được yêu cầu**:
1. `useState`: Quản lý UI state cục bộ (modal đóng/mở, toggle, input form).
2. `useReducer`: Quản lý state cục bộ phức tạp (multi-step wizard, cart items).
3. `Context API`: Chia sẻ state xuyên suốt cây component (User Auth, Theme, Language).
4. `Server Database / API`: Lưu trữ dữ liệu lâu dài và đồng bộ đa thiết bị.

---

## 4. QUY TẮC PHÁT TRIỂN BACKEND & CSDL (BACKEND INTEGRITY)

### 4.1. Kiểm Soát Ép Kiểu Dữ Liệu Native (Strict Type & Native Casting)
* **Kinh nghiệm thực tế:** PostgreSQL có kiểu dữ liệu native `UUID`. Khi thực hiện câu lệnh tìm kiếm hỗn hợp:
  ```typescript
  // CẤM: Gây lỗi Prisma P2023 làm sập API HTTP 500 khi input không phải UUID
  where: { OR: [{ id: identifier }, { serial: identifier }] }

  // BẮT BUỘC: Validate format trước khi query cột native UUID
  import { isUuid } from 'src/common/utils/security.util';
  where: isUuid(identifier)
    ? { OR: [{ id: identifier }, { serial: identifier }] }
    : { OR: [{ serial: identifier }] }
  ```

### 4.2. Tính Toàn Vẹn Giao Dịch (Database Transactions)
* Mọi hành động ghi dữ liệu trên nhiều hơn 1 bảng bắt buộc bọc trong `prisma.$transaction([ ... ])`.
* Chống trạng thái lơ lửng (Inconsistent state).

### 4.3. Quy Chuẩn Debugging: Evidence-Based (Không Đoán Mò)
* Thêm tiền tố `[DEBUG][<module>]...` vào log trước khi sửa lỗi.
* Đối chiếu 3 nguồn: Database query chuẩn giờ VN (`Asia/Ho_Chi_Minh`), Docker container logs, Client browser telemetry.

---

## 5. BẮT ĐẦU DỰ ÁN MỚI
Mọi dự án khi bắt đầu phải tạo file `.agents/rules/project-tech-stack.md` tại root project ghi rõ:
- Tech stack cụ thể đã chọn (Node version, Next.js / NestJS version).
- Cấu trúc thư mục thực tế áp dụng.
- Chiến lược quản trị state và cache.
- Cấu hình server và quy ước deploy.
