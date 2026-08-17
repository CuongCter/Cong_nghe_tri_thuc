# Phân tích Dự báo Mức lương Ngành Khoa học Dữ liệu

## Mô tả

Dự án này thực hiện phân tích dự báo mức lương trong ngành khoa học dữ liệu bằng phương pháp hồi quy tuyến tính. Phân tích được thực hiện theo 4 yêu cầu chính:

1. **Phát biểu bài toán và tiền xử lý dữ liệu** (2 điểm)
2. **Mô tả phương pháp giải quyết bài toán** (2 điểm)
3. **Thực hiện các kỹ thuật phân tích dữ liệu** (3 điểm)
4. **Tổng hợp và phân tích kết quả** (3 điểm)

## Cấu trúc Files

```
├── data-salary.csv                    # Dữ liệu gốc
├── data_science_salary_analysis.py    # Code phân tích chính
├── salary_prediction_demo.py          # Demo chức năng dự báo
├── create_prediction_chart.py         # Tạo biểu đồ dự báo
├── requirements.txt                   # Thư viện cần thiết
├── bao_cao_phan_tich_luong.md        # Báo cáo chi tiết
├── images/                           # Folder chứa tất cả biểu đồ
│   ├── 01a_data_distribution.png     # Phân phối dữ liệu cơ bản
│   ├── 01b_data_analysis.png        # Phân tích chi tiết
│   ├── 02_model_results.png         # Kết quả mô hình
│   ├── 03_correlation_matrix.png     # Ma trận tương quan
│   ├── 04_salary_by_job.png          # Lương theo job title
│   ├── 05_experience_impact.png      # Tác động kinh nghiệm
│   ├── 06_company_size_salary.png    # Lương theo quy mô công ty
│   ├── 07_remote_impact.png          # Tác động remote work
│   ├── 08_residuals_analysis.png     # Phân tích residuals
│   ├── 09_feature_importance.png     # Tầm quan trọng features
│   ├── 10_salary_predictions.png     # Dự báo mức lương
│   └── README.md                     # Mô tả các biểu đồ
└── README.md                         # Hướng dẫn này
```

## Cài đặt và Chạy

### 1. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 2. Chạy phân tích

```bash
# Chạy phân tích đầy đủ (có thể mất thời gian)
python3 data_science_salary_analysis.py

# Hoặc chỉ demo chức năng dự báo
python3 salary_prediction_demo.py

# Hoặc tạo biểu đồ dự báo
python3 create_prediction_chart.py
```

## Tính năng chính

### Tiền xử lý dữ liệu

- ✅ Lọc job title chứa "data" và xuất hiện > 30 lần (14 loại)
- ✅ Xử lý outliers bằng phương pháp IQR
- ✅ Label Encoding cho biến categorical
- ✅ Chuẩn hóa dữ liệu: Z-Score Normalization
- ✅ Trích chọn thuộc tính bằng SelectKBest

### Phân tích dữ liệu

- ✅ So sánh US vs Non-US
- ✅ Phân tích xu hướng lương theo năm
- ✅ Biểu đồ khám phá dữ liệu đầy đủ
- ✅ Hồi quy tuyến tính với Z-Score Normalization

### Đánh giá mô hình

- ✅ R² Score, MSE, MAE
- ✅ Phân tích hệ số hồi quy
- ✅ Tầm quan trọng của features
- ✅ Phân tích residuals chi tiết

### Biểu đồ và Visualization

- ✅ 11 biểu đồ chất lượng cao (300 DPI)
- ✅ Font an toàn (DejaVu Sans) - không lỗi hiển thị
- ✅ Tự động lưu vào folder images/
- ✅ Correlation matrix, Q-Q plot, Feature importance
- ✅ Phân tích US vs Non-US, Remote work impact
- ✅ Biểu đồ dự báo cho các kịch bản khác nhau

### Chức năng Dự báo

- ✅ Dự báo mức lương cho trường hợp cụ thể
- ✅ Confidence interval (95%)
- ✅ So sánh nhiều kịch bản
- ✅ Phân tích tác động các yếu tố
- ✅ Giao diện dự báo tương tác

## Kết quả chính

- **Phương pháp**: Z-Score Normalization (duy nhất)
- **R² Score**: 0.2244 (22.4%)
- **MAE**: $37,641
- **Feature quan trọng nhất**: is_us (33.44%)

## Insights quan trọng

1. **Làm việc tại US** tăng lương trung bình $15,282 so với Non-US
2. **Kinh nghiệm** là yếu tố quan trọng thứ 2 (31.21% tầm quan trọng)
3. **Loại công việc** ảnh hưởng 25.18% đến mức lương
4. **Remote work** có xu hướng tăng lương nhẹ ($294/100% remote)
5. **Xu hướng tăng lương** khoảng $2,635 mỗi năm

## Ví dụ Dự báo

```python
# Dự báo cho Data Scientist Senior tại US
prediction = analyzer.predict_salary({
    'work_year': 2024,
    'experience_level': 'SE',
    'employment_type': 'FT',
    'job_title': 'Data Scientist',
    'remote_ratio': 100,
    'company_size': 'L',
    'company_location': 'US'
})

# Kết quả: ~$165,000 (±$74,000)
```

## Thống kê dữ liệu

- **Tổng mẫu ban đầu**: 16,534
- **Mẫu sau xử lý**: 10,473
- **Job titles phân tích**: 14 loại công việc chứa từ "Data" (> 30 lần xuất hiện)
- **Tỷ lệ train/test**: 80%/20%

## Hạn chế và Khuyến nghị

### Hạn chế

- R² thấp (22.4%) - nhiều yếu tố chưa được giải thích
- Sai số khá lớn ($37,641 MAE)
- Giả định tuyến tính có thể không phù hợp hoàn toàn

### Khuyến nghị cải thiện

1. Thu thập thêm features (kỹ năng, chứng chỉ, kinh nghiệm cụ thể)
2. Thử các mô hình phức tạp hơn (Random Forest, XGBoost)
3. Xử lý tốt hơn các biến categorical
4. Phân tích tương tác giữa các features
5. Cập nhật mô hình định kỳ với dữ liệu mới


