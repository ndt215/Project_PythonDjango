# NHIỆM VỤ DÀNH CHO DEEPSEEK: KHỞI TẠO BỘ KHUNG DỰ ÁN DJANGO REST API (PYCHARM)

> **LƯU Ý DÀNH CHO DEEPSEEK:**  
> 1. Bạn đang làm việc **trực tiếp tại thư mục gốc của project Django mới trong PyCharm**. Không tạo thêm thư mục con dạng `backend/`.  
> 2. **Chưa cần tạo database trước**: Trong Django, CSDL (SQLite) sẽ được tự động tạo thông qua lệnh `migrate` sau khi bạn viết xong `models.py`.  
> 3. **Mục tiêu chính:** Tạo bộ khung cấu trúc chuẩn (boilerplate/skeleton), viết đầy đủ các Models đại diện cho 10 bảng nghiệp vụ, cấu hình file settings, serializers, views và urls cơ bản để người mới học dễ tiếp cận.

---

## 1. THIẾT KẾ CƠ SỞ DỮ LIỆU CẦN TRIỂN KHAI (10 BẢNG)
*Được tham chiếu từ thiết kế hệ thống Măm Măm Food Review:*
- **Quy chuẩn:** Dữ liệu hỗ trợ tiếng Việt có dấu (`verbose_name`), đơn vị tiền tệ VNĐ, đối tượng người dùng gồm: Quản trị viên, Thành viên đã đăng ký, Khách.

1. **`NguoiDung`** (hoặc mở rộng `AbstractUser`): Họ tên, email, mật khẩu, ảnh đại diện, tiểu sử, vai trò (`'quan_tri_vien'`, `'thanh_vien'`, `'khach'`), trạng thái (`'hoat_dong'`, `'bi_khoa'`).
2. **`NhaHang`**: Tên quán, địa chỉ, quận/huyện, thành phố, số điện thoại, loại ẩm thực (Món Việt, Món nước, Hải sản,...), giá từ (VNĐ), giá đến (VNĐ), giờ mở/đóng cửa.
3. **`TheMonAn`**: Tên thẻ (tag), slug.
4. **`BaiReview`**: Khóa ngoại `nguoi_dung`, `nha_hang`. Tiêu đề, nội dung review, điểm trung bình (float), trạng thái (`'cho_duyet'`, `'da_dang'`, `'an'`), lượt thích, quan hệ nhiều-nhiều với `TheMonAn`.
5. **`ChamDiem`** (One-to-One với `BaiReview`): 4 tiêu chí chấm điểm từ 1.0 đến 5.0 gồm `vi_giac`, `khong_gian`, `phuc_vu`, `gia_ca`.
6. **`HinhAnh`**: Khóa ngoại `bai_review`, trường `ImageField(upload_to='reviews/')`, mô tả, cờ `la_anh_bia`, thứ tự.
7. **`BinhLuan`**: Khóa ngoại `bai_review`, `nguoi_dung`, nội dung, lượt thích, ngày tạo.
8. **`LuotThich`**: Khóa ngoại `nguoi_dung` và `bai_review`, ràng buộc `unique_together`.
9. **`QuanYeuThich`**: Khóa ngoại `nguoi_dung` và `nha_hang` (bookmark quán), ràng buộc `unique_together`.
10. **`TheoDoi`**: `nguoi_theo_doi` và `nguoi_duoc_theo_doi` (FK tới `NguoiDung`), ràng buộc `unique_together`.

---

## 2. CÂY THƯ MỤC CẦN BUILD NGAY TẠI THƯ MỤC NÀY

```text
. (Thư mục gốc của project PyCharm)
├── manage.py
├── requirements.txt
├── README.md                          # Hướng dẫn chạy cho người mới học
├── core/                              # Gói cấu hình dự án (Django Project Settings)
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                   # Cấu hình CSDL SQLite, DRF, CORS, Media, Tiếng Việt
│   ├── urls.py                       # Root URLs
│   └── wsgi.py
├── reviews/                           # Ứng dụng chính (Django App)
│   ├── __init__.py
│   ├── admin.py                      # Đăng ký 10 models vào trang quản trị
│   ├── apps.py
│   ├── models.py                     # Định nghĩa 10 Models ORM
│   ├── serializers.py                # ModelSerializer cho các model chính
│   ├── views.py                      # API Views/ViewSets cơ bản trả về JSON
│   ├── urls.py                       # Routing các endpoint API
│   └── migrations/
│       └── __init__.py
└── media/                            # Nơi chứa file ảnh upload (tạo sẵn folder rỗng)
```

---

## 3. YÊU CẦU CHI TIẾT TỪNG FILE

### A. `requirements.txt`
```text
Django>=5.0,<6.0
djangorestframework>=3.15.0
django-cors-headers>=4.3.0
Pillow>=10.0.0
```

### B. `core/settings.py`
- Thêm vào `INSTALLED_APPS`: `'rest_framework'`, `'corsheaders'`, `'reviews'`.
- Thêm middleware: `'corsheaders.middleware.CorsMiddleware'` lên đầu danh sách `MIDDLEWARE`.
- Ngôn ngữ & thời gian:
  ```python
  LANGUAGE_CODE = 'vi'
  TIME_ZONE = 'Asia/Ho_Chi_Minh'
  USE_I18N = True
  USE_TZ = True
  ```
- CSDL dùng SQLite mặc định: `BASE_DIR / 'db.sqlite3'`.
- Media upload config:
  ```python
  MEDIA_URL = '/media/'
  MEDIA_ROOT = BASE_DIR / 'media'
  ```
- Cho phép CORS (để dễ test REST API):
  ```python
  CORS_ALLOW_ALL_ORIGINS = True
  ```

### C. `core/urls.py`
- Include router của app `reviews`: `path('api/', include('reviews.urls'))`.
- Cấu hình phục vụ file media khi ở chế độ `DEBUG = True`.

### D. `reviews/models.py`
- Viết đầy đủ 10 Model theo đúng mục 1.
- Sử dụng `verbose_name` tiếng Việt cho từng trường.
- Đặt phương thức `__str__` có ý nghĩa cho từng model để hiển thị đẹp mắt trên trang Admin.

### E. `reviews/admin.py`
- Đăng ký đầy đủ các Model vào `admin.site.register(...)` để người dùng có thể dùng giao diện Web Admin quản lý ngay.

### F. `reviews/serializers.py` & `reviews/views.py` & `reviews/urls.py`
- Dựng khung sẵn các `ModelSerializer` cho `NhaHang`, `BaiReview`, `BinhLuan`, `TheMonAn`.
- Viết các View cơ bản (có thể dùng `viewsets.ModelViewSet` hoặc `generics.ListCreateAPIView`).
- Đăng ký các route API vào `reviews/urls.py` (ví dụ: `/api/nha-hang/`, `/api/bai-review/`,...).

### G. `README.md` (Hướng dẫn cụ thể cho người mới)
Ghi chú rõ ràng 4 bước thực hiện trong Terminal của PyCharm:
1. `pip install -r requirements.txt`
2. `python manage.py makemigrations` (Tạo kịch bản migration từ `models.py`)
3. `python manage.py migrate` (Khởi tạo toàn bộ bảng trong file `db.sqlite3`)
4. `python manage.py createsuperuser` (Tạo tài khoản admin để đăng nhập vào trang web quản trị)
5. `python manage.py runserver` (Khởi chạy máy chủ API)

---

## 4. TIÊU CHÍ HOÀN THÀNH
- Không báo lỗi cú pháp Python.
- Khi người dùng chạy lệnh `python manage.py makemigrations` và `migrate`, hệ thống tự sinh ra file `db.sqlite3` với 10 bảng hoàn chỉnh mà không gặp lỗi.
