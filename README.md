# Măm Măm Food Review - Bộ khung Django REST API

Dự án mẫu dành cho người mới học Django + Django REST Framework: quản lý nhà hàng,
bài review ẩm thực, chấm điểm, hình ảnh, bình luận, lượt thích và theo dõi người dùng.

Bộ khung này đã có sẵn **10 bảng dữ liệu**, cấu hình SQLite, DRF, CORS, khu vực
media và giao diện Admin tiếng Việt. Bạn chỉ cần chạy vài lệnh là có API hoạt động.

> **Phiên bản:** Django 6.1 + Django REST Framework 3.18 + django-cors-headers 4.9 + Pillow 12.
> Django 6.1 yêu cầu **Python 3.12 trở lên** (khuyến nghị Python 3.13/3.14).
> Các ràng buộc dữ liệu dùng `UniqueConstraint` / `CheckConstraint` - cách khai báo
> hiện đại của Django, thay cho `unique_together` đã cũ.

---

## 1. Cây thư mục dự án

```text
Project_Forum/                  <- Thư mục gốc, nơi chứa manage.py
├── manage.py                   <- Công cụ dòng lệnh Django
├── requirements.txt            <- Danh sách thư viện cần cài
├── README.md                   <- File hướng dẫn này
├── .gitignore
├── core/                       <- Gói cấu hình dự án
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py             <- Cấu hình SQLite, DRF, CORS, Media, tiếng Việt
│   ├── urls.py                 <- URL gốc (/admin/, /api/, /media/)
│   └── wsgi.py
├── reviews/                    <- Ứng dụng chính
│   ├── __init__.py
│   ├── admin.py                <- Đăng ký 10 model vào trang quản trị
│   ├── apps.py
│   ├── models.py               <- 10 bảng ORM
│   ├── serializers.py          <- Chuyển Model <-> JSON
│   ├── views.py                <- ViewSet cho từng bảng
│   ├── urls.py                 <- Router API
│   └── migrations/
│       └── __init__.py
└── media/                      <- Nơi lưu ảnh upload (reviews/, avatars/)
```

---

## 2. Cài đặt và chạy (5 bước trong Terminal của PyCharm)

> **Mẹo:** Trong PyCharm, mở **View > Tool Windows > Terminal** (hoặc `Alt + F12`).
> Nếu đã tạo Virtual Environment, PyCharm thường tự kích hoạt sẵn (thấy `(.venv)` ở đầu dòng lệnh).

### Bước 1 - Cài thư viện

```bash
pip install -r requirements.txt
```

Nếu máy có nhiều phiên bản Python, dùng:

```bash
python -m pip install -r requirements.txt
```

### Bước 2 - Tạo kịch bản migration từ `models.py`

```bash
python manage.py makemigrations
```

Lệnh này đọc `reviews/models.py` và sinh file `reviews/migrations/0001_initial.py`.

### Bước 3 - Tạo các bảng trong CSDL SQLite

```bash
python manage.py migrate
```

Sau lệnh này, file **`db.sqlite3`** xuất hiện ngay trong thư mục gốc (cạnh `manage.py`).

### Bước 4 - Tạo tài khoản quản trị

```bash
python manage.py createsuperuser
```

Nhập username, email và mật khẩu (mật khẩu không hiển thị khi gõ, cứ gõ rồi Enter).

### Bước 5 - Khởi chạy server

```bash
python manage.py runserver
```

Mở trình duyệt:

| Địa chỉ | Mô tả |
| --- | --- |
| http://127.0.0.1:8000/api/ | Trang gốc API, liệt kê mọi endpoint |
| http://127.0.0.1:8000/api/tong-quan/ | Kiểm tra nhanh API và số bản ghi |
| http://127.0.0.1:8000/api/nha-hang/ | Danh sách nhà hàng (JSON) |
| http://127.0.0.1:8000/admin/ | Trang quản trị (đăng nhập bằng superuser) |

---

## 3. 10 bảng dữ liệu

| # | Model | Ý nghĩa | Điểm đáng chú ý |
| --- | --- | --- | --- |
| 1 | `NguoiDung` | Người dùng | Kế thừa `AbstractUser`; vai trò `quan_tri_vien` / `thanh_vien` / `khach`; trạng thái `hoat_dong` / `bi_khoa` |
| 2 | `NhaHang` | Quán ăn | Địa chỉ, quận/huyện, thành phố, loại ẩm thực, giá từ - giá đến (VNĐ), giờ mở/đóng cửa, slug tự sinh |
| 3 | `TheMonAn` | Thẻ món ăn | Tên thẻ + slug tự sinh |
| 4 | `BaiReview` | Bài review | FK người dùng + nhà hàng, điểm trung bình, trạng thái duyệt, M2M với thẻ món ăn |
| 5 | `ChamDiem` | Chấm điểm | One-to-One với bài review; 4 tiêu chí 1.0 - 5.0: vị giác, không gian, phục vụ, giá cả |
| 6 | `HinhAnh` | Ảnh | `ImageField(upload_to='reviews/')`, mô tả, cờ ảnh bìa, thứ tự |
| 7 | `BinhLuan` | Bình luận | FK bài review + người dùng, lượt thích, ngày tạo |
| 8 | `LuotThich` | Lượt thích bài | `UniqueConstraint` (người dùng, bài review) |
| 9 | `QuanYeuThich` | Quán bookmark | `UniqueConstraint` (người dùng, nhà hàng) |
| 10 | `TheoDoi` | Theo dõi | `UniqueConstraint` (người theo dõi, người được theo dõi) + `CheckConstraint` chặn tự theo dõi |

> **Quan trọng:** `settings.py` đã khai báo `AUTH_USER_MODEL = 'reviews.NguoiDung'`.
> Không đổi tên model này sau khi đã chạy `migrate`, nếu không phải xóa `db.sqlite3`
> và tạo lại từ đầu.

---

## 4. Danh sách endpoint API

Mỗi endpoint đều hỗ trợ đủ 5 thao tác: `GET` (danh sách), `POST` (tạo),
`GET /{id}/` (chi tiết), `PUT/PATCH /{id}/` (sửa), `DELETE /{id}/` (xóa).

| Endpoint | Bảng tương ứng |
| --- | --- |
| `/api/nguoi-dung/` | Người dùng |
| `/api/nha-hang/` | Nhà hàng |
| `/api/the-mon-an/` | Thẻ món ăn |
| `/api/bai-review/` | Bài review |
| `/api/cham-diem/` | Chấm điểm |
| `/api/hinh-anh/` | Hình ảnh |
| `/api/binh-luan/` | Bình luận |
| `/api/luot-thich/` | Lượt thích |
| `/api/quan-yeu-thich/` | Quán yêu thích |
| `/api/theo-doi/` | Theo dõi |
| `/api/tong-quan/` | Thống kê số bản ghi |

### Bộ lọc và tìm kiếm có sẵn

```text
/api/nha-hang/?search=phở                # tìm theo tên, địa chỉ, quận, thành phố
/api/nha-hang/?loai_am_thuc=hai_san      # lọc theo loại ẩm thực
/api/nha-hang/?ordering=gia_tu           # sắp xếp theo giá

/api/bai-review/?nha_hang=1              # bài review của một nhà hàng
/api/bai-review/?nguoi_dung=2            # bài review của một người
/api/bai-review/?trang_thai=da_dang      # lọc theo trạng thái duyệt
/api/binh-luan/?bai_review=1             # bình luận của một bài
```

Dữ liệu được phân trang tự động, mỗi trang 10 bản ghi:

```json
{
  "count": 25,
  "next": "http://127.0.0.1:8000/api/nha-hang/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

---

## 5. Ví dụ gọi API

### Tạo nhà hàng (PowerShell / cmd dùng `curl.exe`)

```bash
curl -X POST http://127.0.0.1:8000/api/nha-hang/ ^
  -H "Content-Type: application/json" ^
  -d "{\"ten_quan\":\"Bún chả Hà Nội\",\"dia_chi\":\"12 Lê Lợi\",\"quan_huyen\":\"Quận 1\",\"thanh_pho\":\"TP. Hồ Chí Minh\",\"so_dien_thoai\":\"0901234567\",\"loai_am_thuc\":\"mon_viet\",\"gia_tu\":30000,\"gia_den\":80000,\"gio_mo_cua\":\"08:00\",\"gio_dong_cua\":\"22:00\"}"
```

### Tạo thẻ món ăn

```bash
curl -X POST http://127.0.0.1:8000/api/the-mon-an/ ^
  -H "Content-Type: application/json" ^
  -d "{\"ten_the\":\"Bún chả\"}"
```

### Tạo bài review

```bash
curl -X POST http://127.0.0.1:8000/api/bai-review/ ^
  -H "Content-Type: application/json" ^
  -d "{\"nguoi_dung\":1,\"nha_hang\":1,\"tieu_de\":\"Rất đáng thử\",\"noi_dung\":\"Thịt nướng thơm, nước chấm vừa vị.\",\"the_mon_an\":[1]}"
```

### Chấm điểm cho bài review (tự cập nhật `diem_trung_binh`)

```bash
curl -X POST http://127.0.0.1:8000/api/cham-diem/ ^
  -H "Content-Type: application/json" ^
  -d "{\"bai_review\":1,\"vi_giac\":5,\"khong_gian\":4,\"phuc_vu\":4,\"gia_ca\":5}"
```

### Tải ảnh lên (multipart/form-data)

```bash
curl -X POST http://127.0.0.1:8000/api/hinh-anh/ ^
  -F "bai_review=1" ^
  -F "hinh_anh=@C:\duong\dan\anh.jpg" ^
  -F "mo_ta=Ảnh mặt tiền quán" ^
  -F "la_anh_bia=true" ^
  -F "thu_tu=1"
```

> **Gợi ý cho người mới:** mở trực tiếp `http://127.0.0.1:8000/api/nha-hang/`
> bằng trình duyệt để dùng giao diện **Browsable API** - có form nhập liệu,
> không cần cài Postman.

---

## 6. Ghi chú kỹ thuật

- **Phiên bản:** Django 6.1 yêu cầu Python 3.12+. Nếu máy đang dùng Python 3.11 trở
  xuống, hãy cài Python mới hoặc hạ Django xuống 5.2 (khi đó đổi `Meta.constraints`
  `CheckConstraint(condition=...)` thành `check=...`).
- **CSDL:** SQLite (`db.sqlite3`), không cần cài MySQL/PostgreSQL.
- **Media:** ảnh lưu vào `media/reviews/` (ảnh review) và `media/avatars/` (ảnh đại diện).
  Django tự tạo thư mục con khi có file đầu tiên được upload.
- **CORS:** đang mở cho mọi nguồn (`CORS_ALLOW_ALL_ORIGINS = True`) để tiện test.
  Khi triển khai thật, đổi thành `CORS_ALLOWED_ORIGINS = [...]`.
- **Phân quyền:** hiện tại API cho phép mọi người gọi (`AllowAny`) để dễ học.
  Khi làm thật, thay bằng `IsAuthenticatedOrReadOnly` hoặc `IsAuthenticated`.
- **Múi giờ:** `Asia/Ho_Chi_Minh`, ngôn ngữ `vi`.

---

## 7. Lỗi thường gặp

| Thông báo lỗi | Cách khắc phục |
| --- | --- |
| `No module named 'django'` | Chưa kích hoạt venv hoặc chưa chạy `pip install -r requirements.txt` |
| `Django 6.1 requires Python 3.12+` | Cập nhật Python lên 3.12 trở lên rồi tạo lại venv |
| `No module named 'rest_framework'` | Thiếu `djangorestframework`, chạy lại lệnh pip ở Bước 1 |
| `No module named 'corsheaders'` | Thiếu `django-cors-headers`, chạy lại lệnh pip ở Bước 1 |
| `Cannot use ImageField because Pillow is not installed` | Chạy `pip install Pillow` |
| `You have ... unapplied migrations` | Chạy `python manage.py migrate` |
| `no such table: reviews_nguoidung` | Chưa chạy `makemigrations` + `migrate` |
| `that port is already in use` | Đổi cổng: `python manage.py runserver 8001` |
| `django.db.utils.OperationalError: no such table` | Đã xóa/di chuyển `db.sqlite3` nhưng chưa `migrate` lại |
| Mật khẩu superuser bị quên | `python manage.py changepassword <username>` |

### Muốn xóa và làm lại CSDL từ đầu?

```bash
# Xóa file db.sqlite3 trong thư mục gốc, sau đó:
python manage.py migrate
python manage.py createsuperuser
```

---

## 8. Các lệnh Django hữu ích khác

```bash
python manage.py shell            # Mở Python shell có sẵn Django ORM
python manage.py check            # Kiểm tra lỗi cấu hình
python manage.py showmigrations   # Xem migration đã áp dụng chưa
python manage.py makemigrations --empty reviews   # Tạo migration rỗng (viết tay)
python manage.py collectstatic    # Gom file tĩnh khi triển khai thật
```

Chúc bạn học Django vui vẻ! 🍜
