import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.feature_selection import SelectKBest, f_regression

from salary_visualization import SalaryVisualization
from salary_prediction import SalaryPrediction

class DataScienceSalaryAnalysis:
    @staticmethod
    def format_currency(amount):
        """Format số tiền với dấu phẩy và ký hiệu USD"""
        return f"${amount:,.2f}"

    @staticmethod
    def format_number(number):
        """Format số với dấu phẩy"""
        return f"{number:,.2f}"

    @staticmethod
    def print_header(title, width=80):
        """In header đẹp với viền"""
        print("\n" + "=" * width)
        print(f"{title:^{width}}")
        print("=" * width)

    @staticmethod
    def print_section(title, width=50):
        """In section header"""
        print(f"\n{title}")
        print("-" * width)

    @staticmethod
    def print_metrics_table(metrics_dict, title="MODEL PERFORMANCE METRICS"):
        """In bảng metrics đẹp"""
        print(f"\n{title}")
        print("-" * 60)
        print(f"{'Metric':<20} {'Train':<15} {'Test':<15}")
        print("-" * 60)

        for metric_name, values in metrics_dict.items():
            if isinstance(values, dict) and 'train' in values and 'test' in values:
                train_val = values['train']
                test_val = values['test']
                if 'R²' in metric_name:
                    print(f"{metric_name:<20} {train_val:<15.4f} {test_val:<15.4f}")
                else:
                    print(f"{metric_name:<20} {DataScienceSalaryAnalysis.format_number(train_val):<15} {DataScienceSalaryAnalysis.format_number(test_val):<15}")
        print("-" * 60)
        
    def __init__(self, data_path):
        """
        Khởi tạo với đường dẫn dữ liệu
        
        Args:
            data_path (str): Đường dẫn đến file dữ liệu
            df (DataFrame): Dữ liệu gốc
            df_processed (DataFrame): Dữ liệu đã xử lý
            scaler (StandardScaler): Đối tượng chuẩn hóa dữ liệu
            label_encoders (dict): Dictionary chứa các LabelEncoder cho các cột categorical
            model (LinearRegression): Đối tượng mô hình hồi quy tuyến tính
            X_train, X_test, y_train, y_test (DataFrame/Series): Dữ liệu huấn luyện và kiểm tra
        """
        self.data_path = data_path 
        self.df = None 
        self.df_processed = None 
        self.scaler = None 
        self.label_encoders = {}
        self.model = None 
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
    def load_data(self):
        self.df = pd.read_csv(self.data_path)
        print(f"\n2. THÔNG TIN CƠ BẢN VỀ DỮ LIỆU:")
        print("-" * 30)
        print(f"Kích thước dữ liệu: {self.df.shape}")
        print(f"Số dòng: {self.df.shape[0]}")
        print(f"Số cột: {self.df.shape[1]}")
        
        return self.df
    
    def explore_data(self):
        """
        Khám phá và tóm lược dữ liệu
        """
        print("\n3. TÓM LƯỢC DỮ LIỆU:")
        print("-" * 30)
        
        # Hiển thị thông tin cơ bản
        print("Thông tin các cột:")
        print(self.df.info())
        
        print("\nThống kê mô tả:")
        print(self.df.describe())
        
        print("\nKiểm tra giá trị thiếu:")
        missing_values = self.df.isnull().sum()
        print(missing_values[missing_values > 0])
        if missing_values.sum() == 0:
            print("Không có giá trị thiếu trong dữ liệu")
        
        # Phân tích các job title chứa từ "data"
        print("\n4. PHÂN TÍCH JOB TITLE CHỨA TỪ 'DATA':")
        print("-" * 30)
        data_jobs = self.df[self.df['job_title'].str.contains('Data', case=False, na=False)]
        job_counts = data_jobs['job_title'].value_counts()

        print("Top 20 job title chứa 'Data':")
        print(job_counts.head(20))

        # Lọc các job xuất hiện > 30 lần
        frequent_jobs = job_counts[job_counts > 30]
        print(f"\nCác job xuất hiện > 30 lần ({len(frequent_jobs)} loại):")
        print(frequent_jobs)
        
        return data_jobs, frequent_jobs
    
    def clean_data(self):
        print("\n6. LÀM SẠCH DỮ LIỆU:")
        print("-" * 30)

        # Tạo bản sao để xử lý
        self.df_processed = self.df.copy()

        # Lọc các job chứa từ "data" và xuất hiện > 30 lần
        data_jobs = self.df_processed[self.df_processed['job_title'].str.contains('Data', case=False, na=False)]
        job_counts = data_jobs['job_title'].value_counts()
        frequent_jobs = job_counts[job_counts > 30].index.tolist()

        print(f"Các job chứa 'Data' xuất hiện > 30 lần: {frequent_jobs}")

        # Lọc dữ liệu chỉ giữ lại các job frequent
        self.df_processed = self.df_processed[
            self.df_processed['job_title'].isin(frequent_jobs)
        ]

        print(f"Kích thước dữ liệu sau khi lọc job titles: {self.df_processed.shape}")

        # Min, Max, Median, Std, Mean
        print(f"Min = {self.df_processed['salary_in_usd'].min():.0f}")
        print(f"Max = {self.df_processed['salary_in_usd'].max():.0f}")
        print(f"Median = {self.df_processed['salary_in_usd'].median():.0f}")
        print(f"Mean = {self.df_processed['salary_in_usd'].mean():.0f}")
        print(f"Std = {self.df_processed['salary_in_usd'].std():.0f}")

        # Loại bỏ các outliers (sử dụng IQR method)
        Q1 = self.df_processed['salary_in_usd'].quantile(0.25)
        Q3 = self.df_processed['salary_in_usd'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        print(f"Giới hạn outliers: [{lower_bound:.0f}, {upper_bound:.0f}]")

        # Loại bỏ outliers
        outliers_count = len(self.df_processed[
            (self.df_processed['salary_in_usd'] < lower_bound) |
            (self.df_processed['salary_in_usd'] > upper_bound)
        ])

        self.df_processed = self.df_processed[
            (self.df_processed['salary_in_usd'] >= lower_bound) &
            (self.df_processed['salary_in_usd'] <= upper_bound)
        ]

        print(f"Đã loại bỏ {outliers_count} outliers")
        print(f"Kích thước dữ liệu cuối cùng: {self.df_processed.shape}")

        # Thêm cột phân loại US vs Non-US
        self.df_processed['is_us'] = (self.df_processed['company_location'] == 'US').astype(int)

        # Tạo các cột encoded tạm thời để sử dụng trong visualization
        categorical_columns = ['experience_level', 'employment_type', 'job_title', 'company_size']

        for col in categorical_columns:
            le = LabelEncoder()
            self.df_processed[col + '_encoded'] = le.fit_transform(self.df_processed[col])

        return self.df_processed

    def preprocess_data(self):
        """
        Tiền xử lý dữ liệu: Encoding, Normalization, Feature Selection
        """
        print("\n7. TIỀN XỬ LÝ DỮ LIỆU:")
        print("-" * 30)

        # Làm sạch dữ liệu
        self.clean_data()

        # Tạo bản sao để xử lý
        df_prep = self.df_processed.copy()

        # 1. Label Encoding cho các biến categorical
        categorical_columns = ['experience_level', 'employment_type', 'job_title', 'company_size']

        print("Thực hiện Label Encoding cho các biến categorical:")
        for col in categorical_columns:
            le = LabelEncoder()
            df_prep[col + '_encoded'] = le.fit_transform(df_prep[col])
            self.label_encoders[col] = le
            print(f"- {col}: {len(le.classes_)} categories")

        # 2. Chọn features cho mô hình
        feature_columns = [
            'work_year', 'experience_level_encoded', 'employment_type_encoded',
            'job_title_encoded', 'remote_ratio', 'company_size_encoded', 'is_us'
        ]

        X = df_prep[feature_columns]
        y = df_prep['salary_in_usd']

        print(f"\nSố lượng features: {len(feature_columns)}")
        print(f"Features: {feature_columns}")

        # 3. Chia dữ liệu train/test
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        print(f"\nKích thước tập train: {self.X_train.shape}")
        print(f"Kích thước tập test: {self.X_test.shape}")

        # 4. Bỏ qua chuẩn hóa ở đây - sẽ chuẩn hóa sau khi feature selection
        print("\n8. CHUẨN HÓA DỮ LIỆU:")
        print("-" * 30)
        print("Sẽ thực hiện chuẩn hóa sau khi feature selection để đảm bảo consistency")

        # 5. Feature Selection
        print("\n9. TRÍCH CHỌN THUỘC TÍNH:")
        print("-" * 30)

        # Sử dụng SelectKBest với f_regression
        selector = SelectKBest(score_func=f_regression, k=5)  # Chọn 5 features tốt nhất
        X_train_selected = selector.fit_transform(self.X_train, self.y_train)
        X_test_selected = selector.transform(self.X_test)

        # Lấy tên các features được chọn
        selected_features = [feature_columns[i] for i in selector.get_support(indices=True)]
        feature_scores = selector.scores_[selector.get_support()]

        print("Top 5 features được chọn:")
        for feature, score in zip(selected_features, feature_scores):
            print(f"- {feature}: {score:.2f}")

        self.selected_features = selected_features
        self.feature_selector = selector

        # Lưu dữ liệu đã được feature selection để sử dụng trong training
        self.X_train_selected = X_train_selected
        self.X_test_selected = X_test_selected

        return {
            'X_train_selected': self.X_train_selected,
            'X_test_selected': self.X_test_selected,
            'selected_features': self.selected_features,
            'feature_selector': self.feature_selector
        }

    def train_models(self):
        print("\n1. HUẤN LUYỆN MÔ HÌNH HỒI QUY TUYẾN TÍNH:")
        print("-" * 40)
        print("Sử dụng Z-Score Normalization với 5 features được chọn")

        # Tạo scaler mới cho 5 features được chọn
        self.scaler = StandardScaler()
        X_train_selected_normalized = self.scaler.fit_transform(self.X_train_selected)
        X_test_selected_normalized = self.scaler.transform(self.X_test_selected)

        print(f"Đã chuẩn hóa {self.X_train_selected.shape[1]} features được chọn")

        # Tạo và huấn luyện mô hình với 5 features được chọn
        self.model = LinearRegression()
        self.model.fit(X_train_selected_normalized, self.y_train)

        # Dự đoán
        self.y_train_pred = self.model.predict(X_train_selected_normalized)
        self.y_test_pred = self.model.predict(X_test_selected_normalized)

        # Lưu dữ liệu normalized để sử dụng sau này
        self.X_train_selected_normalized = X_train_selected_normalized
        self.X_test_selected_normalized = X_test_selected_normalized

        # Tính các metrics (R², MSE, RMSE, MAE)
        self.train_r2 = r2_score(self.y_train, self.y_train_pred)
        self.test_r2 = r2_score(self.y_test, self.y_test_pred)
        self.train_mse = mean_squared_error(self.y_train, self.y_train_pred)
        self.test_mse = mean_squared_error(self.y_test, self.y_test_pred)
        self.train_mae = mean_absolute_error(self.y_train, self.y_train_pred)
        self.test_mae = mean_absolute_error(self.y_test, self.y_test_pred)
        self.train_rmse = np.sqrt(self.train_mse)
        self.test_rmse = np.sqrt(self.test_mse)

        # Hiển thị kết quả với format đẹp
        metrics = {
            'R² Score': {'train': self.train_r2, 'test': self.test_r2},
            'MSE': {'train': self.train_mse, 'test': self.test_mse},
            'RMSE': {'train': self.train_rmse, 'test': self.test_rmse},
            'MAE': {'train': self.train_mae, 'test': self.test_mae}
        }

        self.print_metrics_table(metrics, "KẾT QUẢ MÔ HÌNH Z-SCORE NORMALIZATION")

        # Lưu kết quả để tương thích với code cũ
        self.model_results = {
            'zscore': {
                'model': self.model,
                'train_r2': self.train_r2,
                'test_r2': self.test_r2,
                'train_mse': self.train_mse,
                'test_mse': self.test_mse,
                'train_rmse': self.train_rmse,
                'test_rmse': self.test_rmse,
                'train_mae': self.train_mae,
                'test_mae': self.test_mae,
                'y_train_pred': self.y_train_pred,
                'y_test_pred': self.y_test_pred
            }
        }

        self.best_method = 'zscore'
        self.best_model = self.model

        return self.model_results

    def analyze_results(self):
        """
        Phân tích chi tiết kết quả mô hình
        """
        self.print_section("2. PHÂN TÍCH CHI TIẾT MÔ HÌNH", 50)

        # Hiển thị hệ số hồi quy
        print(f"Phương pháp chuẩn hóa: Z-Score Normalization")
        print(f"Intercept (β₀): {self.format_currency(self.model.intercept_)}")

        print(f"\n{'HỆ SỐ HỒI QUY (βᵢ) - 5 FEATURES ĐƯỢC CHỌN'}")
        print("-" * 50)
        # Sử dụng tên features đã được chọn
        selected_feature_names = self.selected_features
        for i, (feature, coef) in enumerate(zip(selected_feature_names, self.model.coef_)):
            print(f"  {feature:<25}: {self.format_number(coef)}")

        # Phân tích tầm quan trọng của features
        feature_importance = abs(self.model.coef_)
        feature_importance_normalized = feature_importance / feature_importance.sum() * 100

        print(f"\n{'TẦM QUAN TRỌNG CỦA 5 FEATURES ĐƯỢC CHỌN'}")
        print("-" * 50)
        # Sắp xếp theo tầm quan trọng
        importance_data = list(zip(selected_feature_names, feature_importance_normalized))
        importance_data.sort(key=lambda x: x[1], reverse=True)

        for feature, importance in importance_data:
            bar_length = int(importance / 5)  # Scale for visualization
            bar = "█" * bar_length
            print(f"  {feature:<25}: {importance:>6.2f}% {bar}")

        # Thêm phần đánh giá mô hình
        self.print_model_evaluation()

    def print_model_evaluation(self):
        """
        In phần đánh giá và giải thích kết quả mô hình
        """
        print(f"\n{'ĐÁNH GIÁ MÔ HÌNH'}")
        print("-" * 40)

        # Đánh giá R²
        if self.test_r2 >= 0.7:
            r2_assessment = "Tốt - Mô hình giải thích được phần lớn biến thiên"
        elif self.test_r2 >= 0.5:
            r2_assessment = "Khá - Mô hình có khả năng dự đoán chấp nhận được"
        elif self.test_r2 >= 0.3:
            r2_assessment = "Trung bình - Mô hình có một số khả năng dự đoán"
        else:
            r2_assessment = "Yếu - Mô hình cần cải thiện đáng kể"

        print(f"• R² Score ({self.test_r2:.4f}): {r2_assessment}")
        print(f"• Mô hình giải thích được {self.test_r2*100:.1f}% biến thiên của mức lương")

        # Đánh giá RMSE
        avg_salary = np.mean(self.y_test)
        rmse_percentage = (self.test_rmse / avg_salary) * 100
        print(f"• RMSE: {self.format_currency(self.test_rmse)} ({rmse_percentage:.1f}% của mức lương trung bình)")

    def run_all_analysis(self):
        # Bước 1: Khám phá dữ liệu
        self.load_data()
        self.explore_data()

        # Bước 2: Làm sạch và chuẩn hóa dữ liệu Tiền xử lý dữ liệu
        self.clean_data()
        self.preprocess_data()

        # Bước 3: Huấn luyện và phân tích mô hình
        self.train_models()
        self.analyze_results()

        self.print_final_dashboard()

        # Bước 5: Dự báo cho các kịch bản
        # predictor = SalaryPrediction()

        # input_data = {
        #     'work_year': 2024,
        #     'experience_level': 'MI',
        #     'employment_type': 'FT',
        #     'job_title': 'Data Engineer',
        #     'is_usa': 1  # 1 = US, 0 = Non-US
        # }
        # predictor.predict_salary(
        #     input_data,
        #     self.model,
        #     self.scaler,
        #     self.label_encoders,
        #     self.selected_features,
        #     self.feature_selector,
        #     self.test_mae
        # )

        # predictor.visualize_predictions(
        #     self.model,
        #     self.scaler,
        #     self.label_encoders,
        #     self.selected_features,
        #     self.feature_selector,
        #     self.test_mae
        # )

        # Bước 6: Vẽ biểu đồ
        # SalaryVisualization(self).draw_visualize()

        # Return kết quả cuối cùng
        return self

    def print_final_dashboard(self):
        """
        In dashboard tổng kết cuối cùng
        """
        self.print_header("📊 DASHBOARD TỔNG KẾT KẾT QUẢ PHÂN TÍCH", 80)

        # Thông tin dữ liệu
        print(f"\n{'📋 THÔNG TIN DỮ LIỆU'}")
        print("-" * 50)
        print(f"• Tổng số mẫu ban đầu: {len(self.df):,}")
        print(f"• Số mẫu sau xử lý: {len(self.df_processed):,}")
        print(f"• Số loại công việc: {len(self.df_processed['job_title'].unique())}")
        print(f"• Khoảng lương: {self.format_currency(self.df_processed['salary_in_usd'].min())} - {self.format_currency(self.df_processed['salary_in_usd'].max())}")

        # Hiệu suất mô hình
        print(f"\n{'🎯 HIỆU SUẤT MÔ HÌNH'}")
        print("-" * 50)
        print(f"• Độ chính xác (R²): {self.test_r2:.1%}")
        print(f"• Sai số trung bình (MAE): {self.format_currency(self.test_mae)}")
        print(f"• Sai số bình phương trung bình (MSE): {self.format_currency(self.test_mse)}")
        print(f"• Sai số bình phương gốc (RMSE): {self.format_currency(self.test_rmse)}")

        # Top features quan trọng (từ 5 features đã được chọn)
        selected_feature_names = self.selected_features
        feature_importance = abs(self.model.coef_)
        feature_importance_normalized = feature_importance / feature_importance.sum() * 100
        importance_data = list(zip(selected_feature_names, feature_importance_normalized))
        importance_data.sort(key=lambda x: x[1], reverse=True)

        print(f"\n{'🔍 TOP 5 YẾU TỐ QUAN TRỌNG NHẤT (ĐÃ ĐƯỢC CHỌN)'}")
        print("-" * 50)
        for i, (feature, importance) in enumerate(importance_data, 1):
            print(f"{i}. {feature}: {importance:.1f}%")

        self.print_header("🎉 HOÀN THÀNH PHÂN TÍCH!", 80)

def main():
    # Đường dẫn đến file dữ liệu
    data_path = "data-salary.csv"

    try:
        analyzer = DataScienceSalaryAnalysis(data_path)
        analyzer.run_all_analysis()

    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {data_path}")
        print("Vui lòng kiểm tra đường dẫn file dữ liệu")
    except Exception as e:
        print(f"Lỗi trong quá trình phân tích: {str(e)}")


if __name__ == "__main__":
    main()
