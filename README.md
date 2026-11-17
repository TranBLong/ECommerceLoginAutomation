# E-Commerce Login Test Automation (EP + BVA)

Dự án test automation cho chức năng **Login** của website  
👉 https://e-commerce-for-testing.onrender.com

Dựa trên bộ test case **Equivalence Partitioning (EP)** và **Boundary Value Analysis (BVA)** từ file `TestCases_Login_EP_BVA.xlsx`.

## 📋 Danh sách Test Case

| ID | Tên Test Case | Loại | Mô tả ngắn |
|----|---------------|------|------------|
| TC_LOGIN_01 | Valid login | Positive (EP) | Đăng nhập thành công với account hợp lệ |
| TC_LOGIN_02 | Unregistered email | Negative (EP) | Email chưa đăng ký |
| TC_LOGIN_03 | Incorrect password | Negative (EP) | Sai mật khẩu |
| TC_LOGIN_04 | Invalid email format | Negative (EP) | Email thiếu ký tự `@` |
| TC_LOGIN_05 | Empty email | Negative (EP) | Để trống email |
| TC_LOGIN_06 | Empty password | Negative (EP) | Để trống password |
| TC_LOGIN_07 | Both empty | Negative (EP) | Cả hai field trống |
| TC_LOGIN_08 | Password min boundary | Positive (BVA) | Password đúng độ dài tối thiểu (8 ký tự) |
| TC_LOGIN_09 | Password below min | Negative (BVA) | Password dưới 8 ký tự |

> **Lưu ý**: Trong file Excel gốc, TC_LOGIN_08 ghi "6 characters" nhưng dữ liệu test và message lỗi thực tế của hệ thống là **8 ký tự**. Dự án đã chỉnh theo thực tế.

## 🛠 Công nghệ sử dụng

- **Python 3.10+**
- **Selenium 4**
- **unittest** + **html-testRunner** (hoặc pytest)
- **Page Object Model (POM)**
- **webdriver-manager** (tự động quản lý chromedriver)

## 📁 Cấu trúc dự án

```
e-commerce-login-automation/
├── config.ini                 # Cấu hình URL + credentials
├── requirements.txt
├── README.md
├── pages/
│   └── login_page.py          # Page Object của trang Sign In
├── tests/
│   └── test_login_ep_bva.py   # 9 test cases EP + BVA
├── utils/
│   └── browser_setup.py       # Khởi tạo WebDriver
├── reports/                   # HTML report sau khi chạy test
└── resources/                 # (optional) chromedriver local
```

## ⚙️ Cài đặt

```bash
# 1. Clone / copy project
cd e-commerce-login-automation

# 2. Tạo virtual environment (khuyến nghị)
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Cài thư viện
pip install -r requirements.txt
```

## ▶️ Chạy test

### Cách 1: Chạy bằng unittest + HTML report

```bash
python tests/test_login_ep_bva.py
```

Report sẽ được tạo trong thư mục `reports/`.

### Cách 2: Chạy bằng pytest (nếu thích)

```bash
pytest tests/test_login_ep_bva.py -v --html=reports/report.html --self-contained-html
```

### Chạy 1 test case cụ thể

```bash
python -m unittest tests.test_login_ep_bva.TestLoginEPBVA.test_TC_LOGIN_01_valid_login
```

## 🔧 Cấu hình

Mở file `config.ini`:

```ini
[app]
base_url = https://e-commerce-for-testing.onrender.com
login_url = https://e-commerce-for-testing.onrender.com/signin

[credentials]
valid_email = adminit24m@gmail.com
valid_password = admin123
```

Nếu muốn dùng chromedriver local (Windows), điền path vào:

```ini
[webdriver]
driver_path = C:\path\to\chromedriver.exe
```

Nếu để trống, project sẽ tự động tải chromedriver bằng `webdriver-manager`.

## 📌 Ghi chú quan trọng

1. Website đang host trên **Render** → đôi khi cold start chậm. Nếu test fail do timeout, chạy lại.
2. Account `adminit24m@gmail.com` / `admin123` được lấy từ file test case gốc.
3. Message lỗi của hệ thống đang hiển thị bằng **tiếng Việt** (ví dụ: "Bạn chưa nhập địa chỉ email").
4. Project sử dụng **Explicit Wait** + Page Object Model để tăng độ ổn định.

## 👤 Nguồn tham khảo

- Repo gốc: https://github.com/taquocy/e-commerce-for-test-automation
- Test case do Claude tạo (EP + BVA)
- Website Under Test: https://e-commerce-for-testing.onrender.com
