import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Thiết lập font hỗ trợ tiếng Việt và style cho biểu đồ
import matplotlib.font_manager as fm

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.unicode_minus'] = False

# Thêm cấu hình để hỗ trợ tiếng Việt tốt hơn
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.formatter.use_locale'] = True

# Sử dụng style an toàn hơn
plt.style.use('default')
sns.set_style("whitegrid")
sns.set_palette("husl")

class SalaryVisualization:
    def __init__(self, data_processor=None):
        """
        Khởi tạo với data processor
        
        Args:
            data_processor: Instance của DataScienceSalaryAnalysis
        """
        self.data_processor = data_processor
        
    def format_currency(self, x, pos):
        """Hàm format số ngắn gọn"""
        if x >= 1e6:
            return f'${x/1e6:.1f}M'
        elif x >= 1e3:
            return f'${x/1e3:.0f}K'
        else:
            return f'${x:.0f}'

    def visualize_data(self, data):
        """
        Vẽ biểu đồ khám phá dữ liệu cơ bản
        
        Args:
            data: DataFrame chứa dữ liệu đã xử lý
        """
        print("\n5. BIỂU ĐỒ KHÁM PHÁ DỮ LIỆU (DỮ LIỆU ĐÃ XỬ LÝ):")
        print("-" * 30)
        print(f"✅ Sử dụng dữ liệu đã xử lý: {data.shape[0]} records")

        # PHẦN 1: Phân phối và so sánh cơ bản (3 biểu đồ)
        fig1, axes1 = plt.subplots(1, 3, figsize=(18, 6))
        fig1.suptitle('Data Science Salary Analysis - Phần 1: Phân phối dữ liệu', fontsize=16, fontweight='bold')

        # 1. Histogram của salary
        axes1[0].hist(data['salary_in_usd'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        axes1[0].set_title('Phân phối mức lương')
        axes1[0].set_xlabel('Mức lương (USD)')
        axes1[0].set_ylabel('Tần suất')
        axes1[0].grid(True, alpha=0.3)
        axes1[0].xaxis.set_major_formatter(plt.FuncFormatter(self.format_currency))

        # 2. Box plot salary theo experience level
        sns.boxplot(data=data, x='experience_level', y='salary_in_usd', ax=axes1[1])
        axes1[1].set_title('Mức lương theo Experience Level')
        axes1[1].set_xlabel('Experience Level')
        axes1[1].set_ylabel('Mức lương (USD)')
        axes1[1].yaxis.set_major_formatter(plt.FuncFormatter(self.format_currency))

        # 3. Box plot salary theo company size
        sns.boxplot(data=data, x='company_size', y='salary_in_usd', ax=axes1[2])
        axes1[2].set_title('Mức lương theo Company Size')
        axes1[2].set_xlabel('Company Size')
        axes1[2].set_ylabel('Mức lương (USD)')
        axes1[2].yaxis.set_major_formatter(plt.FuncFormatter(self.format_currency))

        plt.tight_layout()
        plt.savefig('images/01_data_distribution.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        print("Đã lưu: images/01_data_distribution.png")
        plt.close()

        # PHẦN 2: Phân tích chi tiết (3 biểu đồ)
        fig2, axes2 = plt.subplots(1, 3, figsize=(18, 6))
        fig2.suptitle('Data Science Salary Analysis - Phần 2: Phân tích chi tiết', fontsize=16, fontweight='bold')

        # 4. US vs Non-US salary comparison (thay thế job title chart)
        us_comparison = data.groupby('is_us')['salary_in_usd'].agg(['mean', 'median', 'count'])
        us_comparison.index = ['Non-US', 'US']

        x_pos = np.arange(len(us_comparison))
        width = 0.35

        bars1 = axes2[0].bar(x_pos - width/2, us_comparison['mean'], width,
                           label='Mean', color='skyblue', alpha=0.8)
        bars2 = axes2[0].bar(x_pos + width/2, us_comparison['median'], width,
                           label='Median', color='lightcoral', alpha=0.8)

        axes2[0].set_title('So sánh lương US vs Non-US')
        axes2[0].set_xlabel('Khu vực')
        axes2[0].set_ylabel('Mức lương (USD)')
        axes2[0].set_xticks(x_pos)
        axes2[0].set_xticklabels(us_comparison.index)
        axes2[0].legend()
        axes2[0].yaxis.set_major_formatter(plt.FuncFormatter(self.format_currency))

        # Thêm giá trị lên các cột
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                axes2[0].text(bar.get_x() + bar.get_width()/2., height + 1000,
                            f'${height/1000:.0f}K', ha='center', va='bottom', fontsize=9)

        # 5. Salary trend theo năm
        yearly_salary = data.groupby('work_year')['salary_in_usd'].mean()
        axes2[1].plot(yearly_salary.index, yearly_salary.values, marker='o', linewidth=3, markersize=10, color='green')
        axes2[1].set_title('Xu hướng lương theo năm')
        axes2[1].set_xlabel('Năm')
        axes2[1].set_ylabel('Lương trung bình (USD)')
        axes2[1].grid(True, alpha=0.3)
        axes2[1].yaxis.set_major_formatter(plt.FuncFormatter(self.format_currency))

        # Cải thiện hiển thị trục x
        axes2[1].set_xticks(yearly_salary.index)
        axes2[1].set_xticklabels([str(int(year)) for year in yearly_salary.index], fontsize=10)

        # Thêm giá trị lên các điểm
        for year, salary in yearly_salary.items():
            axes2[1].text(year, salary + 3000, f'${salary/1000:.0f}K',
                         ha='center', va='bottom', fontsize=10, fontweight='bold')

        # 6. US vs Non-US salary comparison
        if 'is_us' not in data.columns:
            data = data.copy()
            data['is_us'] = data['company_location'] == 'US'
        us_comparison = data.groupby('is_us')['salary_in_usd'].mean()
        us_comparison.index = ['Non-US', 'US']

        bars = axes2[2].bar(us_comparison.index, us_comparison.values, color=['orange', 'lightblue'], alpha=0.8)
        axes2[2].set_title('So sánh lương: US vs Non-US')
        axes2[2].set_xlabel('Khu vực')
        axes2[2].set_ylabel('Lương trung bình (USD)')
        axes2[2].yaxis.set_major_formatter(plt.FuncFormatter(self.format_currency))

        # Thêm giá trị lên các cột
        for bar, value in zip(bars, us_comparison.values):
            axes2[2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3000,
                         f'${value/1000:.0f}K', ha='center', va='bottom', fontsize=11, fontweight='bold')

        # Thêm chênh lệch
        diff = us_comparison['US'] - us_comparison['Non-US']
        pct = (diff / us_comparison['Non-US']) * 100
        axes2[2].text(0.5, max(us_comparison.values) * 0.7,
                     f'Chênh lệch: ${diff/1000:.0f}K\n({pct:.1f}% cao hơn)',
                     ha='center', va='center', fontsize=10,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

        plt.tight_layout()
        plt.savefig('images/02_data_analysis.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        print("Đã lưu: images/02_data_analysis.png")
        plt.close()

        # In thống kê so sánh US vs Non-US
        print("\nSo sánh mức lương US vs Non-US:")
        us_stats = data.groupby('is_us')['salary_in_usd'].agg(['count', 'mean', 'median', 'std'])
        us_stats.index = ['Non-US', 'US']
        print(us_stats)

    def visualize_results(self, model_results, best_method, y_test, y_test_pred, X_train_selected, model, df_processed, scaler):
        """
        Trực quan hóa kết quả mô hình (cập nhật cho 5 features)

        Args:
            model_results: Dictionary chứa kết quả các mô hình
            best_method: Phương pháp tốt nhất
            y_test: Giá trị thực tế test set
            y_test_pred: Giá trị dự đoán test set
            X_train_selected: 5 features được chọn (training set)
            model: Mô hình đã train
            df_processed: Dữ liệu đã xử lý
            scaler: Scaler đã fit
        """
        print("\n3. TRỰC QUAN HÓA KẾT QUẢ:")
        print("-" * 40)

        best_result = model_results[best_method]
        test_r2 = best_result['test_r2']

        # Tạo figure với nhiều subplot
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Linear Regression Model Analysis Results', fontsize=16, fontweight='bold')

        # 1. Hiển thị R² Score của mô hình
        bars = axes[0, 0].bar(['Z-Score Normalization'], [test_r2], color='skyblue')
        axes[0, 0].set_title('R² Score của mô hình')
        axes[0, 0].set_xlabel('Phương pháp chuẩn hóa')
        axes[0, 0].set_ylabel('Test R² Score')
        axes[0, 0].set_ylim(0, max(0.5, test_r2 + 0.1))

        # Thêm giá trị lên cột
        axes[0, 0].text(0, test_r2 + 0.01, f'{test_r2:.3f}',
                       ha='center', va='bottom', fontweight='bold')

        # 2. Actual vs Predicted (Test set)
        axes[0, 1].scatter(y_test, y_test_pred, alpha=0.6, color='blue')
        axes[0, 1].plot([y_test.min(), y_test.max()],
                       [y_test.min(), y_test.max()], 'r--', lw=2)
        axes[0, 1].set_title('Actual vs Predicted (Test Set)')
        axes[0, 1].set_xlabel('Actual Salary (USD)')
        axes[0, 1].set_ylabel('Predicted Salary (USD)')

        # 3. Residuals plot
        residuals = y_test - y_test_pred
        axes[0, 2].scatter(y_test_pred, residuals, alpha=0.6, color='green')
        axes[0, 2].axhline(y=0, color='r', linestyle='--')
        axes[0, 2].set_title('Residuals Plot')
        axes[0, 2].set_xlabel('Predicted Salary (USD)')
        axes[0, 2].set_ylabel('Residuals')

        # 4. Model Performance Summary
        # Hiển thị metrics summary thay vì feature importance (sẽ có chart riêng)
        metrics_text = f"""Model Performance:
R² Score: {model_results[best_method]['test_r2']:.4f}
RMSE: ${np.sqrt(model_results[best_method]['test_mse']):,.0f}
MAE: ${model_results[best_method]['test_mae']:,.0f}

Features: 5 selected from 7 original
Method: {best_method.upper()} Normalization"""

        axes[1, 0].text(0.1, 0.5, metrics_text, transform=axes[1, 0].transAxes,
                       fontsize=11, verticalalignment='center',
                       bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        axes[1, 0].set_title('Model Summary')
        axes[1, 0].axis('off')

        # 5. Distribution of residuals
        axes[1, 1].hist(residuals, bins=30, alpha=0.7, color='purple', edgecolor='black')
        axes[1, 1].set_title('Phân phối Residuals')
        axes[1, 1].set_xlabel('Residuals')
        axes[1, 1].set_ylabel('Tần suất')

        # 6. US vs Non-US salary comparison với predictions
        us_actual = df_processed.groupby('is_us')['salary_in_usd'].mean()

        # Simplified US vs Non-US comparison (chỉ actual data để tránh lỗi scaler)
        us_count = df_processed.groupby('is_us')['salary_in_usd'].count()

        x_pos = np.arange(2)
        bars = axes[1, 2].bar(x_pos, [us_actual[0], us_actual[1]],
                             color=['lightcoral', 'skyblue'], alpha=0.8)

        axes[1, 2].set_title('US vs Non-US: Average Salary')
        axes[1, 2].set_xlabel('Khu vực')
        axes[1, 2].set_ylabel('Mức lương trung bình (USD)')
        axes[1, 2].set_xticks(x_pos)
        axes[1, 2].set_xticklabels(['Non-US', 'US'])
        axes[1, 2].yaxis.set_major_formatter(plt.FuncFormatter(self.format_currency))

        # Thêm giá trị và count lên các cột
        for i, (bar, salary, count) in enumerate(zip(bars, [us_actual[0], us_actual[1]], [us_count[0], us_count[1]])):
            axes[1, 2].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2000,
                           f'${salary/1000:.0f}K\n({count:,} jobs)',
                           ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        # Lưu ảnh với nền trắng
        plt.savefig('images/03_model_results.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        print("Đã lưu biểu đồ kết quả mô hình: images/03_model_results.png")
        plt.close()  # Đóng figure để giải phóng bộ nhớ

    def visualize_matrix(self, df_processed):
        # 1. Correlation Matrix (bao gồm cả salary_in_usd)
        print("Tạo correlation matrix với salary_in_usd...")
        plt.figure(figsize=(14, 12))

        # Thêm salary_in_usd vào 5 features được chọn
        numeric_cols = self.data_processor.selected_features + ['salary_in_usd']

        # Đảm bảo tất cả columns tồn tại
        available_cols = [col for col in numeric_cols if col in df_processed.columns]

        corr_data = df_processed[available_cols]
        correlation_matrix = corr_data.corr()

        # Tạo mask để chỉ hiển thị nửa dưới của ma trận
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))

        # Tạo heatmap
        sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='RdYlBu_r',
                   center=0, square=True, linewidths=0.5, fmt='.3f',
                   cbar_kws={"shrink": .8})

        plt.title('Ma trận tương quan: 5 Features + Salary\n(Giá trị càng gần ±1 = tương quan càng mạnh)',
                 fontsize=16, fontweight='bold', pad=20)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)

        # Thêm chú thích
        plt.figtext(0.02, 0.02,
                   'Đỏ: Tương quan âm | Xanh: Tương quan dương | Trắng: Không tương quan',
                   fontsize=10, style='italic')

        plt.tight_layout()
        plt.savefig('images/05_correlation_matrix.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        print("Đã lưu: images/05_correlation_matrix.png")

        # In ra correlation với salary để dễ đọc
        salary_corr = correlation_matrix['salary_in_usd'].drop('salary_in_usd').sort_values(key=abs, ascending=False)
        print(f"\n📊 Tương quan với salary_in_usd:")
        print("-" * 40)
        for feature, corr in salary_corr.items():
            direction = "Dương" if corr > 0 else "Âm"
            strength = "Mạnh" if abs(corr) > 0.5 else "Trung bình" if abs(corr) > 0.3 else "Yếu"
            print(f"  {feature:<25}: {corr:>7.3f} ({direction}, {strength})")

        plt.close()

    def generate_additional_charts_DISABLED(self, df_processed):
        """
        Tạo các biểu đồ bổ sung quan trọng

        Args:
            df_processed: DataFrame dữ liệu đã xử lý
        """
        print("\n4. TẠO CÁC BIỂU ĐỒ BỔ SUNG:")
        print("-" * 40)

        # 1. Correlation Matrix
        print("Tạo correlation matrix...")
        plt.figure(figsize=(12, 10))

        # Chọn các cột số để tính correlation
        numeric_cols = ['work_year', 'salary_in_usd', 'remote_ratio',
                       'experience_level_encoded', 'employment_type_encoded',
                       'job_title_encoded', 'company_size_encoded', 'is_us']

        corr_data = df_processed[numeric_cols]
        correlation_matrix = corr_data.corr()

        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm',
                   center=0, square=True, linewidths=0.5, fmt='.2f')
        plt.title('Ma trận tương quan giữa các biến', fontsize=16, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig('images/03_correlation_matrix.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        print("Đã lưu: images/03_correlation_matrix.png")
        plt.close()

        # 2. Salary Distribution by Job Title
        print("Tạo phân phối lương theo job title...")
        plt.figure(figsize=(15, 8))

        # Lấy top 10 job titles có nhiều mẫu nhất
        top_jobs = df_processed['job_title'].value_counts().head(10).index
        data_subset = df_processed[df_processed['job_title'].isin(top_jobs)]

        sns.boxplot(data=data_subset, x='job_title', y='salary_in_usd')
        plt.xticks(rotation=45, ha='right')
        plt.title('Phân phối mức lương theo Job Title (Top 10)', fontsize=16, fontweight='bold')
        plt.xlabel('Job Title')
        plt.ylabel('Mức lương (USD)')
        plt.tight_layout()
        plt.savefig('images/04_salary_by_job.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        print("Đã lưu: images/04_salary_by_job.png")
        plt.close()

        # 3. Experience Level Impact
        print("Tạo biểu đồ tác động của experience level...")
        plt.figure(figsize=(12, 6))

        exp_mapping = {0: 'Entry', 1: 'Mid', 2: 'Senior', 3: 'Executive'}
        df_processed_copy = df_processed.copy()
        df_processed_copy['exp_level_name'] = df_processed_copy['experience_level_encoded'].map(exp_mapping)

        exp_stats = df_processed_copy.groupby('exp_level_name')['salary_in_usd'].agg(['mean', 'count'])

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Mean salary by experience
        exp_stats['mean'].plot(kind='bar', ax=ax1, color='skyblue')
        ax1.set_title('Mức lương trung bình theo Experience Level')
        ax1.set_ylabel('Mức lương trung bình (USD)')
        ax1.tick_params(axis='x', rotation=45)

        # Count by experience
        exp_stats['count'].plot(kind='bar', ax=ax2, color='lightcoral')
        ax2.set_title('Số lượng mẫu theo Experience Level')
        ax2.set_ylabel('Số lượng')
        ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig('images/05_experience_impact.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        print("Đã lưu: images/05_experience_impact.png")
        plt.close()

        # 4. Company Size vs Salary
        print("Tạo biểu đồ company size vs salary...")
        plt.figure(figsize=(10, 6))

        size_mapping = {0: 'Small', 1: 'Medium', 2: 'Large'}
        df_processed_copy['company_size_name'] = df_processed_copy['company_size_encoded'].map(size_mapping)

        sns.violinplot(data=df_processed_copy, x='company_size_name', y='salary_in_usd')
        plt.title('Phân phối mức lương theo quy mô công ty', fontsize=16, fontweight='bold')
        plt.xlabel('Quy mô công ty')
        plt.ylabel('Mức lương (USD)')
        plt.tight_layout()
        plt.savefig('images/06_company_size_salary.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        print("Đã lưu: images/06_company_size_salary.png")
        plt.close()

        return True

    def generate_remote_impact_chart_DISABLED(self, df_processed):
        """
        Tạo biểu đồ tác động của remote ratio

        Args:
            df_processed: DataFrame dữ liệu đã xử lý
        """
        print("Tạo biểu đồ tác động của remote ratio...")
        plt.figure(figsize=(12, 6))

        # Chia remote ratio thành các nhóm
        df_processed_copy = df_processed.copy()
        df_processed_copy['remote_group'] = pd.cut(df_processed_copy['remote_ratio'],
                                                  bins=[0, 25, 75, 100],
                                                  labels=['On-site (0-25%)', 'Hybrid (25-75%)', 'Remote (75-100%)'],
                                                  include_lowest=True)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Box plot
        sns.boxplot(data=df_processed_copy, x='remote_group', y='salary_in_usd', ax=ax1)
        ax1.set_title('Mức lương theo mức độ Remote')
        ax1.set_xlabel('Mức độ Remote')
        ax1.set_ylabel('Mức lương (USD)')
        ax1.tick_params(axis='x', rotation=45)

        # Scatter plot với cải thiện
        ax2.scatter(df_processed_copy['remote_ratio'], df_processed_copy['salary_in_usd'],
                   alpha=0.6, s=20, color='blue')
        ax2.set_title('Mối quan hệ Remote Ratio vs Salary')
        ax2.set_xlabel('Remote Ratio (%)')
        ax2.set_ylabel('Mức lương (USD)')
        ax2.set_xticks([0, 25, 50, 75, 100])
        ax2.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('images/07_remote_impact.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        print("Đã lưu: images/07_remote_impact.png")
        plt.close()

        return True

    def generate_residuals_analysis_DISABLED(self, y_test, y_test_pred):
        """
        Tạo biểu đồ phân tích residuals chi tiết

        Args:
            y_test: Giá trị thực tế test set
            y_test_pred: Giá trị dự đoán test set
        """
        print("Tạo phân tích residuals chi tiết...")

        residuals = y_test - y_test_pred

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Phân tích Residuals chi tiết', fontsize=16, fontweight='bold')

        # 1. Histogram of residuals
        axes[0, 0].hist(residuals, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 0].set_title('Phân phối Residuals')
        axes[0, 0].set_xlabel('Residuals')
        axes[0, 0].set_ylabel('Tần suất')
        axes[0, 0].axvline(residuals.mean(), color='red', linestyle='--',
                          label=f'Mean: {residuals.mean():.2f}')
        axes[0, 0].legend()

        # 2. Q-Q plot
        stats.probplot(residuals, dist="norm", plot=axes[0, 1])
        axes[0, 1].set_title('Q-Q Plot (Normal Distribution)')
        axes[0, 1].grid(True)

        # 3. Residuals vs Fitted
        axes[1, 0].scatter(y_test_pred, residuals, alpha=0.6, color='green')
        axes[1, 0].axhline(y=0, color='red', linestyle='--')
        axes[1, 0].set_title('Residuals vs Fitted Values')
        axes[1, 0].set_xlabel('Fitted Values')
        axes[1, 0].set_ylabel('Residuals')

        # 4. Scale-Location plot
        sqrt_abs_residuals = np.sqrt(np.abs(residuals))
        axes[1, 1].scatter(y_test_pred, sqrt_abs_residuals, alpha=0.6, color='orange')
        axes[1, 1].set_title('Scale-Location Plot')
        axes[1, 1].set_xlabel('Fitted Values')
        axes[1, 1].set_ylabel('√|Residuals|')

        plt.tight_layout()
        plt.savefig('images/08_residuals_analysis.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        print("Đã lưu: images/08_residuals_analysis.png")
        plt.close()

        return True

    def generate_feature_importance_chart_OLD(self, X_train, model):
        """
        Tạo biểu đồ tầm quan trọng của features

        Args:
            X_train: Features training set
            model: Mô hình đã train
        """
        print("Tạo biểu đồ tầm quan trọng features...")

        feature_names = X_train.columns
        feature_importance = abs(model.coef_)
        feature_importance_normalized = feature_importance / feature_importance.sum() * 100

        # Tạo DataFrame để dễ xử lý
        importance_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': feature_importance_normalized,
            'Coefficient': model.coef_
        }).sort_values('Importance', ascending=True)

        plt.figure(figsize=(12, 8))

        # Tạo màu sắc dựa trên dấu của coefficient
        colors = ['red' if coef < 0 else 'green' for coef in importance_df['Coefficient']]

        bars = plt.barh(range(len(importance_df)), importance_df['Importance'], color=colors, alpha=0.7)
        plt.yticks(range(len(importance_df)), importance_df['Feature'])
        plt.xlabel('Tầm quan trọng (%)')
        plt.title('Tầm quan trọng của các Features trong mô hình\n(Xanh: Tác động tích cực, Đỏ: Tác động tiêu cực)',
                 fontsize=14, fontweight='bold')

        # Thêm giá trị lên các thanh
        for i, (bar, importance, coef) in enumerate(zip(bars, importance_df['Importance'], importance_df['Coefficient'])):
            plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{importance:.1f}%\n({coef:.0f})',
                    ha='left', va='center', fontsize=9)

        plt.tight_layout()
        plt.savefig('images/09_feature_importance.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        print("Đã lưu: images/09_feature_importance.png")
        plt.close()

        return True

    def generate_feature_importance_chart_selected(self, selected_features, model):
        """
        Tạo biểu đồ tầm quan trọng của 5 features được chọn

        Args:
            selected_features: List tên 5 features được chọn
            model: Mô hình đã train
        """
        print("Tạo biểu đồ Feature Importance cho 5 features được chọn...")

        # Tính feature importance
        feature_importance = abs(model.coef_)
        feature_importance_normalized = feature_importance / feature_importance.sum() * 100

        # Tạo DataFrame để dễ xử lý
        importance_df = pd.DataFrame({
            'feature': selected_features,
            'importance': feature_importance_normalized
        }).sort_values('importance', ascending=True)

        # Tạo biểu đồ
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))

        # Horizontal bar chart
        bars = ax.barh(importance_df['feature'], importance_df['importance'],
                      color='skyblue', edgecolor='navy', alpha=0.7)

        # Thêm giá trị lên các thanh
        for i, (bar, importance) in enumerate(zip(bars, importance_df['importance'])):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                   f'{importance:.1f}%', ha='left', va='center', fontweight='bold')

        ax.set_title('Tầm Quan Trọng của 5 Features Được Chọn\n(Feature Selection với SelectKBest)',
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Tầm Quan Trọng (%)', fontsize=12)
        ax.set_ylabel('Features', fontsize=12)
        ax.grid(axis='x', alpha=0.3)

        # Thêm thông tin
        ax.text(0.02, 0.98, f'Tổng: {len(selected_features)} features được chọn từ 7 features ban đầu',
               transform=ax.transAxes, fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

        plt.tight_layout()
        plt.savefig('images/04_selected_feature_importance.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        print("Đã lưu: images/04_selected_feature_importance.png")
        plt.close()

        return True

    def draw_visualize(self):
        print("🎨 Vẽ các biểu đồ phân tích...")
        # 1. Biểu đồ khám phá dữ liệu cơ bản
        self.visualize_data(self.data_processor.df_processed)

        # 2. Kết quả mô hình
        self.visualize_results(self.data_processor.model_results, self.data_processor.best_method,
                              self.data_processor.y_test, self.data_processor.y_test_pred,
                              self.data_processor.X_train_selected, self.data_processor.model,
                              self.data_processor.df_processed, self.data_processor.scaler)

        # 3. Feature importance cho 5 features được chọn
        self.generate_feature_importance_chart_selected(
            self.data_processor.selected_features,
            self.data_processor.model
        )

        # 4. Biểu đồ correlation matrix
        self.visualize_matrix(self.data_processor.df_processed)

        print("✅ Hoàn thành vẽ các biểu đồ quan trọng!")
        print("📊 Đã loại bỏ các biểu đồ redundant: Job Title, Company Size, Remote Impact, Residuals")

        return True
    