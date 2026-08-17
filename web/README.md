# 📊 Data Science Salary Analysis Dashboard

Một website đẹp và chuyên nghiệp để hiển thị phân tích mức lương ngành Data Science với khả năng dự đoán lương sử dụng Machine Learning.

## ✨ Tính năng

### 🎯 **Dashboard Chính**
- **Hero Section**: Thống kê tổng quan với animation đẹp mắt
- **Tổng quan Dự án**: Giới thiệu methodology và kết quả
- **11 Biểu đồ Chuyên nghiệp**: Hiển thị trong tabs có tổ chức
- **Responsive Design**: Tối ưu cho mọi thiết bị

### 🔮 **Dự đoán Lương**
- **Form tương tác**: 7 parameters để dự đoán
- **14 Job Titles**: Chỉ những ngành đã được phân tích
- **Real-time Prediction**: Kết quả tức thì với confidence interval
- **Machine Learning**: Sử dụng mô hình đã train hoặc fallback coefficients

### 📈 **Key Insights**
- **4 Insights chính**: US Premium, Experience Gap, Growth Trend, Location Factor
- **Khuyến nghị Nghề nghiệp**: Hướng dẫn tăng lương và xu hướng tương lai
- **Interactive Cards**: Hover effects và animations

## 🚀 Cách chạy

### 1. Cài đặt Dependencies
```bash
cd web
pip install -r requirements.txt
```

### 2. Chạy Flask Server
```bash
python app.py
```

### 3. Truy cập Website
Mở trình duyệt và vào: `http://localhost:5000`

## 🏗️ Cấu trúc Project

```
web/
├── index.html              # Trang chính
├── css/
│   └── style.css          # Styling chuyên nghiệp
├── js/
│   └── script.js          # JavaScript tương tác
├── app.py                 # Flask API backend
├── requirements.txt       # Python dependencies
└── README.md             # Tài liệu này
```

## 🎨 Design Features

### **UI/UX Highlights**
- **Modern Gradient**: Hero section với gradient đẹp mắt
- **Glass Morphism**: Cards với backdrop-filter và transparency
- **Smooth Animations**: Fade-in, slide-up effects
- **Interactive Elements**: Hover states, loading animations
- **Professional Typography**: Inter font family

### **Color Scheme**
- **Primary**: `#667eea` → `#764ba2` (Gradient)
- **Secondary**: `#f093fb` → `#f5576c` (Prediction section)
- **Accent**: `#ffc107` (Warning/Highlight)
- **Text**: `#333` (Dark), `rgba(255,255,255,0.8)` (Light)

### **Components**
- **Stat Cards**: Glass morphism với icons
- **Feature Cards**: Shadow effects với hover animations
- **Chart Cards**: Clean layout với modal view
- **Prediction Form**: Glass morphism với real-time updates
- **Insight Cards**: Border-left accent với numbers

## 🔧 Technical Details

### **Frontend**
- **HTML5**: Semantic markup
- **CSS3**: Flexbox, Grid, Custom Properties
- **JavaScript ES6+**: Modules, Async/Await
- **Bootstrap 5.3**: Responsive grid và components
- **Font Awesome 6.4**: Professional icons

### **Backend**
- **Flask 2.3.3**: Lightweight Python web framework
- **Flask-CORS**: Cross-origin resource sharing
- **NumPy**: Numerical computations
- **Integration**: Với module `data_science_salary_analysis.py`

### **Machine Learning**
- **Model**: Linear Regression với Z-Score Normalization
- **Features**: 7 features quan trọng
- **Accuracy**: R² = 0.2244, MAE = $37,641
- **Fallback**: Hardcoded coefficients nếu model không load được

## 📊 API Endpoints

### `POST /api/predict`
Dự đoán mức lương
```json
{
  "work_year": 2024,
  "experience_level": "SE",
  "employment_type": "FT",
  "job_title": "Data Scientist",
  "remote_ratio": 50,
  "company_size": "M",
  "company_location": "US"
}
```

### `GET /api/stats`
Thống kê dataset

### `GET /api/job-titles`
Danh sách 14 job titles

### `GET /api/health`
Health check

## 🎯 Job Titles Supported

1. Data Engineer
2. Data Scientist
3. Data Analyst
4. Data Architect
5. Data Science
6. Data Manager
7. Data Science Manager
8. Data Specialist
9. Data Science Consultant
10. Data Analytics Manager
11. Head of Data
12. Data Modeler
13. Data Product Manager
14. Director of Data Science

## 🌟 Screenshots

### Hero Section
- Gradient background với stats cards
- Call-to-action buttons
- Responsive design

### Charts Section
- Tabbed interface
- 11 biểu đồ chất lượng cao
- Modal view cho chi tiết

### Prediction Section
- Interactive form
- Real-time results
- Confidence intervals

### Insights Section
- Key metrics cards
- Career recommendations
- Future trends

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production
- Sử dụng Gunicorn hoặc uWSGI
- Nginx reverse proxy
- SSL certificate
- Environment variables

## 📝 Notes

- Website tự động fallback nếu không load được trained model
- Tất cả predictions đều có confidence intervals
- Responsive design cho mobile và tablet
- SEO-friendly với semantic HTML
- Accessibility features (ARIA labels, keyboard navigation)

## 🎉 Kết quả

Một website hoàn chỉnh, chuyên nghiệp với:
- ✅ UI/UX đẹp mắt và hiện đại
- ✅ 11 biểu đồ chất lượng cao
- ✅ Dự đoán lương real-time
- ✅ Responsive design
- ✅ Professional animations
- ✅ Clean code structure
