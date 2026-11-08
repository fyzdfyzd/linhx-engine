---
name: backend-security-audit
description: Quy trình tự động rà soát an toàn mã nguồn Backend NestJS/Express theo chuẩn OWASP API Security Top 10 (2023), OWASP LLM Applications (2025) và ASVS v4.0.3 Level 2. Cung cấp ma trận kiểm thử, bộ lệnh SAST Grep tự động, Mẫu Code Chuẩn Mực, Pre-flight Checklist và Toàn bộ Bài học Cạm bẫy Kỹ thuật Thực chiến.
---

# QUY CHUẨN RÀ SOÁT AN TOÀN MÃ NGUỒN BACKEND (SAST & API AUDIT)
**Quản lý chuyên môn:** Tài (Tech Lead)  
**Phạm vi áp dụng:** Toàn bộ dịch vụ Backend Node.js / NestJS / Prisma / PostgreSQL / Cloud Run  

Tài liệu cung cấp quy chuẩn rà soát an toàn mã nguồn tĩnh (**SAST**) và kiểm thử an ninh chuyên sâu dành cho Kỹ sư Phần mềm và AI Agent khi phát triển, tối ưu và vận hành các hệ thống backend.

---

### 📚 TÀI LIỆU TIÊU CHUẨN QUỐC TẾ BẮT BUỘC THAM CHIẾU:
Khi cần nghiên cứu nâng cấp hoặc bổ sung quy chuẩn an ninh mới cho hệ thống, Tech Team tham chiếu trực tiếp các nguồn chính thức sau:
1. **OWASP WSTG v4.2 (Web Security Testing Guide):**  
   `https://owasp.org/www-project-web-security-testing-guide/v42/`
2. **OWASP ASVS v4.0.3 (Application Security Verification Standard - Level 2):**  
   `https://owasp.org/www-project-application-security-verification-standard/`
3. **OWASP API Security Top 10 (2023):**  
   `https://owasp.org/API-Security/editions/2023/en/0x11-t10/`
4. **OWASP Top 10 for LLM Applications (2025):**  
   `https://owasp.org/www-project-top-10-for-large-language-model-applications/`
5. **CWE List (Common Weakness Enumeration - MITRE):**  
   `https://cwe.mitre.org/data/definitions/`

---

## 🧭 I. MA TRẬN TIÊU CHUẨN AN NINH OWASP API TOP 10 (2023) & OWASP LLM (2025)

| Mã Chuẩn | Tên Rủi Ro Kỹ Thuật | Dấu Hiệu Trong Mã Nguồn (Anti-Patterns) | Tiêu Chuẩn Khắc Phục Bắt Buộc (Remediation) |
| :--- | :--- | :--- | :--- |
| **API1:2023** | **Phân Quyền Đối Tượng Dữ Liệu (BOLA / IDOR)** | Dùng `@Param('id')`, `@Query('userId')`, `@Body('userId')` để truy vấn hoặc cập nhật dữ liệu cá nhân của người dùng. | **BẮT BUỘC** trích xuất danh tính từ JWT Token đã xác thực: `req.user.sub` hoặc `req.user.id`. Tuyệt đối không tin tưởng ID người dùng do client gửi lên. |
| **API2:2023** | **Xác Thực Đầu Vào (Broken Authentication)** | Thiếu `@UseGuards(JwtAuthGuard)` trên endpoint nhạy cảm; dùng mật khẩu yếu; không có reCAPTCHA chống brute-force. | Bọc `@UseGuards(JwtAuthGuard)` trên mọi route nghiệp vụ riêng tư. Áp dụng Google reCAPTCHA v3 và Rate Limiting (`@Throttle`) trên các cổng xác thực. |
| **API3:2023** | **Gán Thuộc Tính Ngoài Phạm Vi (Mass Assignment)** | Sử dụng object literal inline dạng `@Body() body: any` hoặc `@Body() body: { name: string }`. | **BẮT BUỘC** định nghĩa Class DTO độc lập với decorator từ `class-validator` (`@IsString()`, `@IsOptional()`, `@IsInt()`). Kích hoạt `ValidationPipe({ whitelist: true, forbidNonWhitelisted: true })` toàn cục. |
| **API4:2023** | **Tiêu Thụ Tài Nguyên Không Giới Hạn (DoS / DoW)** | API danh sách (`findMany`) không có phân trang; vòng lặp gọi AI LLM vô hạn; không giới hạn dung lượng upload. | Áp dụng `@Query('page')` và `@Query('limit')` với trần cố định `Math.min(limit, 100)`. Thiết lập `AbortController` timeout 45s cho các luồng xử lý AI. |
| **API5:2023** | **Phân Quyền Cấp Chức Năng (BFLA)** | API Admin/Staff không kiểm tra Role hoặc chỉ kiểm tra ở tầng Frontend UI. | Kết hợp `@UseGuards(JwtAuthGuard, RolesGuard)` và `@Roles('super_admin', 'admin')` để phân quyền chặt chẽ tại tầng Controller. |
| **API6:2023** | **Yêu Cầu Phía Máy Chủ Không An Toàn (SSRF)** | Server gọi `fetch(url)` hoặc `axios.get(url)` với `url` do client/webhook truyền lên mà không kiểm tra tên miền và IP private. | Whitelist danh sách domain cho phép (GCS, Firebase Storage). Chặn đứng `localhost`, `127.0.0.1`, RFC1918 (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) và Cloud Metadata `169.254.169.254`. |
| **API7:2023** | **Cấu Hình An Toàn Chưa Phù Hợp** | CORS mở `origin: '*'`; ghi lộ thông tin nhạy cảm (PII, Token, Prompt) trong log console Production. | Khóa CORS theo whitelist domain cụ thể. Sử dụng hàm mask/redact thông tin nhạy cảm trước khi ghi log. |
| **API8:2023** | **Bảo Vệ Khỏi Tấn Công Tự Động** | Không có cơ chế chống bot cào quét dữ liệu, spam tạo mã QR rác, spam gửi OTP. | Tích hợp Throttling theo IP / User ID kết hợp reCAPTCHA v3 trên mọi form tương tác công khai. |
| **API9:2023** | **Quản Lý Phiên Bản API Thiếu Rõ Ràng** | Tồn tại các route thử nghiệm, debug, control-plane bị bỏ quên không có bảo vệ. | Rà soát và xóa bỏ các endpoint thừa thãi; nhóm version API tường minh (`/api/v1/...`). |
| **API10:2023** | **Sử Dụng API Bên Thứ Ba Chưa An Toàn** | Tin tưởng tuyệt đối dữ liệu trả về từ LLM (Gemini/OpenAI) mà không validate schema trước khi lưu CSDL. | Dùng `zod`, `class-validator` hoặc JSON Schema parse kết quả của AI trước khi ghi vào Database. |
| **CWE-200** | **Lộ Cấu Hình Hệ Thống & Khóa Nhạy Cảm** | Endpoint cấu hình `/api/system-configs` mở public hoặc thiếu phân quyền Admin; API trả về `bypassPasskey`, `systemPrompt` của AI, hoặc danh sách blacklist từ khóa cấm; rò rỉ metadata cấu hình nội bộ. | **BẮT BUỘC** khóa `@UseGuards(JwtAuthGuard, RolesGuard)` và `@Roles('super_admin', 'admin')`. Loại bỏ hoàn toàn passkey khỏi response; cấu hình `isSecret: true` cho bảng brand safety; mask/sanitize mọi trường nhạy cảm. |
| **CWE-200:Pipeline** | **Lộ Cấu Trúc Pipeline AI & Dữ Liệu Tài Chính** | Endpoint public `/api/campaign/slug/:slug` hoặc `/api/public/campaign/:code` trả về `pipelineSteps` chứa `promptTemplate`, `config`, tên model AI, hoặc dữ liệu tài chính nội bộ `budgetVnd`. Kẻ tấn công đọc trộm cấu trúc pipeline, bí quyết prompt AI và cấu hình kỹ thuật. | **Loại bỏ triệt để `pipelineSteps` khỏi API Public**: Do Frontend End-user đã chuyển sang dùng 100% câu quote tĩnh (`ROTATING_QUOTES`) và % tiến trình từ SSE/Polling, API Public loại bỏ hoàn toàn `pipelineSteps` khỏi câu query `include` và response (vừa tối ưu tốc độ DB vừa bảo mật cấu trúc). Backend Pipeline Orchestrator khi thực thi tự query DB nội bộ để nhận prompt và config. |
| **API2:ZeroTrust** | **Endpoint Công Khai Không Cần Thiết** | Mở public tùy tiện các endpoint Master Data (`/campaign/branches`, `/campaign/collections`), luồng quét/nhận quà QR (`/qr/*`), luồng submit AI Pipeline mà không yêu cầu Token đăng nhập. | **Mặc định 100% endpoint là Private (bọc JwtAuthGuard)**. Chỉ cho phép mở Public các route nằm trong `APPROVED_PUBLIC_WHITELIST` được phê chuẩn chính thức (Auth, Landing Page, Legal, Telemetry) và **BẮT BUỘC** có Rate Limiting (`@Throttle`). |
| **CWE-434:Upload** | **Tải Tệp Không Giới Hạn & Nguy Cơ Cạn Ổ Đĩa** | Mở public endpoint tải ảnh/media (`/uploads/base64`, `/uploads/photos`) không yêu cầu Auth hoặc thiếu Rate Limiting, cho phép bot spam làm cạn kiệt ổ đĩa VPS/Cloud Storage. | **BẮT BUỘC** bọc `@UseGuards(JwtAuthGuard)` trên các cổng upload media cá nhân, kèm Rate Limiting `@Throttle({ default: { limit: 15, ttl: 60000 } })`. Sanitize tên tệp chống Path Traversal và xác thực Magic Bytes nhị phân. |
| **LLM01/04** | **Tiêm Nhiễm Lệnh AI & Tràn Chi Phí Gọi Model** | Cộng chuỗi trực tiếp input người dùng vào System Prompt; không giới hạn độ dài input văn bản/ảnh/audio. | Tách biệt `systemInstruction` và `userContent`. Giới hạn ký tự tối đa (VD: max 1000 ký tự prompt, max 5 ảnh). OCR/ASR tiền kiểm tra trước khi nạp vào mô hình đa phương thức. |
| **CWE-22** | **Duyệt Thư Mục & Giải Nén Tệp Tùy Tiện (Zip Slip)** | Dùng `path.join(baseDir, userInput)` mà không làm sạch input; giải nén zip không kiểm tra canonical path. | Sử dụng regex gắt gao `/[^a-zA-Z0-9_-]/g` (loại bỏ dấu chấm `.`) và kiểm tra `path.resolve(basePath, cleanId).startsWith(basePath)`. |
| **CWE-330** | **Sinh Mã Ngẫu Nhiên Không An Toàn** | Sử dụng `Math.random()` để sinh mã Token xác thực, mã OTP, mã QR ID hoặc mã mở quà. | **BẮT BUỘC** sử dụng CSPRNG: `crypto.randomBytes(8).toString('hex')`, `crypto.randomInt(100000, 1000000)` hoặc `crypto.randomUUID()`. |
| **CWE-362** | **Cạnh Tranh Tiến Trình Giao Dịch (TOC/TOU)** | Kiểm tra số dư / trạng thái thẻ quà và cập nhật không bọc trong Database Transaction. | **BẮT BUỘC** bọc trong `prisma.$transaction()` kết hợp Unique Constraints hoặc Row-Level Locking để chống Double-Claim / Double-Spend. |
| **CWE-434** | **Tải Lên Tệp SVG Chứa Mã Độc XSS** | Cho phép upload tệp SVG không làm sạch XML hoặc không kiểm tra Magic Bytes. | Kiểm tra Magic Bytes 4-12 bytes nhị phân. Cấm hoặc sanitize triệt để thẻ `<script>` trong tệp SVG. Giới hạn pixel (max 4096x4096) chống Decompression Bomb. |

---

## ⚡ II. BỘ LỆNH QUÉT TĨNH TỰ ĐỘNG (AUTOMATED SAST GREP MATRIX)

Khi thực hiện audit Backend, AI Agent và Dev chạy ngay các mẫu regex sau để rà soát mã nguồn:

```bash
# 0. QUÉT AST TỰ ĐỘNG 100% CONTROLLER ENDPOINTS (BẮT BUỘC - CI/CD GATE)
# Chạy Linter AST quét toàn bộ các Controllers, chặn đứng endpoint thiếu Auth ngoài Whitelist
npm run test:auth-audit

# 1. Quét tìm sinh token / OTP ngẫu nhiên yếu (CWE-330)
grep -rnE "Math\.random\(" backend/src/

# 2. Quét tìm Mass Assignment / Thiếu DTO Class trong Controller (API3:2023)
grep -rnE "@Body\(\)\s+[a-zA-Z0-9_]+\s*:\s*(any|\{[^}]*\})" backend/src/

# 3. Quét tìm SQL Injection thô hoặc Unsafe queries
grep -rnE "(\$queryRawUnsafe|\$executeRawUnsafe)" backend/src/

# 4. Quét tìm Controller Admin thiếu Guard hoặc Role (API5:2023)
grep -rnE "@Controller\(['\"]admin" backend/src/

# 5. Quét tìm CORS wildcard chưa thu hẹp (API7:2023)
grep -rnE "origin:\s*['\"]?\*['\"]?" backend/src/

# 6. Quét tìm Path Traversal / Nối chuỗi file thiếu sanitize (CWE-22)
grep -rnE "path\.join\(.*(req\.|body\.|query\.|params\.)" backend/src/

# 7. Quét tìm URL fetch không qua whitelist SSRF (API6:2023)
grep -rnE "fetch\((req\.|body\.|query\.)" backend/src/

# 8. Quét tìm Rò rỉ Thông tin Nhạy cảm (CWE-200: Passkey, Prompt, Blacklist lộ ra API)
grep -rnE "(bypassPasskey|systemPrompt|obsceneBlacklist|politicalBlacklist|competitorBlacklist)" backend/src/modules/system-config/

# 9. Quét tìm Endpoint Public thiếu Rate Limiting Throttler (API8:2023)
grep -rnE "@Controller\(['\"](auth|analytics/telemetry)" backend/src/

# 10. Quét tìm Rò rỉ Prompt AI & Budget trong API Public (CWE-200: Pipeline Steps & Campaign)
grep -rnE "(promptTemplate|brandSafetyPrompt|budgetVnd)" backend/src/modules/public-campaign/ backend/src/modules/campaign/campaign.service.ts

# 11. Quét tìm Cổng Upload File thiếu JwtAuthGuard hoặc thiếu Rate Limiting (CWE-434 / DoS)
grep -rnE "@Post\(['\"](base64|photos|upload)" backend/src/modules/uploads/
```

---

## 🏆 III. MẪU CODE CHUẨN MỰC (CODE TEMPLATES)

### 1. Template: Controller Chuẩn Bảo Mật & Phân Quyền Đa Tầng
```typescript
import { Controller, Get, Post, Put, Body, Param, Query, UseGuards, Request, HttpStatus, HttpCode } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth, ApiResponse } from '@nestjs/swagger';
import { Throttle } from '@nestjs/throttler';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { RolesGuard } from '../auth/guards/roles.guard';
import { Roles } from '../auth/decorators/roles.decorator';
import { UpdateUserProfileDto, QueryPaginationDto } from './dto/user.dto';
import { UserService } from './user.service';

@ApiTags('User Profile Management')
@Controller('users')
@UseGuards(JwtAuthGuard, RolesGuard)
@ApiBearerAuth()
export class UserController {
  constructor(private readonly userService: UserService) {}

  // 1. Chống IDOR: Lấy userId trực tiếp từ JWT Payload đã xác thực
  @Put('profile')
  @ApiOperation({ summary: 'Cập nhật thông tin cá nhân của chính mình' })
  async updateProfile(@Request() req: any, @Body() body: UpdateUserProfileDto) {
    const currentUserId = req.user.sub || req.user.id;
    return this.userService.updateProfile(currentUserId, body);
  }

  // 2. Chống DoS: Bắt buộc phân trang và giới hạn trần bản ghi
  @Get('admin/list')
  @Roles('super_admin', 'admin')
  @Throttle({ short: { limit: 30, ttl: 60000 } })
  @ApiOperation({ summary: 'Lấy danh sách người dùng dành cho Admin' })
  async getAllUsers(@Query() query: QueryPaginationDto) {
    const page = Math.max(1, Number(query.page) || 1);
    const limit = Math.min(100, Math.max(1, Number(query.limit) || 20));
    return this.userService.findAllPaginated(page, limit);
  }
}
```

### 2. Template: Class DTO Chuẩn (Secure Validation DTO)
```typescript
import { IsString, IsNotEmpty, IsOptional, IsEmail, MaxLength, MinLength, IsInt, Min, Max } from 'class-validator';
import { Type } from 'class-transformer';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class UpdateUserProfileDto {
  @ApiProperty({ example: 'Nguyễn Văn A', description: 'Họ và tên khách hàng' })
  @IsString()
  @IsNotEmpty()
  @MaxLength(100)
  fullName: string;

  @ApiPropertyOptional({ example: 'user@tranbao.vn', description: 'Địa chỉ email' })
  @IsOptional()
  @IsEmail()
  @MaxLength(150)
  email?: string;

  @ApiPropertyOptional({ example: '0912345678', description: 'Số điện thoại' })
  @IsOptional()
  @IsString()
  @MaxLength(20)
  phone?: string;
}

export class QueryPaginationDto {
  @ApiPropertyOptional({ default: 1 })
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  page?: number = 1;

  @ApiPropertyOptional({ default: 20 })
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  @Max(100)
  limit?: number = 20;
}
```

### 3. Template: Xử Lý I/O, Chống Path Traversal & Sinh Mã CSPRNG
```typescript
import * as path from 'path';
import * as crypto from 'crypto';
import { BadRequestException } from '@nestjs/common';

export class SafeStorageHelper {
  private static readonly BASE_DIR = path.resolve(process.cwd(), 'storage_vault');

  public static sanitizeIdentifier(rawId: string): string {
    if (!rawId || typeof rawId !== 'string') {
      throw new BadRequestException('Mã định danh không hợp lệ');
    }
    // Loại bỏ hoàn toàn dấu chấm, slash, backslash, ký tự shell độc hại
    const clean = rawId.replace(/[^a-zA-Z0-9_-]/g, '');
    if (clean.length === 0 || clean.length > 128) {
      throw new BadRequestException('Độ dài mã định danh không hợp lệ');
    }
    
    // Kiểm tra Canonical Path an toàn
    const resolvedPath = path.resolve(this.BASE_DIR, clean);
    if (!resolvedPath.startsWith(this.BASE_DIR)) {
      throw new BadRequestException('Phát hiện đường dẫn không an toàn');
    }
    return clean;
  }

  // Sinh Token bí mật chuẩn mật mã học (CSPRNG)
  public static generateSecureToken(prefix: string = 'token'): string {
    return `${prefix}-${crypto.randomBytes(8).toString('hex')}`;
  }

  // Sinh OTP 6 chữ số chuẩn CSPRNG
  public static generateSecureOtp(): string {
    return crypto.randomInt(100000, 1000000).toString();
  }
}
```

### 4. Template: Chống Race Condition trong Giao Dịch / Đổi Thưởng
```typescript
import { Injectable, BadRequestException, ConflictException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class SecureTransactionService {
  constructor(private prisma: PrismaService) {}

  async claimReward(userId: string, rewardPoolId: string) {
    // Bọc trong transaction để kiểm soát tuần tự (chống TOC/TOU)
    return this.prisma.$transaction(async (tx) => {
      // 1. Kiểm tra tồn kho và lock bản ghi
      const pool = await tx.rewardPool.findUnique({
        where: { id: rewardPoolId },
      });

      if (!pool || pool.currentStock <= 0) {
        throw new BadRequestException('Phần thưởng đã hết số lượng');
      }

      // 2. Trừ tồn kho có điều kiện nguyên tử (Atomic Update)
      const updated = await tx.rewardPool.updateMany({
        where: { id: rewardPoolId, currentStock: { gt: 0 } },
        data: { currentStock: { decrement: 1 } },
      });

      if (updated.count === 0) {
        throw new ConflictException('Phần thưởng vừa được nhận bởi người dùng khác. Vui lòng thử lại.');
      }

      // 3. Ghi nhận lịch sử nhận quà của user
      return tx.userReward.create({
        data: {
          userId,
          rewardPoolId,
          claimedAt: new Date(),
        },
      });
    });
  }
}
```

---

## ✅ IV. PRE-FLIGHT SECURITY CHECKLIST CHO DEVELOPER / AI AGENT

Trước khi bàn giao hoặc đánh dấu hoàn thành bất kỳ tính năng Backend nào, kiểm tra qua 13 tiêu chí:

- [ ] **1. Authentication:** Mọi route không phải public đều có `@UseGuards(JwtAuthGuard)` chưa?
- [ ] **2. IDOR:** Có endpoint nào đọc `userId` từ `body`/`param` thay vì `req.user.sub` không?
- [ ] **3. DTO Validation:** 100% `@Body()` đã dùng Class DTO với `@IsString`, `@IsOptional` chưa? (Không còn object `{}` inline).
- [ ] **4. Pagination:** Các API danh sách Admin đã có `take`/`skip` với trần `limit <= 100` chưa?
- [ ] **5. Token Entropy:** Đã thay thế 100% `Math.random()` bằng `crypto.randomBytes()` / `crypto.randomInt()` chưa?
- [ ] **6. SSRF & Path Traversal:** Các hàm đọc URL và I/O thư mục đã qua whitelist và `sanitizeId` chưa?
- [ ] **7. Concurrency & Race Condition:** Các tác vụ trừ kho/đổi quà/nhận thưởng đã bọc trong `prisma.$transaction()` chưa?
- [ ] **8. PII Masking:** API danh sách quầy đã ẩn token và che số điện thoại đối với nhân viên chưa?
- [ ] **9. AST Auth Linter:** Đã chạy `npm run test:auth-audit` và đạt 0 vi phạm (100% endpoint được bảo vệ hoặc nằm trong Whitelist phê duyệt)?
- [ ] **10. Secret Sanitization & CWE-200:** Đã kiểm tra không có API nào trả về `bypassPasskey`, `systemPrompt`, hay danh sách `blacklist` ra phía client?
- [ ] **11. Rate Limiting:** Các endpoint public (auth, telemetry, pre-check AI) đã gắn decorator `@Throttle` chưa?
- [ ] **12. Public Campaign Sanitization:** Các API công khai chiến dịch (`/campaign/slug/:slug`, `/public-campaign/:code`) đã lọc bỏ `promptTemplate`, `config`, `brandSafetyPrompt` và `budgetVnd` chưa?
- [ ] **13. Media Upload Guarding:** Các endpoint tải ảnh/tệp (`/uploads/base64`, `/uploads/photos`) đã bọc `@UseGuards(JwtAuthGuard)` và `@Throttle(15 req/phút)` chưa?

---

## 🎯 V. BÀI HỌC BẢO MẬT & CẠM BẪY ĐẶC THÙ THỰC CHIẾN ĐÃ XỬ LÝ TẠI TRÂN BẢO PLATFORM

Đây là các vấn đề kỹ thuật và cạm bẫy thực tế **đã phát sinh trong quá trình xây dựng Trân Bảo Platform**, cần được duy trì để kế thừa cho các dự án sau:

### 1. Cạm bẫy Crash Prisma do chuỗi Placeholder (`?collectionId=ALL`)
- **Nguyên nhân kỹ thuật:** Frontend truyền param lọc `?collectionId=ALL` hoặc `""`. Nếu truyền trực tiếp vào câu lệnh `where: { collectionId }` của Prisma, Prisma sẽ ném ngoại lệ `Invalid UUID string` gây **HTTP 500 Crash**.
- **Giải pháp chuẩn:** Mọi query param dạng UUID bắt buộc phải lọc bỏ giá trị placeholder (`"ALL"`, `""`) hoặc kiểm tra Regex UUID trước khi đưa vào Prisma filter:
  ```typescript
  const isUUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(param);
  const filter = (param && param !== 'ALL' && isUUID) ? { collectionId: param } : {};
  ```

### 2. Thu Hồi Phiên Đăng Nhập Với JWT (Session Invalidation Bypass)
- **Nguyên nhân kỹ thuật:** Khi quản trị viên khóa tài khoản hoặc người dùng đổi mật khẩu, JWT Token cũ vẫn có thể tiếp tục gửi request nếu hệ thống chỉ kiểm tra chữ ký tĩnh.
- **Giải pháp chuẩn:** Duy trì bảng `user_sessions` trong PostgreSQL. `JwtStrategy` đối soát `sessionId` và kiểm tra trường `revokedAt === null`. Khi logout hoặc đổi pass, kích hoạt `revokedAt = new Date()`.

### 3. Kiểm Soát Tài Liệu Swagger Docs trên Môi Trường Production
- **Nguyên nhân kỹ thuật:** Mặc định NestJS Swagger để lộ toàn bộ danh sách API endpoints và schema cơ sở dữ liệu tại `/api/docs`.
- **Giải pháp chuẩn:** Chỉ kích hoạt Swagger khi `process.env.NODE_ENV !== 'production'`. Nếu cần dùng ở môi trường Staging/Dev, bọc middleware xác thực cơ bản (HTTP Basic Auth).

### 4. Xử Lý Hàng Đợi Nền Khi Chuyển Sang Server Độc Lập (BullMQ / Redis)
- **Nguyên nhân kỹ thuật:** Trên Cloud Run, hàng đợi AI Pipeline có thể chạy in-memory tạm thời. Khi chuyển giao hệ thống sang VPS nội bộ với lượng truy cập cao, chạy in-memory sẽ làm crash tiến trình Node.js do cạn bộ nhớ (Out Of Memory).
- **Giải pháp chuẩn:** Khi deploy lên Server nội bộ, bắt buộc bổ sung container Redis trong `docker-compose.yml` và kích hoạt `this.aiPipelineQueue.add('execute')` trong `pipeline.service.ts`.

### 5. Chuẩn Hóa Phiên Bản Mô Hình AI (Gemini Modern Standard)
- **Nguyên nhân kỹ thuật:** Sử dụng các model AI phiên bản cũ đã ngừng hỗ trợ dẫn tới lỗi 404 từ API AI Studio.
- **Giải pháp chuẩn:** Hệ thống quy định sử dụng các model ổn định hiện hành: `gemini-2.5-flash` / `gemini-3-flash` tùy theo cấu hình chiến dịch.

### 6. Xử Lý Bảo Vệ Cấu Hình AI Prompt & Passkey trên `/api/system-configs`
- **Nguyên nhân kỹ thuật (CWE-200 / Information Disclosure):** Endpoint `GET /api/system-configs` nếu mở public sẽ để lộ:
  1. `systemPrompt` của AI kiểm duyệt nội dung an toàn thương hiệu.
  2. Toàn bộ danh sách đen từ khóa cấm (`obsceneBlacklist`, `politicalBlacklist`, `competitorBlacklist`).
  3. Mật khẩu vượt rào bảo trì (`bypassPasskey`).
- **Giải pháp chuẩn:**
  1. **Khóa Auth Admin:** Mọi route cấu hình hệ thống (`/system-configs*`) bắt buộc bọc `@UseGuards(JwtAuthGuard, RolesGuard)` và `@Roles('super_admin', 'admin')`.
  2. **Không trả Secret cho Client:** API public kiểm tra trạng thái bảo trì (`/system-configs/maintenance`) tuyệt đối **KHÔNG** trả về `bypassPasskey`. Mật khẩu vượt bảo trì chỉ được đối soát nội bộ trên server.
  3. **Đánh dấu bí mật trong Database:** Các cấu hình an toàn AI (`brand_safety_config`) lưu cờ `isSecret: true` và lọc bỏ khỏi mọi response chung.

### 7. Nguyên Tắc Zero-Trust Whitelist & Khóa Auth Mặc Định
- **Nguyên nhân kỹ thuật (Broken Auth / API2:2023):** Các endpoint Master Data danh mục chi nhánh (`/campaign/branches`), bộ sưu tập (`/campaign/collections`), hay luồng quét quà QR (`/qr/*`) nếu mở public tùy tiện sẽ tạo điều kiện cho bot cào dữ liệu hoặc kích hoạt nghiệp vụ không kiểm soát.
- **Giải pháp chuẩn:**
  1. **Mặc định Private:** 100% endpoint mới trong Controller được bọc `@UseGuards(JwtAuthGuard)`.
  2. **Yêu cầu Đăng nhập:** Người dùng trước khi quét nhận quà, mở hòm ký ức hoặc tạo thiệp AI đều phải xác thực để có Bearer Token.
  3. **Phê duyệt Whitelist chính thức:** Chỉ những route bắt buộc (Auth login/register, Landing Page, Legal terms, Telemetry) mới được đưa vào danh sách ngoại lệ và có Rate Limiting (`@Throttle`).
  4. **Tự động hóa CI/CD:** Script `npm run test:auth-audit` là chốt chặn kiểm tra tự động trước khi build staging/production.

### 8. Tách Biệt Tầng API Public DTO và Tầng Xử Lý AI Orchestrator (CWE-200: Pipeline Steps)
- **Nguyên nhân kỹ thuật:** Khi mở API công khai chi tiết chiến dịch `GET /api/campaign/slug/:slug` cho khách hàng xem landing page, nếu câu lệnh `include: { pipelineSteps: true }` không được lọc bỏ, toàn bộ `promptTemplate`, `config`, tên model AI và thứ tự các bước AI sẽ bị lộ trên Network tab của trình duyệt.
- **Giải pháp chuẩn:**
  1. **Loại bỏ khỏi API Public:** Client chỉ cần nhận các câu thông điệp xoay vòng tĩnh (`ROTATING_QUOTES`) và % tiến độ từ SSE, không cần đến `pipelineSteps`. Vì vậy, câu lệnh query `getCampaignBySlug` loại bỏ hoàn toàn `pipelineSteps` khỏi `include` và JSON response.
  2. **Xử lý An toàn tại Server:** Backend Orchestrator tự động query trực tiếp từ CSDL (`include: { campaign: { include: { pipelineSteps: true } } }`) khi xử lý tác vụ nền. Toàn bộ luồng kiểm duyệt an toàn và sinh lời chúc AI chạy phía server, độc lập với dữ liệu trả về trình duyệt.
  3. **Phân quyền cho CMS:** API Admin `getCampaignById(id: string)` vẫn giữ nguyên `pipelineSteps` khi có xác thực Token Admin để quản trị viên tùy biến bình thường.

### 9. Phòng Chống Tấn Công Làm Cạn Kiệt Ổ Đĩa Qua Cổng Upload Media (CWE-434 / Storage Exhaustion)
- **Nguyên nhân kỹ thuật:** Các endpoint upload ảnh như `/api/uploads/base64` và `/api/uploads/photos` nếu không có Auth sẽ bị bot khai thác gửi số lượng lớn tệp rác, gây tràn ổ cứng VPS (`No space left on device`), dẫn đến dừng toàn bộ dịch vụ backend.
- **Giải pháp chuẩn:**
  1. Bắt buộc gắn `@UseGuards(JwtAuthGuard)` trên tất cả endpoint upload tệp người dùng.
  2. Áp dụng Rate Limiting `@Throttle({ default: { limit: 15, ttl: 60000 } })` (tối đa 15 file/phút/user).
  3. Kiểm tra Magic Bytes nhị phân (chỉ chấp nhận JPEG, PNG, WebP) và làm sạch tên file chống Path Traversal (`filename.replace(/[^a-zA-Z0-9._-]/g, '')`).

---
*Tài liệu quy chuẩn lưu trữ tại thư mục `C:\Work\Projects\NoiBo\Tech_Operations\standards\`.*
