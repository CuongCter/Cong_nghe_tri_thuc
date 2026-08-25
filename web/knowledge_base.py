"""
Knowledge Base cho Hệ Chuyên Gia Tư Vấn Lương Data Science
============================================================

Mỗi luật có cấu trúc:
{
    "id": "R001",
    "category": "...",
    "description": "Mô tả ngắn",
    "if": {"field": value, ...},      # Điều kiện
    "then": {                         # Kết luận
        "tier": "...",
        "action": "...",
        "warning": "...",
        "salary_range": [min, max],
        ...
    },
    "cf": 0.85,                        # Certainty Factor (0-1)
    "priority": 1,                     # Ưu tiên khi xung đột
    "source": "..."                    # Nguồn tri thức
}

Tri thức được rút ra từ:
- Phân tích 10,473 records trong data-salary.csv
- Quy tắc ngành (US premium, experience premium, ...)
- Best practices trong tuyển dụng Data Science
"""

KNOWLEDGE_RULES = [
    # ============================================================
    # NHÓM 1: PHÂN LOẠI CẤP BẬC LƯƠNG (Salary Tier Classification)
    # Dựa trên mean salary của nhóm experience_level + is_us
    # ============================================================
    {
        "id": "R001",
        "category": "Salary Tier",
        "description": "Executive ở US - Tier cao nhất",
        "if": {"experience_level": "EX", "is_us": 1},
        "then": {
            "tier": "Tier 1 - Executive Premium (US)",
            "salary_range": [130000, 290000],
            "market_position": "Top 5%",
            "action": "Đề xuất mức lương cao nhất, bao gồm stock options và bonus",
            "warning": "Cạnh tranh gay gắt, cần phân biệt với Tier 2"
        },
        "cf": 0.95,
        "priority": 10,
        "source": "298 mẫu EX ở US, mean=$181,335"
    },
    {
        "id": "R002",
        "category": "Salary Tier",
        "description": "Executive ở Non-US - Tier cao ngoài Mỹ",
        "if": {"experience_level": "EX", "is_us": 0},
        "then": {
            "tier": "Tier 2 - Executive (Non-US)",
            "salary_range": [90000, 270000],
            "market_position": "Top 10% trong nước",
            "action": "Cân nhắc mức lương theo sức mua địa phương (PPP)",
            "warning": "Lương danh nghĩa có thể thấp hơn nhưng sức mua tương đương"
        },
        "cf": 0.85,
        "priority": 10,
        "source": "37 mẫu EX Non-US, mean=$150,122"
    },
    {
        "id": "R003",
        "category": "Salary Tier",
        "description": "Senior ở US - Tier phổ biến nhất",
        "if": {"experience_level": "SE", "is_us": 1},
        "then": {
            "tier": "Tier 2 - Senior (US)",
            "salary_range": [105000, 200000],
            "market_position": "Top 25-50%",
            "action": "Đây là nhóm phổ biến nhất (6068 mẫu). Đề xuất mức competitive",
            "warning": "Cạnh tranh cao với supply dồi dào"
        },
        "cf": 0.95,
        "priority": 10,
        "source": "6068 mẫu SE ở US, mean=$153,442, median=$147,572"
    },
    {
        "id": "R004",
        "category": "Salary Tier",
        "description": "Senior ở Non-US",
        "if": {"experience_level": "SE", "is_us": 0},
        "then": {
            "tier": "Tier 3 - Senior (Non-US)",
            "salary_range": [50000, 170000],
            "market_position": "Median thị trường",
            "action": "Điều chỉnh theo quốc gia cụ thể",
            "warning": "Đa dạng lớn giữa các nước (Ấn Độ vs Đức)"
        },
        "cf": 0.85,
        "priority": 10,
        "source": "546 mẫu SE Non-US, mean=$110,176"
    },
    {
        "id": "R005",
        "category": "Salary Tier",
        "description": "Mid-level ở US",
        "if": {"experience_level": "MI", "is_us": 1},
        "then": {
            "tier": "Tier 3 - Mid-level (US)",
            "salary_range": [80000, 170000],
            "market_position": "Median thị trường US",
            "action": "Đây là sweet spot cho thị trường tuyển dụng",
            "warning": "Có thể đàm phán thêm benefits"
        },
        "cf": 0.95,
        "priority": 10,
        "source": "2190 mẫu MI ở US, mean=$124,263"
    },
    {
        "id": "R006",
        "category": "Salary Tier",
        "description": "Mid-level ở Non-US",
        "if": {"experience_level": "MI", "is_us": 0},
        "then": {
            "tier": "Tier 4 - Mid-level (Non-US)",
            "salary_range": [40000, 120000],
            "market_position": "Phổ biến",
            "action": "Mức lương khởi điểm tốt cho người chuyển việc",
            "warning": "So sánh với chi phí sinh hoạt địa phương"
        },
        "cf": 0.85,
        "priority": 10,
        "source": "469 mẫu MI Non-US, mean=$77,843"
    },
    {
        "id": "R007",
        "category": "Salary Tier",
        "description": "Entry-level ở US",
        "if": {"experience_level": "EN", "is_us": 1},
        "then": {
            "tier": "Tier 4 - Entry-level (US)",
            "salary_range": [55000, 130000],
            "market_position": "Phổ biến cho fresh grads",
            "action": "Có thể offer thấp hơn median với đào tạo nội bộ",
            "warning": "Cạnh tranh với mức lương IT fresher chung"
        },
        "cf": 0.90,
        "priority": 10,
        "source": "685 mẫu EN ở US, mean=$94,600"
    },
    {
        "id": "R008",
        "category": "Salary Tier",
        "description": "Entry-level ở Non-US - Tier thấp nhất",
        "if": {"experience_level": "EN", "is_us": 0},
        "then": {
            "tier": "Tier 5 - Entry-level (Non-US)",
            "salary_range": [20000, 90000],
            "market_position": "Median thấp",
            "action": "Đào tạo nội bộ, có thể offer thấp hơn median",
            "warning": "Cạnh tranh với mức lương fresher IT chung"
        },
        "cf": 0.80,
        "priority": 10,
        "source": "180 mẫu EN Non-US, mean=$49,955"
    },

    # ============================================================
    # NHÓM 2: CHIẾN LƯỢC TUYỂN DỤNG (Recruitment Strategy)
    # Dựa trên hot jobs + experience
    # ============================================================
    {
        "id": "R010",
        "category": "Recruitment Strategy",
        "description": "Senior Data Scientist ở US - Thị trường nóng",
        "if": {"experience_level": "SE", "job_title": "Data Scientist", "is_us": 1},
        "then": {
            "strategy": "Thị trường cạnh tranh cao",
            "suggested_recruitment_time": "2-3 tháng",
            "suggested_bonus": "10-20% signing bonus",
            "benefits_to_highlight": ["Stock options", "Remote work", "Learning budget", "Conference budget"],
            "urgency": "Cao - cần hành động nhanh"
        },
        "cf": 0.90,
        "priority": 8,
        "source": "Top job phổ biến với 1215 mẫu SE DS ở US"
    },
    {
        "id": "R011",
        "category": "Recruitment Strategy",
        "description": "Senior Data Engineer ở US",
        "if": {"experience_level": "SE", "job_title": "Data Engineer", "is_us": 1},
        "then": {
            "strategy": "Thị trường cạnh tranh",
            "suggested_recruitment_time": "2-4 tháng",
            "suggested_bonus": "8-15% signing bonus",
            "benefits_to_highlight": ["Remote work", "Cloud certifications budget", "Tech conference"],
            "urgency": "Cao"
        },
        "cf": 0.88,
        "priority": 8,
        "source": "2243 mẫu SE DE ở US"
    },
    {
        "id": "R012",
        "category": "Recruitment Strategy",
        "description": "Senior Data Analyst ở US",
        "if": {"experience_level": "SE", "job_title": "Data Analyst", "is_us": 1},
        "then": {
            "strategy": "Thị trường bình thường",
            "suggested_recruitment_time": "1-2 tháng",
            "suggested_bonus": "5-10% signing bonus",
            "benefits_to_highlight": ["Flexible hours", "Career path to Data Scientist"],
            "urgency": "Trung bình"
        },
        "cf": 0.85,
        "priority": 7,
        "source": "1290 mẫu SE DA ở US"
    },
    {
        "id": "R013",
        "category": "Recruitment Strategy",
        "description": "Senior ở Non-US - Thị trường bình thường",
        "if": {"experience_level": "SE", "is_us": 0},
        "then": {
            "strategy": "Thị trường bình thường",
            "suggested_recruitment_time": "1-3 tháng",
            "suggested_bonus": "5-10% signing bonus",
            "benefits_to_highlight": ["Visa sponsorship (nếu cần)", "Remote work"],
            "urgency": "Trung bình"
        },
        "cf": 0.80,
        "priority": 6,
        "source": "Tổng hợp 546 mẫu SE Non-US"
    },

    # ============================================================
    # NHÓM 3: VỊ TRÍ ĐẶC BIỆT (Premium Roles)
    # Top paying jobs trong dataset
    # ============================================================
    {
        "id": "R020",
        "category": "Premium Role",
        "description": "Head of Data - vị trí cao nhất",
        "if": {"job_title": "Head of Data"},
        "then": {
            "tier": "C-Suite / VP Level",
            "salary_range": [150000, 290000],
            "action": "Offer cao + equity lớn, focus leadership impact",
            "required_experience": "EX (Executive)",
            "warning": "Không phù hợp với level EN/MI"
        },
        "cf": 0.95,
        "priority": 9,
        "source": "54 mẫu, mean=$198,392 - cao nhất trong dataset"
    },
    {
        "id": "R021",
        "category": "Premium Role",
        "description": "Director of Data Science",
        "if": {"job_title": "Director of Data Science"},
        "then": {
            "tier": "Director Level",
            "salary_range": [140000, 290000],
            "action": "Offer cao + bonus thưởng KPI",
            "required_experience": "EX (Executive)",
            "warning": "Yêu cầu kinh nghiệm quản lý nhiều năm"
        },
        "cf": 0.95,
        "priority": 9,
        "source": "28 mẫu, mean=$195,582"
    },
    {
        "id": "R022",
        "category": "Premium Role",
        "description": "Data Science Manager",
        "if": {"job_title": "Data Science Manager"},
        "then": {
            "tier": "Manager Level",
            "salary_range": [120000, 250000],
            "action": "Offer competitive + leadership bonus",
            "required_experience": "SE hoặc EX",
            "warning": "Cần cân bằng giữa technical và management"
        },
        "cf": 0.92,
        "priority": 8,
        "source": "107 mẫu, mean=$178,533"
    },
    {
        "id": "R023",
        "category": "Premium Role",
        "description": "Data Architect - cao hơn Data Engineer",
        "if": {"job_title": "Data Architect"},
        "then": {
            "tier": "Architect / Senior IC",
            "salary_range": [100000, 230000],
            "action": "Offer theo kinh nghiệm + tech stack premium",
            "required_experience": "SE thường",
            "warning": "Cần deep technical expertise"
        },
        "cf": 0.90,
        "priority": 7,
        "source": "421 mẫu, mean=$154,707"
    },

    # ============================================================
    # NHÓM 4: CẢNH BÁO BẤT THƯỜNG (Anomaly Detection)
    # ============================================================
    {
        "id": "R030",
        "category": "Anomaly",
        "description": "Entry-level với remote 100% ở US - Bất thường",
        "if": {"experience_level": "EN", "is_us": 1, "remote_ratio": 100},
        "then": {
            "warning": "Entry-level, Mỹ, 100% remote - dữ liệu hạn chế",
            "action": "Kiểm tra job_title cụ thể, có thể offer thận trọng",
            "confidence_adjustment": -0.15,
            "reason": "Pattern ít gặp trong data, MAE có thể cao hơn"
        },
        "cf": 0.70,
        "priority": 5,
        "source": "Pattern bất thường"
    },
    {
        "id": "R031",
        "category": "Anomaly",
        "description": "Executive level với company size S",
        "if": {"experience_level": "EX", "company_size": "S"},
        "then": {
            "warning": "EX ở công ty nhỏ - có thể là founder/CEO",
            "action": "Verify lại job_title và title thực tế",
            "confidence_adjustment": -0.20,
            "reason": "Mẫu rất ít, có thể noise"
        },
        "cf": 0.60,
        "priority": 5,
        "source": "Mẫu cực ít trong data"
    },
    {
        "id": "R032",
        "category": "Anomaly",
        "description": "Entry-level với job_title cao cấp",
        "if": {"experience_level": "EN", "job_title_in": ["Head of Data", "Director of Data Science", "Data Science Manager"]},
        "then": {
            "warning": "Bất thường: EN không phù hợp với vị trí quản lý cao",
            "action": "Verify lại experience_level và job_title",
            "confidence_adjustment": -0.30,
            "reason": "Có thể nhập liệu sai hoặc title inflation"
        },
        "cf": 0.65,
        "priority": 6,
        "source": "Logic ngành"
    },

    # ============================================================
    # NHÓM 5: CÔNG TY VÀ MÔI TRƯỜNG LÀM VIỆC
    # ============================================================
    {
        "id": "R040",
        "category": "Company Size",
        "description": "Công ty lớn - Lương ổn định",
        "if": {"company_size": "L"},
        "then": {
            "characteristic": "Công ty lớn - quy trình chuẩn",
            "salary_adjustment": "Có thể thấp hơn M nhưng stable hơn",
            "benefits_to_highlight": ["Health insurance tốt", "Pension plan", "Job security"],
            "action": "Đánh giá tổng compensation package"
        },
        "cf": 0.85,
        "priority": 4,
        "source": "370 mẫu size L, mean=$120,629"
    },
    {
        "id": "R041",
        "category": "Company Size",
        "description": "Công ty vừa - Sweet spot",
        "if": {"company_size": "M"},
        "then": {
            "characteristic": "Công ty vừa - balance tốt nhất",
            "salary_adjustment": "Median cao nhất trong 3 nhóm",
            "benefits_to_highlight": ["Equity upside", "Flexible role", "Impact trực tiếp"],
            "action": "Điểm hấp dẫn nhất cho nhiều ứng viên"
        },
        "cf": 0.95,
        "priority": 4,
        "source": "10035 mẫu size M (96% data), mean=$137,894"
    },
    {
        "id": "R042",
        "category": "Company Size",
        "description": "Công ty nhỏ - Lương thấp nhưng linh hoạt",
        "if": {"company_size": "S"},
        "then": {
            "characteristic": "Công ty nhỏ/startup",
            "salary_adjustment": "Lương thấp hơn 50% so với M",
            "benefits_to_highlight": ["Equity lớn", "Đa vai trò", "Tăng tốc nhanh"],
            "action": "Cân nhắc equity thay vì base salary"
        },
        "cf": 0.85,
        "priority": 4,
        "source": "68 mẫu size S, mean=$71,606"
    },

    # ============================================================
    # NHÓM 6: LOẠI HÌNH LÀM VIỆC (Employment Type)
    # ============================================================
    {
        "id": "R050",
        "category": "Employment Type",
        "description": "Full-time - phổ biến nhất",
        "if": {"employment_type": "FT"},
        "then": {
            "characteristic": "Full-time - chuẩn nhất",
            "salary_range": "Ổn định, có benefits đầy đủ",
            "action": "Offer competitive với full benefits package"
        },
        "cf": 0.95,
        "priority": 3,
        "source": "10440 mẫu (99.7% data), mean=$137,017"
    },
    {
        "id": "R051",
        "category": "Employment Type",
        "description": "Part-time - Lương thấp hơn",
        "if": {"employment_type": "PT"},
        "then": {
            "characteristic": "Part-time - phụ thêm",
            "salary_range": "Thấp hơn FT 40-50%",
            "action": "Thường làm thêm ngoài giờ"
        },
        "cf": 0.80,
        "priority": 3,
        "source": "25 mẫu PT, mean=$81,094"
    },
    {
        "id": "R052",
        "category": "Employment Type",
        "description": "Contract - Trung bình",
        "if": {"employment_type": "CT"},
        "then": {
            "characteristic": "Contract - dự án ngắn hạn",
            "salary_range": "Có thể cao hơn FT theo giờ",
            "action": "Negotiate rate per hour cao hơn"
        },
        "cf": 0.75,
        "priority": 3,
        "source": "5 mẫu CT, mean=$128,379"
    },
    {
        "id": "R053",
        "category": "Employment Type",
        "description": "Freelance - Rủi ro cao",
        "if": {"employment_type": "FL"},
        "then": {
            "characteristic": "Freelance - không ổn định",
            "salary_range": "Dao động lớn",
            "action": "Cần đánh giá kỹ năng tự quản lý"
        },
        "cf": 0.70,
        "priority": 3,
        "source": "3 mẫu FL, mean=$47,000"
    },

    # ============================================================
    # NHÓM 7: XU HƯỚNG THEO NĂM (Year Trend)
    # ============================================================
    {
        "id": "R060",
        "category": "Year Trend",
        "description": "Năm 2024 - Lương ổn định",
        "if": {"work_year": 2024},
        "then": {
            "trend": "Mức lương tăng 76% so với 2020",
            "action": "Dùng data 2023-2024 làm reference chính",
            "growth_rate": "Từ $77k (2020) → $135k (2024)"
        },
        "cf": 0.95,
        "priority": 2,
        "source": "3706 mẫu 2024, mean=$135,669"
    },
    {
        "id": "R061",
        "category": "Year Trend",
        "description": "Pre-2022 - Lương thấp hơn",
        "if": {"work_year_in": [2020, 2021]},
        "then": {
            "warning": "Dữ liệu cũ, lương có thể không reflect thị trường hiện tại",
            "action": "Sử dụng thận trọng"
        },
        "cf": 0.85,
        "priority": 2,
        "source": "Chỉ 164 mẫu trước 2022"
    },

    # ============================================================
    # NHÓM 8: REMOTE WORK
    # ============================================================
    {
        "id": "R070",
        "category": "Remote Work",
        "description": "100% Remote - Phổ biến thứ 2",
        "if": {"remote_ratio": 100},
        "then": {
            "characteristic": "Fully remote - tăng nhẹ so với on-site",
            "salary_adjustment": "+1.3% so với on-site",
            "benefits_to_highlight": ["Work from anywhere", "No commute"],
            "action": "Tốt cho talent giữa các thành phố"
        },
        "cf": 0.88,
        "priority": 2,
        "source": "3446 mẫu (33%), mean=$138,808"
    },
    {
        "id": "R071",
        "category": "Remote Work",
        "description": "On-site (0%) - Phổ biến nhất",
        "if": {"remote_ratio": 0},
        "then": {
            "characteristic": "On-site truyền thống",
            "salary_adjustment": "Baseline",
            "benefits_to_highlight": ["Team collaboration", "Office perks"]
        },
        "cf": 0.92,
        "priority": 2,
        "source": "6915 mẫu (66%), mean=$136,994"
    },
    {
        "id": "R072",
        "category": "Remote Work",
        "description": "Hybrid 50% - Ít phổ biến",
        "if": {"remote_ratio": 50},
        "then": {
            "warning": "Dữ liệu hạn chế cho hybrid 50%",
            "salary_adjustment": "Mean thấp hơn do mẫu nhỏ",
            "action": "Dùng model dự đoán chính, không nên dựa vào mean thống kê"
        },
        "cf": 0.60,
        "priority": 2,
        "source": "Chỉ 112 mẫu, có thể không đại diện"
    },

    # ============================================================
    # NHÓM 9: META-RULES (Luật meta cho recommendation)
    # ============================================================
    {
        "id": "R090",
        "category": "Meta",
        "description": "Tổng hợp khuyến nghị cho US Premium",
        "if": {"is_us": 1, "experience_level_in": ["SE", "EX"]},
        "then": {
            "tier_label": "US Premium Talent",
            "general_advice": "Thị trường Mỹ cạnh tranh cao, cần offer tốt để giữ chân",
            "salary_negotiation_tips": [
                "Nhấn mạnh unique skills",
                "Đưa competing offers",
                "Đàm phán equity + bonus",
                "Linh hoạt về remote work"
            ],
            "recommended_actions": ["Quick offer (trong 1 tuần)", "Signing bonus", "Equity upside"]
        },
        "cf": 0.92,
        "priority": 1,
        "source": "Quy tắc ngành US tech"
    },
    {
        "id": "R091",
        "category": "Meta",
        "description": "Tổng hợp khuyến nghị cho Non-US Cost-conscious",
        "if": {"is_us": 0, "experience_level_in": ["MI", "SE"]},
        "then": {
            "tier_label": "Non-US Market Standard",
            "general_advice": "Cân nhắc PPP và cost of living khi offer",
            "salary_negotiation_tips": [
                "Tham khảo levels.fyi cho region",
                "Cân nhắc benefits thay vì cash",
                "Nhấn mạnh work-life balance"
            ],
            "recommended_actions": ["Standard offer", "Clear career path", "Local benefits"]
        },
        "cf": 0.85,
        "priority": 1,
        "source": "Quy tắc ngành quốc tế"
    }
]


def get_rules_by_category(category=None):
    """Lấy luật theo category"""
    if category is None:
        return KNOWLEDGE_RULES
    return [r for r in KNOWLEDGE_RULES if r["category"] == category]


def get_all_categories():
    """Lấy tất cả categories"""
    return sorted(set(r["category"] for r in KNOWLEDGE_RULES))


def get_rule_by_id(rule_id):
    """Tìm luật theo ID"""
    for r in KNOWLEDGE_RULES:
        if r["id"] == rule_id:
            return r
    return None


def get_rule_stats():
    """Thống kê về Knowledge Base"""
    total = len(KNOWLEDGE_RULES)
    by_category = {}
    for r in KNOWLEDGE_RULES:
        by_category[r["category"]] = by_category.get(r["category"], 0) + 1
    return {
        "total_rules": total,
        "by_category": by_category,
        "categories": get_all_categories()
    }