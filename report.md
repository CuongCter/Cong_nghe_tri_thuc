# CHƯƠNG 3: THỰC NGHIỆM VÀ ĐÁNH GIÁ

## 3.1. Tìm hiểu dữ liệu

### 3.1.1. Thông tin cơ bản về dữ liệu (từ `load_data()`)

Dữ liệu được sử dụng trong nghiên cứu này là bộ dữ liệu về lương trong lĩnh vực khoa học dữ liệu với các thông tin cơ bản sau:

- **Kích thước dữ liệu**: 16,534 dòng × 11 cột
- **Số dòng**: 16,534 mẫu dữ liệu
- **Số cột**: 11 thuộc tính
- **Khoảng thời gian**: Từ năm 2020 đến 2024
- **Phạm vi lương**: Từ $15,000 đến $800,000 USD

### 3.1.2. Khám phá và tóm lược dữ liệu (từ `explore_data()`)

#### Thông tin các cột (`df.info()`)

Bộ dữ liệu bao gồm 11 cột với các kiểu dữ liệu như sau:

| STT | Tên cột | Kiểu dữ liệu | Mô tả |
|-----|---------|--------------|-------|
| 0 | work_year | int64 | Năm làm việc |
| 1 | experience_level | object | Mức độ kinh nghiệm |
| 2 | employment_type | object | Loại hình việc làm |
| 3 | job_title | object | Chức danh công việc |
| 4 | salary | int64 | Lương theo đồng tiền địa phương |
| 5 | salary_currency | object | Đơn vị tiền tệ |
| 6 | salary_in_usd | int64 | Lương quy đổi USD |
| 7 | employee_residence | object | Nơi cư trú nhân viên |
| 8 | remote_ratio | int64 | Tỷ lệ làm việc từ xa |
| 9 | company_location | object | Địa điểm công ty |
| 10 | company_size | object | Quy mô công ty |

#### Thống kê mô tả (`df.describe()`)

| Chỉ số | work_year | salary | salary_in_usd | remote_ratio |
|--------|-----------|--------|---------------|--------------|
| count | 16,534 | 16,534 | 16,534 | 16,534 |
| mean | 2023.23 | 163,727 | 149,687 | 32.00 |
| std | 0.71 | 340,206 | 68,505 | 46.25 |
| min | 2020 | 14,000 | 15,000 | 0 |
| 25% | 2023 | 101,763 | 101,125 | 0 |
| 50% | 2023 | 142,200 | 141,300 | 0 |
| 75% | 2024 | 187,200 | 185,900 | 100 |
| max | 2024 | 30,400,000 | 800,000 | 100 |

#### Kiểm tra giá trị thiếu

Kết quả kiểm tra cho thấy **không có giá trị thiếu** trong toàn bộ bộ dữ liệu, đảm bảo tính toàn vẹn của dữ liệu.

#### Phân tích các cột categorical và numerical

**Top 20 job title chứa từ "Data":**

| Chức danh | Số lượng |
|-----------|----------|
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

## 3.2. Tiền xử lý dữ liệu

### 3.2.1. Làm sạch dữ liệu (từ `clean_data()`)

#### Lọc job title chứa "Data" và xuất hiện > 30 lần

Để đảm bảo tính đại diện và độ tin cậy của mô hình, nghiên cứu chỉ giữ lại các chức danh:
- Chứa từ "Data" trong tên
- Xuất hiện trên 30 lần trong bộ dữ liệu

**Kết quả**: 14 loại công việc được giữ lại, giảm kích thước dữ liệu từ 16,534 xuống 10,675 mẫu.

#### Phân tích outliers bằng phương pháp IQR

**Thống kê lương sau khi lọc job title:**
- Min: $15,000
- Max: $774,000  
- Median: $135,000
- Mean: $140,563
- Std: $60,510

**Phương pháp IQR:**
- Q1 (25%): $101,125
- Q3 (75%): $185,900
- IQR = Q3 - Q1 = $84,775
- Lower bound = Q1 - 1.5 × IQR = -$16,420
- Upper bound = Q3 + 1.5 × IQR = $289,852

#### Loại bỏ outliers

- **Số outliers được loại bỏ**: 202 mẫu
- **Kích thước dữ liệu cuối cùng**: 10,473 mẫu
- **Khoảng lương sau xử lý**: $15,000 - $288,400

#### Tạo biến phân loại US vs Non-US

Tạo biến `is_us` để phân biệt công ty tại Mỹ và ngoài Mỹ:
- `is_us = 1`: Công ty tại Mỹ
- `is_us = 0`: Công ty ngoài Mỹ

### 3.2.2. Mã hóa dữ liệu (từ `preprocess_data()`)

#### Label Encoding cho biến categorical

| Biến | Số categories |
|------|---------------|
| experience_level | 4 |
| employment_type | 4 |
| job_title | 14 |
| company_size | 3 |

#### Chia tách dữ liệu train/test (80/20)

- **Tập huấn luyện**: 8,378 mẫu (80%)
- **Tập kiểm tra**: 2,095 mẫu (20%)

#### Chuẩn hóa dữ liệu (Z-Score Normalization)

Áp dụng chuẩn hóa Z-Score sau khi trích chọn thuộc tính để đảm bảo tính nhất quán.

#### Trích chọn thuộc tính (SelectKBest với k=5)

**Top 5 features được chọn:**

| Feature | F-Score |
|---------|---------|
| experience_level_encoded | 986.34 |
| is_us | 931.06 |
| job_title_encoded | 504.50 |
| work_year | 19.15 |
| employment_type_encoded | 8.42 |

## 3.3. Xây dựng và huấn luyện mô hình

### 3.3.1. Mô hình hồi quy tuyến tính (từ `train_models()`)

#### Thiết lập mô hình Linear Regression

- **Thuật toán**: Linear Regression từ scikit-learn
- **Phương pháp chuẩn hóa**: Z-Score Normalization
- **Số features**: 5 (đã được trích chọn)

#### Huấn luyện trên tập train

Mô hình được huấn luyện trên 8,378 mẫu với 5 features đã được chuẩn hóa.

#### Dự đoán trên tập test

Thực hiện dự đoán trên 2,095 mẫu trong tập kiểm tra.

## 3.4. Đánh giá mô hình

### 3.4.1. Các chỉ số đánh giá (từ `print_model_evaluation()`)

| Metric | Train | Test |
|--------|-------|------|
| **R² Score** | 0.2284 | **0.2279** |
| **MSE** | 2,234,139,149.60 | **2,205,724,096.38** |
| **RMSE** | 47,266.68 | **46,965.14** |
| **MAE** | 37,489.36 | **37,530.46** |

### 3.4.2. Phân tích kết quả

#### Tầm quan trọng của 5 features được chọn

| Rank | Feature | Tầm quan trọng |
|------|---------|----------------|
| 1 | is_us | 35.1% |
| 2 | experience_level_encoded | 32.8% |
| 3 | job_title_encoded | 26.7% |
| 4 | work_year | 5.3% |
| 5 | employment_type_encoded | 0.1% |

#### Phân tích hệ số hồi quy

**Intercept (β₀)**: $136,913.07

**Hệ số hồi quy (βᵢ):**
- work_year: 2,302.03
- experience_level_encoded: 14,195.57
- employment_type_encoded: -64.46
- job_title_encoded: 11,564.17
- is_us: 15,215.21

#### So sánh dự đoán vs thực tế

- **R² Score**: 0.2279 - Mô hình giải thích được 22.8% biến thiên của mức lương
- **Đánh giá**: Yếu - Mô hình cần cải thiện đáng kể
- **RMSE**: $46,965.14 (34.4% của mức lương trung bình)

## 3.5. Trực quan hóa kết quả

### 3.5.1. Biểu đồ khám phá dữ liệu

Các biểu đồ được tạo ra bao gồm:

1. **Phân phối lương theo experience level** (`01_data_distribution.png`)
2. **So sánh US vs Non-US** (`02_data_analysis.png`)
3. **Xu hướng lương theo năm** (trong các biểu đồ phân tích)

### 3.5.2. Biểu đồ đánh giá mô hình

1. **Feature importance chart** (`04_selected_feature_importance.png`)
2. **Correlation matrix** (`05_correlation_matrix.png`)
3. **Model results** (`03_model_results.png`)

## 3.6. Ứng dụng dự báo

### 3.6.1. Hệ thống dự báo lương (từ `SalaryPrediction`)

Hệ thống dự báo được xây dựng với các tính năng:

#### Input validation
- Kiểm tra tính hợp lệ của dữ liệu đầu vào
- Xử lý các giá trị ngoài phạm vi

#### Preprocessing pipeline
- Label encoding cho biến categorical
- Feature selection
- Z-score normalization

#### Prediction với confidence interval
- Dự đoán mức lương
- Tính toán khoảng tin cậy dựa trên MAE

### 3.6.2. Kết quả dự báo mẫu

#### Ví dụ dự báo cho các kịch bản khác nhau

Hệ thống có thể dự báo lương cho nhiều kịch bản khác nhau được minh họa trong `06_prediction_scenarios.png`.

#### Phân tích độ tin cậy

- **MAE**: $37,530.46 - Sai số trung bình tuyệt đối
- **Confidence interval**: ±$37,530 (khoảng tin cậy 68%)
- **Độ chính xác**: 22.8% (R² Score)

## Kết luận

Mô hình hồi quy tuyến tính đã được xây dựng thành công với khả năng giải thích 22.8% biến thiên của mức lương. Mặc dù hiệu suất chưa cao, mô hình đã xác định được các yếu tố quan trọng nhất ảnh hưởng đến mức lương trong lĩnh vực khoa học dữ liệu, bao gồm vị trí địa lý (US vs Non-US), mức độ kinh nghiệm, và loại công việc.
