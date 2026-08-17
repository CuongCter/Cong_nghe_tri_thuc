# TÀI LIỆU KỸ THUẬT: DỰ ÁN PHÂN TÍCH & DỰ BÁO MỨC LƯƠNG NGÀNH DATA SCIENCE

> **Mục đích tài liệu**: Giải thích một cách dễ hiểu toàn bộ dự án — vì sao làm, làm gì, luồng xử lý đi từ dữ liệu thô đến web dự báo ra sao, dùng phương pháp gì, và bài toán đang giải quyết là gì. Người đọc lại có thể nắm được ý nghĩa bài toán và luồng hoạt động từ đầu đến cuối.

---

## MỤC LỤC

1. [Ý tưởng & bài toán](#1-ý-tưởng--bài-toán)
2. [Luồng hoạt động tổng quan](#2-luồng-hoạt-động-tổng-quan)
3. [Dữ liệu đầu vào](#3-dữ-liệu-đầu-vào)
4. [Tiền xử lý dữ liệu](#4-tiền-xử-lý-dữ-liệu)
5. [Phương pháp phân tích & mô hình](#5-phương-pháp-phân-tích--mô-hình)
6. [Kết quả & đánh giá](#6-kết-quả--đánh-giá)
7. [Luồng web dự báo (Flask)](#7-luồng-web-dự-báo-flask)
8. [Cách chạy dự án](#8-cách-chạy-dự-án)
9. [Hạn chế & hướng cải thiện](#9-hạn-chế--hướng-cải-thiện)

---

## 1. Ý TƯỞNG & BÀI TOÁN

### 1.1. Bài toán đặt ra

Trong ngành **Data Science**, mức lương giữa các cá nhân chênh lệch rất lớn — có người $30,000/năm, có người $300,000/năm dù cùng làm một vị trí. Câu hỏi đặt ra:

> **"Mức lương của một vị trí trong ngành Data Science phụ thuộc vào những yếu tố nào, và ta có thể dự đoán được nó không?"**

Đây là bài toán thuộc nhóm **Hồi quy (Regression)** trong Machine Learning — cụ thể là **Hồi quy tuyến tính (Linear Regression)**. Biến cần dự đoán (target) là `salary_in_usd` (mức lương quy đổi ra USD), là một con số thực.

### 1.2. Vì sao chọn Hồi quy tuyến tính?

| Lý do | Giải thích |
|------|-----------|
| **Dễ giải thích** | Hệ số hồi quy cho biết yếu tố nào ảnh hưởng mạnh/yếu đến lương |
| **Dễ triển khai** | Không cần tuning nhiều, chạy nhanh |
| **Đủ tốt cho phân tích ban đầu** | Cho thấy các xu hướng tổng quan |
| **Có công thức toán học rõ ràng** | Có thể dự đoán thủ công qua `intercept + β₁·x₁ + β₂·x₂ + ...` |

### 1.3. Mục tiêu cụ thể

- Tìm ra **các yếu tố ảnh hưởng mạnh nhất** đến lương Data Science.
- Xây dựng **mô hình dự đoán lương** dựa trên 5–7 đặc trưng đầu vào.
- Cung cấp **công cụ web trực quan** để người dùng nhập thông tin và nhận dự báo tức thì.

---

## 2. LUỒNG HOẠT ĐỘNG TỔNG QUAN

Dự án có **hai phần chính** chạy nối tiếp nhau:

### Sơ đồ tổng

```
┌────────────────────────────────────────────────────────────────┐
│                  PHẦN 1: PHÂN TÍCH (Offline)                   │
│                                                                │
│   data-salary.csv (16,534 dòng)                                │
│          │                                                     │
│          ▼                                                     │
│   ┌─────────────────┐                                          │
│   │ Tiền xử lý      │ ─ Lọc job, loại outliers, encode         │
│   └────────┬────────┘                                          │
│            ▼                                                   │
│   ┌─────────────────┐                                          │
│   │ Trích chọn đặc  │ ─ SelectKBest (k=5)                      │
│   │ trưng           │                                          │
│   └────────┬────────┘                                          │
│            ▼                                                   │
│   ┌─────────────────┐                                          │
│   │ Chuẩn hóa       │ ─ Z-Score Normalization                   │
│   └────────┬────────┘                                          │
│            ▼                                                   │
│   ┌─────────────────┐                                          │
│   │ Huấn luyện mô   │ ─ Linear Regression                     │
│   │ hình            │                                          │
│   └────────┬────────┘                                          │
│            ▼                                                   │
│   Hệ số hồi quy (intercept, β₁, β₂, ...)                      │
│   + Bộ scaler (Z-Score mean/std)                               │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                  PHẦN 2: WEB DỰ BÁO (Online)                  │
│                                                                │
│   Người dùng nhập form trên web (index.html)                   │
│          │                                                     │
│          ▼                                                     │
│   POST /api/predict (Flask)                                    │
│          │                                                     │
│          ├─► Mã hóa input (Experience, Job, ...)                │
│          ├─► Z-Score Normalize (dùng scaler từ Phần 1)         │
│          ├─► Model.predict(...)  ─ HOẶC ─                       │
│          └─► Tính bằng hệ số (nếu model lỗi)                  │
│          │                                                     │
│          ▼                                                     │
│   Trả về JSON: { prediction, confidence_lower, ... }           │
│          │                                                     │
│          ▼                                                     │
│   Hiển thị kết quả trên giao diện web                          │
└────────────────────────────────────────────────────────────────┘
```

### Ý nghĩa từng bước

- **Phần 1 chạy 1 lần** để sinh ra bộ hệ số (`MODEL_COEFFICIENTS`) và bộ scaler. Có thể lưu ra file pickle hoặc nhúng trực tiếp vào `app.py`.
- **Phần 2 chạy liên tục**: mỗi lần người dùng nhấn nút "Dự báo" trên web, request POST được gửi đến `/api/predict`, mã hóa + chuẩn hóa, đưa qua mô hình, trả về JSON.

---

## 3. DỮ LIỆU ĐẦU VÀO

### 3.1. Nguồn dữ liệu

File `data-salary.csv` — bộ dữ liệu về lương ngành Khoa học Dữ liệu.

| Thông tin | Giá trị |
|----------|---------|
| Kích thước | 16,534 dòng × 11 cột |
| Khoảng thời gian | 2020 – 2024 |
| Phạm vi lương | $15,000 – $800,000 |
| Giá trị thiếu | Không có |

### 3.2. Mô tả 11 cột

| Cột | Kiểu | Ý nghĩa |
|------|------|---------|
| `work_year` | int | Năm làm việc (2020–2024) |
| `experience_level` | object | Mức kinh nghiệm: `EN` (Entry), `MI` (Mid), `SE` (Senior), `EX` (Executive) |
| `employment_type` | object | Loại hợp đồng: `FT` (Full-time), `PT` (Part-time), `CT` (Contract), `FL` (Freelance) |
| `job_title` | object | Chức danh công việc |
| `salary` | int | Lương theo đồng tiền gốc |
| `salary_currency` | object | Đơn vị tiền tệ gốc |
| `salary_in_usd` | int | **Lương quy đổi USD** ← đây là biến mục tiêu (target) |
| `employee_residence` | object | Quốc gia cư trú của nhân viên |
| `remote_ratio` | int | Tỷ lệ làm việc từ xa (0%, 50%, 100%) |
| `company_location` | object | Quốc gia của công ty |
| `company_size` | object | Quy mô: `S` (Small), `M` (Medium), `L` (Large) |

### 3.3. Top các chức danh phổ biến

| Chức danh | Số lượng |
|-----------|---------:|
| Data Engineer | 3,464 |
| Data Scientist | 3,314 |
| Data Analyst | 2,440 |
| Data Architect | 435 |
| Data Science | 271 |
| Data Manager | 212 |
| Data Science Manager | 122 |
| Data Specialist | 86 |
| Data Science Consultant | 83 |
| Data Analytics Manager | 62 |
| Head of Data | 61 |
| Data Modeler | 56 |
| Data Product Manager | 36 |
| Director of Data Science | 33 |

---

## 4. TIỀN XỬ LÝ DỮ LIỆU

Đây là giai đoạn quan trọng nhất để đảm bảo mô hình học được đúng. Dự án thực hiện **4 bước** theo thứ tự:

### 4.1. Lọc chức danh công việc

**Quy tắc**: Giữ lại các job_title có chứa chữ **"Data"** và xuất hiện **trên 30 lần**.

**Lý do**:
- Tập trung vào nhóm ngành Data Science đúng nghĩa.
- Đảm bảo mỗi job có đủ mẫu để mô hình học (tránh nhiễu từ các job hiếm gặp).

**Kết quả**: Giữ lại 14 loại công việc, dữ liệu giảm từ 16,534 → 10,675 mẫu.

### 4.2. Loại bỏ giá trị ngoại lai (Outliers) bằng IQR

**Phương pháp IQR (Interquartile Range)**:

```
Q1 = $101,125    (phân vị 25%)
Q3 = $185,900    (phân vị 75%)
IQR = Q3 - Q1 = $84,775

Lower bound = Q1 - 1.5 × IQR = -$16,420  (coi như 0)
Upper bound = Q3 + 1.5 × IQR = $289,852
```

Mọi mẫu có lương nằm ngoài khoảng `[0, $289,852]` sẽ bị loại.

**Kết quả**: Loại bỏ 202 mẫu ngoại lai, dữ liệu còn **10,473 mẫu**, lương nằm trong khoảng $15,000 – $288,400.

**Lý do dùng IQR**: Tránh ảnh hưởng của các giá trị cực đoan (ví dụ lương CEO $800,000/năm) làm sai lệch đường hồi quy.

### 4.3. Tạo biến phân loại US vs Non-US

Tạo biến nhị phân `is_us`:
- `is_us = 1`: công ty đặt tại Mỹ
- `is_us = 0`: công ty ngoài Mỹ

**Lý do**: Khi phân tích sơ bộ thấy Mỹ có mức lương cao hơn hẳn các nước khác. Gộp thành 1 biến giúp mô hình dễ học xu hướng này.

### 4.4. Mã hóa biến phân loại (Label Encoding)

Các cột dạng chữ (categorical) được chuyển sang số nguyên:

| Biến | Mapping |
|--------|----------|
| `experience_level` | EN→0, MI→1, SE→2, EX→3 |
| `employment_type` | FT→0, PT→1, CT→2, FL→3 |
| `job_title` | Data Engineer→0, Data Scientist→1, ... (14 mã) |
| `company_size` | S→0, M→1, L→2 |

**Lưu ý quan trọng**: Thứ tự trong mapping được cố định tại `app.py:44-46`. Khi gọi API phải dùng đúng mapping này — nếu truyền giá trị ngoài mapping sẽ gây lỗi `KeyError`.

### 4.5. Trích chọn đặc trưng (SelectKBest)

Dùng `SelectKBest` (thuộc `sklearn.feature_selection`) với **k=5** để chọn ra 5 features có ảnh hưởng mạnh nhất đến lương.

**Top 5 features được chọn (theo F-score)**:

| Hạng | Feature | F-Score |
|-----:|---------|--------:|
| 1 | experience_level_encoded | 986.34 |
| 2 | is_us | 931.06 |
| 3 | job_title_encoded | 504.50 |
| 4 | work_year | 19.15 |
| 5 | employment_type_encoded | 8.42 |

### 4.6. Chuẩn hóa Z-Score

Công thức:

```
z = (x - mean) / std
```

Mỗi feature sẽ được đưa về dạng có mean = 0 và std = 1.

**Vì sao cần?**
- Các feature có thang đo khác nhau (ví dụ `work_year` ~2024, `experience_level` chỉ 0–3). Nếu không chuẩn hóa, feature nào có số lớn hơn sẽ chi phối mô hình.
- Linear Regression đặc biệt nhạy với thang đo.

**Lưu ý khi dự đoán**: Khi nhận input mới, **bắt buộc phải dùng cùng `mean` và `std` đã tính trên tập train** (xem `app.py:143-144` gọi `analyzer.scaler.transform`).

### 4.7. Chia tập Train/Test (80/20)

- **Train**: 8,378 mẫu (80%) — dùng để huấn luyện mô hình.
- **Test**: 2,095 mẫu (20%) — dùng để đánh giá mô hình.

---

## 5. PHƯƠNG PHÁP PHÂN TÍCH & MÔ HÌNH

### 5.1. Hồi quy tuyến tính (Linear Regression)

**Công thức tổng quát**:

```
y = β₀ + β₁·x₁ + β₂·x₂ + ... + βₙ·xₙ
```

Trong đó:
- `y` = mức lương dự đoán
- `β₀` = intercept (điểm gốc khi tất cả features = 0)
- `βᵢ` = hệ số của feature thứ i
- `xᵢ` = giá trị feature thứ i (sau khi chuẩn hóa)

**Thuật toán học**: scikit-learn tìm β bằng **Ordinary Least Squares (OLS)** — cực tiểu hóa tổng bình phương sai số giữa dự đoán và thực tế.

### 5.2. Hệ số hồi quy thu được

Sau huấn luyện, mô hình cho ra các hệ số sau (lưu trong `MODEL_COEFFICIENTS` tại `app.py:32-41`):

| Feature | Hệ số (β) | Ý nghĩa |
|---------|---------:|---------|
| **intercept** | 136,913.07 | Mức lương cơ sở |
| `work_year` | 2,635.11 | Mỗi năm tăng thêm ~$2,635 |
| `experience_level_encoded` | 14,263.28 | Mỗi bậc kinh nghiệm cộng ~$14,263 |
| `employment_type_encoded` | -67.69 | Gần như không ảnh hưởng |
| `job_title_encoded` | 11,506.27 | Mỗi mã job cộng ~$11,506 |
| `remote_ratio` | 293.69 | Mỗi % remote cộng ~$294 |
| `company_size_encoded` | -1,651.69 | Công ty lớn hơn thì giảm nhẹ |
| `is_us` | 15,282.33 | Làm ở Mỹ cộng thêm ~$15,282 |

### 5.3. Công thức dự đoán

Khi API nhận được input từ người dùng, áp dụng:

```
salary = 136913.07
        + 2635.11 × work_year
        + 14263.28 × experience_level_encoded
        + (-67.69) × employment_type_encoded
        + 11506.27 × job_title_encoded
        + 293.69 × remote_ratio
        + (-1651.69) × company_size_encoded
        + 15282.33 × is_us
```

Mã nguồn tại `app.py:177-184`.

### 5.4. Hai luồng dự đoán trong API

`/api/predict` có **2 cơ chế** (xem `app.py:118-121`):

#### Luồng A: Trained model (ưu tiên)

```python
# Bước 1: Mã hóa input thành vector
features = [work_year, experience_level_encoded,
            employment_type_encoded, job_title_encoded,
            remote_ratio, company_size_encoded, is_us]

# Bước 2: Chuẩn hóa bằng scaler đã fit trên tập train
features_normalized = scaler.transform(features)

# Bước 3: Dự đoán
prediction = model.predict(features_normalized)
```

#### Luồng B: Fallback coefficients (khi model lỗi)

Dùng hệ số cứng trong `MODEL_COEFFICIENTS` để tính trực tiếp bằng công thức. Đảm bảo API **luôn trả về kết quả** dù model chưa load được.

---

## 6. KẾT QUẢ & ĐÁNH GIÁ

### 6.1. Các chỉ số đánh giá

| Metric | Train | Test | Ý nghĩa |
|--------|------:|-----:|---------|
| **R² Score** | 0.2284 | 0.2279 | Mô hình giải thích ~22.8% biến thiên lương |
| **MSE** | 2,234,139,149 | 2,205,724,096 | Sai số bình phương trung bình |
| **RMSE** | 47,266.68 | 46,965.14 | Sai số trung bình ~$47k |
| **MAE** | 37,489.36 | 37,530.46 | Sai số tuyệt đối trung bình ~$37.5k |

### 6.2. Tầm quan trọng của các đặc trưng

| Hạng | Feature | Tầm quan trọng |
|-----:|---------|---------------:|
| 1 | is_us | 35.1% |
| 2 | experience_level_encoded | 32.8% |
| 3 | job_title_encoded | 26.7% |
| 4 | work_year | 5.3% |
| 5 | employment_type_encoded | 0.1% |

### 6.3. Khoảng tin cậy (Confidence Interval)

API trả về khoảng tin cậy dựa trên **MAE**:

```
confidence_lower  = max(0, prediction - MAE)
confidence_upper  = prediction + MAE
```

Với MAE = $37,530, khoảng này rộng ~±$37k → phản ánh đúng mức độ chắc chắn của mô hình.

### 6.4. Đánh giá tổng thể

- **R² = 0.228**: Mô hình giải thích được ~23% biến thiên — đây là mức **yếu**, có nghĩa còn rất nhiều yếu tố chưa được đưa vào (kỹ năng cụ thể, công ty, thành phố, v.v.).
- **MAE = $37,530**: Sai số lớn, người dùng nên tham khảo khoảng tin cậy thay vì con số dự đoán chính xác.
- **Không overfit**: Chỉ số train/test gần bằng nhau (0.2284 vs 0.2279).

---

## 7. LUỒNG WEB DỰ BÁO (FLASK)

### 7.1. Kiến trúc

```
┌────────────────────────────────────────────────┐
│              Browser (index.html)              │
│                                                │
│  [Form nhập: 7 trường]                        │
│        │                                       │
│        │ POST /api/predict                     │
│        ▼                                       │
│  ┌──────────────────────────────────────┐     │
│  │   Flask Server (app.py)              │     │
│  │                                      │     │
│  │   validate input ─► encode ─►        │     │
│  │   normalize ─► model.predict ─►      │     │
│  │   confidence interval                │     │
│  └──────────────┬───────────────────────┘     │
│                 │ JSON response               │
│                 ▼                             │
│  [Hiển thị: predicted salary + khoảng ±MAE]   │
└────────────────────────────────────────────────┘
```

### 7.2. Các endpoint

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/` | Trang chủ (index.html) |
| POST | `/api/predict` | Dự đoán lương từ 7 trường input |
| GET | `/api/stats` | Thống kê dataset |
| GET | `/api/job-titles` | Danh sách 14 job titles hợp lệ |
| GET | `/api/health` | Health check |

### 7.3. Ví dụ gọi API

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "work_year": 2024,
    "experience_level": "SE",
    "employment_type": "FT",
    "job_title": "Data Scientist",
    "remote_ratio": 100,
    "company_size": "L",
    "company_location": "US"
  }'
```

**Phản hồi mẫu**:
```json
{
  "prediction": 165000,
  "confidence_lower": 127359,
  "confidence_upper": 202641,
  "method": "trained_model",
  "mae": 37641
}
```

### 7.4. Ý nghĩa thiết kế 2 luồng

- Nếu `analyzer` load được (đã train mô hình trước đó): dùng mô hình thật.
- Nếu lỗi (file pickle không tồn tại, version mismatch...): tự động fallback dùng `MODEL_COEFFICIENTS` cứng.

→ Hệ thống **luôn hoạt động** ổn định, không bao giờ trả về lỗi 500 vì model.

---

## 8. CÁCH CHẠY DỰ ÁN

### 8.1. Phân tích dữ liệu (offline)

```bash
cd "d:/Thạc sĩ/Phân tích dữ liệu/data-engineer-analyst"

# Kích hoạt venv (nếu có)
source venv/Scripts/activate

# Cài dependencies
pip install -r requirements.txt

# Chạy các script phân tích
python salary_visualization.py   # Sinh 11 biểu đồ
python salary_analysis.py        # Phân tích chính
python salary_prediction.py      # Mô hình dự báo
```

### 8.2. Web Flask (online)

```bash
cd "d:/Thạc sĩ/Phân tích dữ liệu/data-engineer-analyst/web"
source ../venv/Scripts/activate
pip install -r requirements.txt
python app.py
```

Mở trình duyệt: **http://localhost:5000**

---

## 9. HẠN CHẾ & HƯỚNG CẢI THIỆN

### 9.1. Hạn chế hiện tại

| Vấn đề | Giải thích |
|--------|-----------|
| R² thấp (22.8%) | Còn ~77% biến thiên lương chưa được giải thích |
| Sai số lớn (MAE ~$37k) | Trên lương trung bình ~$140k, sai số ~27% |
| Chỉ có 7 features | Thiếu các yếu tố quan trọng: kỹ năng cụ thể, thành phố, ngành nghề công ty |
| Giả định tuyến tính | Quan hệ giữa features và lương có thể không hoàn toàn tuyến tính |

### 9.2. Hướng cải thiện

1. **Thu thập thêm features**:
   - Kỹ năng cụ thể (Python, SQL, Spark, Cloud...)
   - Chứng chỉ (AWS, GCP, Azure...)
   - Số năm kinh nghiệm cụ thể (thay vì mã bậc)
   - Thành phố cụ thể (thay vì chỉ US vs Non-US)

2. **Thử mô hình phức tạp hơn**:
   - Random Forest
   - XGBoost / LightGBM
   - Neural Network (cho dữ liệu lớn)

3. **Feature engineering nâng cao**:
   - Tạo tương tác giữa features (vd: `experience_level × is_us`)
   - Polynomial features
   - Target encoding thay vì label encoding

4. **Đánh giá lại**:
   - Cross-validation (5-fold hoặc 10-fold)
   - Tính các metric chuyên sâu hơn (MAPE, R² adjusted)

5. **Cập nhật định kỳ**: Thêm dữ liệu mới mỗi năm để mô hình theo kịp thị trường.

---

## TÓM TẮT

| Thành phần | Nội dung |
|-----------|---------|
| **Bài toán** | Hồi quy — dự đoán mức lương ngành Data Science |
| **Dữ liệu** | 16,534 dòng → sau xử lý 10,473 dòng |
| **Phương pháp** | Linear Regression + Z-Score Normalization + SelectKBest (k=5) |
| **Top features** | is_us (35%), experience_level (33%), job_title (27%) |
| **Hiệu suất** | R² = 0.228, MAE = $37,530 |
| **Giao diện** | Flask web (Python backend) + Bootstrap frontend |
| **Input dự đoán** | 7 trường: work_year, experience_level, employment_type, job_title, remote_ratio, company_size, company_location |
| **Output** | prediction + confidence interval (±MAE) |

---

*Tài liệu này tổng hợp lại toàn bộ dự án để người đọc có thể hiểu ý nghĩa bài toán, phương pháp áp dụng, và luồng hoạt động từ dữ liệu thô đến web dự báo.*