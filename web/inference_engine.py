"""
Inference Engine cho Hệ Chuyên Gia Tư Vấn Lương
=================================================

Thực hiện:
- Forward chaining: từ facts (input) → match rules → fire conclusions
- Certainty Factor (CF) propagation theo công thức MYCIN
- Conflict resolution khi nhiều luật cùng category
- Working memory để luật sau có thể dùng kết quả luật trước
"""

from knowledge_base import KNOWLEDGE_RULES


class InferenceEngine:
    """Bộ suy diễn cho hệ chuyên gia"""

    def __init__(self, rules=None):
        """Khởi tạo với knowledge base"""
        self.rules = rules if rules is not None else KNOWLEDGE_RULES
        self.working_memory = {}
        self.fired_rules = []
        self.firing_log = []

    def reset(self):
        """Reset working memory"""
        self.working_memory = {}
        self.fired_rules = []
        self.firing_log = []

    def forward_chaining(self, facts, max_iterations=5):
        """
        Forward chaining: từ sự kiện ban đầu, áp dụng luật để sinh kết luận.
        Lặp tối đa max_iterations lần để cho phép luật mới dùng kết quả luật cũ.

        Args:
            facts: dict input từ người dùng
            max_iterations: số lần lặp tối đa

        Returns:
            list các luật đã được kích hoạt
        """
        self.reset()
        self.working_memory = dict(facts)

        for iteration in range(max_iterations):
            new_rules_fired = []

            for rule in self.rules:
                if rule["id"] in [r["rule_id"] for r in self.fired_rules]:
                    continue  # Không fire lại luật đã fire

                if self._match_conditions(rule["if"], self.working_memory):
                    fired = {
                        "rule_id": rule["id"],
                        "category": rule["category"],
                        "description": rule.get("description", ""),
                        "then": rule["then"],
                        "cf": rule["cf"],
                        "priority": rule.get("priority", 5),
                        "source": rule.get("source", ""),
                        "iteration": iteration + 1
                    }
                    self.fired_rules.append(fired)
                    new_rules_fired.append(fired)

                    # Cập nhật working memory với kết luận
                    self._update_working_memory(rule["then"])

                    self.firing_log.append(
                        f"[Iter {iteration+1}] Fired {rule['id']} ({rule['category']}) CF={rule['cf']}"
                    )

            # Nếu không có luật mới nào fire → dừng
            if not new_rules_fired:
                break

        return self.fired_rules

    def _match_conditions(self, conditions, facts):
        """
        Kiểm tra điều kiện của luật có khớp với facts không.
        Hỗ trợ: equality, _in (giá trị nằm trong list)
        """
        for key, expected in conditions.items():
            # Hỗ trợ toán tử đặc biệt: key_in (giá trị nằm trong list)
            if key.endswith("_in"):
                field = key[:-3]  # Bỏ _in
                if field not in facts:
                    return False
                if facts[field] not in expected:
                    return False
            else:
                if key not in facts:
                    return False
                actual = facts[key]
                if isinstance(expected, list):
                    if actual not in expected:
                        return False
                else:
                    if actual != expected:
                        return False
        return True

    def _update_working_memory(self, conclusions):
        """Cập nhật working memory với kết luận (flat các giá trị)"""
        for k, v in conclusions.items():
            if isinstance(v, (str, int, float, bool)):
                self.working_memory[f"derived_{k}"] = v

    def combine_certainty_factors(self, cf_values):
        """
        Kết hợp nhiều CF khi nhiều luật cùng kết luận (MYCIN-style).

        Công thức:
        - Nếu cùng dương: CF = CF1 + CF2 * (1 - CF1)
        - Nếu cùng âm: CF = CF1 + CF2 * (1 + CF1)
        - Nếu khác dấu: CF = (CF1 + CF2) / (1 - min(|CF1|, |CF2|))

        Args:
            cf_values: list các CF (0-1 hoặc -1-1)

        Returns:
            CF hợp nhất
        """
        if not cf_values:
            return 0

        result = cf_values[0]
        for cf in cf_values[1:]:
            if result >= 0 and cf >= 0:
                # Cùng dương
                result = result + cf * (1 - result)
            elif result <= 0 and cf <= 0:
                # Cùng âm
                result = result + cf * (1 + result)
            else:
                # Khác dấu
                denom = 1 - min(abs(result), abs(cf))
                if denom == 0:
                    result = 0
                else:
                    result = (result + cf) / denom

        return max(-1, min(1, result))  # Clamp

    def get_combined_confidence_by_category(self):
        """
        Tính CF tổng hợp theo từng category
        Trả về dict {category: {cf_combined, rules_fired}}
        """
        by_category = {}
        for fired in self.fired_rules:
            cat = fired["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(fired["cf"])

        result = {}
        for cat, cfs in by_category.items():
            result[cat] = {
                "cf_combined": round(self.combine_certainty_factors(cfs), 3),
                "rules_count": len(cfs),
                "cf_values": [round(c, 3) for c in cfs]
            }

        return result

    def resolve_conflicts(self):
        """
        Khi nhiều luật cùng category và tier → chọn luật có priority cao nhất.
        Trả về danh sách conclusions đã được resolve.
        """
        # Nhóm theo category
        by_category = {}
        for fired in self.fired_rules:
            cat = fired["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(fired)

        # Trong mỗi category, chọn luật priority cao nhất
        resolved = []
        for cat, rules in by_category.items():
            # Sắp xếp theo priority giảm dần
            rules_sorted = sorted(rules, key=lambda r: r.get("priority", 0), reverse=True)
            # Giữ luật đầu tiên (priority cao nhất)
            resolved.append(rules_sorted[0])

        return resolved

    def synthesize_recommendation(self, ml_prediction):
        """
        Tổng hợp khuyến nghị cuối cùng từ ML + Rules

        Args:
            ml_prediction: dict từ predict_with_coefficients hoặc predict_with_trained_model
                {prediction, confidence_lower, confidence_upper, method, mae}

        Returns:
            dict recommendation tổng hợp
        """
        # Phân loại tier chính từ Salary Tier
        tier = None
        strategy = None
        warnings = []
        actions = []
        benefits = []
        negotiation_tips = []
        anomalies = []

        for r in self.fired_rules:
            cat = r["category"]
            then = r["then"]

            if cat == "Salary Tier" and tier is None:
                tier = then.get("tier", "")
            elif cat == "Recruitment Strategy" and strategy is None:
                strategy = then
            elif cat == "Premium Role":
                tier = then.get("tier", tier)
            elif cat == "Anomaly":
                anomalies.append(then.get("warning", ""))
                if then.get("action"):
                    warnings.append(then.get("action"))
            elif cat == "Meta":
                if then.get("tier_label"):
                    tier = then.get("tier_label")
                if then.get("salary_negotiation_tips"):
                    negotiation_tips.extend(then.get("salary_negotiation_tips", []))
                if then.get("recommended_actions"):
                    actions.extend(then.get("recommended_actions", []))
            else:
                if then.get("action"):
                    actions.append(then.get("action"))
                if then.get("benefits_to_highlight"):
                    benefits.extend(then.get("benefits_to_highlight", []))

        # Tính confidence tổng thể
        combined = self.get_combined_confidence_by_category()
        overall_cf = self._calculate_overall_cf(combined)

        return {
            "ml_prediction": ml_prediction,
            "tier": tier or "Standard",
            "strategy": strategy,
            "warnings": list(set(warnings + anomalies)),
            "actions": list(set(actions)),
            "benefits_to_highlight": list(set(benefits)),
            "negotiation_tips": negotiation_tips,
            "overall_confidence": overall_cf,
            "category_confidences": combined,
            "rules_fired_count": len(self.fired_rules),
            "firing_log": self.firing_log
        }

    def _calculate_overall_cf(self, combined_categories):
        """
        Tính overall confidence từ tất cả categories.
        Sử dụng weighted average theo priority.
        """
        if not combined_categories:
            return 0.0

        cfs = [v["cf_combined"] for v in combined_categories.values()]
        return round(sum(cfs) / len(cfs), 3)

    def get_key_drivers(self, ml_prediction):
        """Trích xuất các yếu tố chính ảnh hưởng đến dự đoán"""
        facts = self.working_memory
        drivers = []

        # is_us - yếu tố quan trọng nhất
        if facts.get("is_us") == 1:
            drivers.append({
                "factor": "is_us",
                "impact": "+$15,282",
                "reason": "Thị trường Mỹ trả cao hơn 35% so với Non-US",
                "importance": 0.351
            })
        else:
            drivers.append({
                "factor": "is_us",
                "impact": "Baseline",
                "reason": "Non-US (sức mua địa phương thấp hơn)",
                "importance": 0.351
            })

        # Experience level
        exp_impact = {
            "EN": {"impact": "Baseline", "importance": 0.328},
            "MI": {"impact": "+$14,263", "importance": 0.328},
            "SE": {"impact": "+$28,526", "importance": 0.328},
            "EX": {"impact": "+$42,789", "importance": 0.328}
        }
        exp = facts.get("experience_level")
        if exp in exp_impact:
            d = exp_impact[exp]
            drivers.append({
                "factor": f"experience_level ({exp})",
                "impact": d["impact"],
                "reason": f"Trình độ {exp} trong thị trường Data Science",
                "importance": d["importance"]
            })

        # Job title
        job = facts.get("job_title")
        job_premium = {
            "Head of Data": "+$60,000",
            "Director of Data Science": "+$58,000",
            "Data Science Manager": "+$45,000",
            "Data Product Manager": "+$20,000",
            "Data Architect": "+$18,000",
            "Data Scientist": "+$12,000",
            "Data Engineer": "+$6,000",
            "Data Analyst": "-$30,000",
            "Data Specialist": "-$45,000"
        }
        if job in job_premium:
            drivers.append({
                "factor": f"job_title ({job})",
                "impact": job_premium[job],
                "reason": f"Vị trí {job} trong hệ thống lương",
                "importance": 0.267
            })

        # Remote ratio
        remote = facts.get("remote_ratio")
        if remote == 100:
            drivers.append({
                "factor": "remote_ratio (100%)",
                "impact": "+$29,369",
                "reason": "100% remote có salary nhỉnh hơn",
                "importance": 0.053
            })
        elif remote == 50:
            drivers.append({
                "factor": "remote_ratio (50%)",
                "impact": "+$14,685",
                "reason": "Hybrid working",
                "importance": 0.053
            })

        return drivers


def run_inference(facts, ml_predictor):
    """
    Hàm tiện ích để chạy inference hoàn chỉnh.

    Args:
        facts: dict input từ người dùng
        ml_predictor: function(data) → dict {prediction, confidence_lower, ...}

    Returns:
        dict recommendation tổng h�p
    """
    engine = InferenceEngine()

    # Bước 1: Forward chaining
    fired_rules = engine.forward_chaining(facts)

    # Bước 2: ML prediction
    ml_pred = ml_predictor(facts)

    # Bước 3: Synthesize
    recommendation = engine.synthesize_recommendation(ml_pred)

    # Bước 4: Thêm key drivers
    recommendation["key_drivers"] = engine.get_key_drivers(ml_pred)

    # Bước 5: Fired rules details
    recommendation["rules_fired"] = fired_rules
    recommendation["engine_state"] = {
        "working_memory_keys": list(engine.working_memory.keys()),
        "iterations_used": max((r["iteration"] for r in fired_rules), default=0)
    }

    return recommendation


# ============================================================
# BACKWARD CHAINING ENGINE - Suy diễn ngược
# ============================================================
#
# Forward chaining:  Facts → Rules → Conclusions
# Backward chaining: Goal → Rules → Sub-goals → Facts cần thiết
#
# Use case: "Tôi có budget $150k, nên tuyển vị trí nào?"
#   → Goal: salary_in_range($150k)
#   → Tìm rules có kết luận về salary_range phù hợp
#   → Trích xuất facts (job_title, experience_level, is_us) từ điều kiện
#   → Verify bằng ML prediction
# ============================================================

from knowledge_base import KNOWLEDGE_RULES  # noqa: F401
import itertools


class BackwardChainingEngine:
    """Bộ suy diễn ngược: từ mức lương mong muốn → tìm vị trí phù hợp"""

    def __init__(self, rules=None):
        self.rules = rules if rules is not None else KNOWLEDGE_RULES
        self.search_log = []

    def reset_log(self):
        self.search_log = []

    def find_matching_combinations(self,
                                    target_salary,
                                    min_salary=None,
                                    max_salary=None,
                                    company_location=None,
                                    employment_type=None,
                                    remote_ratio=None,
                                    top_k=5):
        """
        Tìm các combinations (job_title, experience_level) có mức lương
        dự đoán nằm trong khoảng [min_salary, max_salary].

        Args:
            target_salary: mức lương mong muốn (dùng để xác định khoảng ±20%)
            min_salary: cận dưới (mặc định = target_salary * 0.8)
            max_salary: cận trên (mặc định = target_salary * 1.2)
            company_location: ràng buộc vị trí địa lý ('US' / 'Other')
            employment_type: ràng buộc loại hợp đồng ('FT', 'PT', ...)
            remote_ratio: ràng buộc tỷ lệ remote (0/50/100)
            top_k: số kết quả trả về

        Returns:
            dict với các combinations được xếp hạng theo độ sát với target
        """
        self.reset_log()

        # Default range: ±20% quanh target
        if min_salary is None:
            min_salary = int(target_salary * 0.8)
        if max_salary is None:
            max_salary = int(target_salary * 1.2)

        # 14 job titles + 4 experience levels = 56 combinations cơ sở
        all_jobs = [
            'Data Engineer', 'Data Scientist', 'Data Analyst',
            'Data Architect', 'Data Science', 'Data Manager',
            'Data Science Manager', 'Data Specialist',
            'Data Science Consultant', 'Data Analytics Manager',
            'Head of Data', 'Data Modeler', 'Data Product Manager',
            'Director of Data Science'
        ]
        all_levels = ['EN', 'MI', 'SE', 'EX']
        all_locations = ['US', 'Other']
        all_emp_types = ['FT', 'PT', 'CT', 'FL']
        all_remote = [0, 50, 100]
        all_sizes = ['S', 'M', 'L']

        # Filter theo ràng buộc
        locations = [company_location] if company_location else all_locations
        emp_types = [employment_type] if employment_type else all_emp_types
        remotes = [remote_ratio] if remote_ratio is not None else all_remote

        candidates = []
        evaluated = 0

        # Lazy import để tránh circular
        from app import predict_with_coefficients, predict_with_trained_model
        try:
            from app import analyzer
            ml_predictor = predict_with_trained_model if (analyzer and hasattr(analyzer, 'model')) else predict_with_coefficients
        except Exception:
            ml_predictor = predict_with_coefficients

        # Duyệt combinations
        for job in all_jobs:
            for level in all_levels:
                # Tìm luật tier phù hợp
                tier_info = self._find_tier_rule(job, level, None)
                if not tier_info:
                    continue

                for loc in locations:
                    for emp in emp_types:
                        for remote in remotes:
                            for size in all_sizes:
                                evaluated += 1

                                facts = {
                                    'work_year': 2024,
                                    'experience_level': level,
                                    'employment_type': emp,
                                    'job_title': job,
                                    'remote_ratio': remote,
                                    'company_size': size,
                                    'company_location': loc,
                                    'is_us': 1 if loc == 'US' else 0
                                }

                                try:
                                    pred = ml_predictor(facts)
                                    salary = pred.get('prediction', 0)
                                    mae = pred.get('mae', 0)

                                    # Check nếu nằm trong khoảng
                                    if min_salary <= salary <= max_salary:
                                        # Tính điểm sát với target (càng nhỏ càng tốt)
                                        distance = abs(salary - target_salary)
                                        # Càng ít rules fired thì CF càng cao → bonus
                                        confidence_bonus = (1 - mae / max(salary, 1)) * 0.1

                                        candidates.append({
                                            'job_title': job,
                                            'experience_level': level,
                                            'company_location': loc,
                                            'employment_type': emp,
                                            'remote_ratio': remote,
                                            'company_size': size,
                                            'predicted_salary': salary,
                                            'distance_from_target': distance,
                                            'mae': mae,
                                            'tier': tier_info.get('tier', ''),
                                            'cf': tier_info.get('cf', 0),
                                            'match_score': self._calculate_match_score(
                                                distance, target_salary, confidence_bonus
                                            ),
                                            'within_range': True
                                        })
                                except Exception:
                                    continue

        # Sắp xếp: ưu tiên diverse combination trước, rồi mới distance
        # Mục tiêu: mỗi experience_level chỉ lấy 1-2 candidates tốt nhất
        # Mỗi job_title chỉ lấy 1 candidate tốt nhất

        # Bước 1: Group theo experience_level + job_title, lấy best candidate
        best_by_combo = {}
        for c in candidates:
            key = (c['experience_level'], c['job_title'])
            if key not in best_by_combo or c['distance_from_target'] < best_by_combo[key]['distance_from_target']:
                best_by_combo[key] = c

        unique_candidates = list(best_by_combo.values())

        # Bước 2: Sắp xếp theo distance tăng dần
        unique_candidates.sort(key=lambda x: x['distance_from_target'])

        self.search_log.append(f"Evaluated {evaluated} combinations")
        self.search_log.append(f"Found {len(candidates)} total matches, {len(unique_candidates)} unique profiles")

        return {
            'target_salary': target_salary,
            'min_salary': min_salary,
            'max_salary': max_salary,
            'constraints': {
                'company_location': company_location,
                'employment_type': employment_type,
                'remote_ratio': remote_ratio
            },
            'candidates': unique_candidates[:top_k],
            'total_matches': len(candidates),
            'unique_profiles': len(unique_candidates),
            'evaluated': evaluated,
            'search_log': self.search_log
        }

    def _find_tier_rule(self, job_title, experience_level, is_us):
        """Tìm luật tier phù h�p với job + experience"""
        best_rule = None
        best_priority = -1

        for rule in self.rules:
            if rule['category'] not in ['Salary Tier', 'Premium Role']:
                continue

            conds = rule['if']

            # Check experience_level
            if 'experience_level' in conds and conds['experience_level'] != experience_level:
                continue

            # Check job_title
            if 'job_title' in conds and conds['job_title'] != job_title:
                continue

            # Check job_title_in
            if 'job_title_in' in conds and job_title not in conds['job_title_in']:
                continue

            # Check is_us nếu có constraint
            if is_us is not None and 'is_us' in conds and conds['is_us'] != is_us:
                continue

            priority = rule.get('priority', 5)
            if priority > best_priority:
                best_priority = priority
                best_rule = {
                    'tier': rule['then'].get('tier', ''),
                    'cf': rule['cf'],
                    'salary_range': rule['then'].get('salary_range')
                }

        return best_rule

    def _calculate_match_score(self, distance, target, confidence_bonus):
        """
        Tính điểm match score (0-1).
        Càng sát target + càng ít MAE càng tốt.
        """
        if target == 0:
            return 0

        # Khoảng cách tương đối (càng nhỏ càng tốt)
        relative_distance = distance / target

        # Score = 1 - relative_distance (tối đa 1)
        base_score = max(0, 1 - relative_distance)

        return min(1, base_score + confidence_bonus)

    def explain_recommendation(self, candidate):
        """Sinh giải thích cho một candidate"""
        explanations = []

        # Tier explanation
        if candidate.get('tier'):
            explanations.append({
                'type': 'tier',
                'text': f"📊 Vị trí thuộc nhóm: {candidate['tier']} (CF: {candidate['cf']*100:.0f}%)"
            })

        # Salary explanation
        explanations.append({
            'type': 'salary',
            'text': f"💰 Mức lương dự đoán: ${candidate['predicted_salary']:,} (±${candidate['mae']:,})"
        })

        # Distance explanation
        explanations.append({
            'type': 'accuracy',
            'text': f"🎯 Cách target ${abs(candidate['distance_from_target']):,}"
        })

        # Combination explanation
        explanations.append({
            'type': 'combination',
            'text': f"👤 {candidate['experience_level']} - {candidate['job_title']} - {candidate['company_location']} - {candidate['company_size']} - {candidate['remote_ratio']}% remote"
        })

        return explanations


def run_backward_inference(target_salary,
                           company_location=None,
                           employment_type=None,
                           remote_ratio=None,
                           top_k=5):
    """
    Hàm tiện ích chạy backward chaining.

    Args:
        target_salary: mức lương mong muốn
        constraints: location, employment_type, remote_ratio
        top_k: số kết quả

    Returns:
        dict recommendations
    """
    engine = BackwardChainingEngine()
    result = engine.find_matching_combinations(
        target_salary=target_salary,
        company_location=company_location,
        employment_type=employment_type,
        remote_ratio=remote_ratio,
        top_k=top_k
    )

    # Thêm explanations cho top candidates
    for candidate in result['candidates']:
        candidate['explanations'] = engine.explain_recommendation(candidate)

    return result