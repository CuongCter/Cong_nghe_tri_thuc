"""
Explanation Module cho Hệ Chuyên Gia Tư Vấn Lương
==================================================

Cung cấp:
- Giải thích từng luật được kích hoạt
- Phân tích breakdown mức lương
- So sánh với thị trường
- Action items cho HR/Ứng viên
- Visual explanation data
"""


class ExplanationModule:
    """Module giải thích kết quả từ hệ chuyên gia"""

    def __init__(self):
        self.explanations = []

    def explain(self, recommendation):
        """
        Tạo explanation toàn diện từ recommendation.

        Args:
            recommendation: dict từ InferenceEngine.synthesize_recommendation()

        Returns:
            dict explanation
        """
        ml = recommendation.get("ml_prediction", {})
        tier = recommendation.get("tier", "Unknown")
        rules_fired = recommendation.get("rules_fired", [])
        key_drivers = recommendation.get("key_drivers", [])

        # 1. Rules explanation
        rules_explanation = self._explain_rules(rules_fired)

        # 2. Salary breakdown
        salary_breakdown = self._explain_salary(ml, tier)

        # 3. Market comparison
        market_context = self._explain_market_context(recommendation)

        # 4. Action items
        action_items = self._generate_action_items(recommendation)

        # 5. Confidence narrative
        confidence_narrative = self._explain_confidence(recommendation)

        return {
            "salary_breakdown": salary_breakdown,
            "rules_explanation": rules_explanation,
            "market_context": market_context,
            "action_items": action_items,
            "confidence_narrative": confidence_narrative,
            "summary": self._generate_summary(recommendation, rules_explanation)
        }

    def _explain_rules(self, rules_fired):
        """Giải thích từng luật được kích hoạt"""
        explanations = []
        for r in rules_fired:
            cat = r.get("category", "")
            then = r.get("then", {})
            cf = r.get("cf", 0)
            source = r.get("source", "")

            if cat == "Salary Tier":
                explanations.append({
                    "rule_id": r["rule_id"],
                    "type": "tier",
                    "title": f"Phân loại: {then.get('tier', 'Unknown')}",
                    "message": self._get_tier_message(then),
                    "confidence": f"{cf*100:.0f}%",
                    "cf": cf,
                    "source": source,
                    "icon": self._get_tier_icon(then.get("market_position", ""))
                })
            elif cat == "Recruitment Strategy":
                explanations.append({
                    "rule_id": r["rule_id"],
                    "type": "strategy",
                    "title": f"Chiến lược: {then.get('strategy', 'Unknown')}",
                    "message": self._get_strategy_message(then),
                    "confidence": f"{cf*100:.0f}%",
                    "cf": cf,
                    "source": source,
                    "icon": "fas fa-bullseye"
                })
            elif cat == "Premium Role":
                explanations.append({
                    "rule_id": r["rule_id"],
                    "type": "premium",
                    "title": f"Vị trí cao cấp: {then.get('tier', 'Unknown')}",
                    "message": self._get_premium_message(then),
                    "confidence": f"{cf*100:.0f}%",
                    "cf": cf,
                    "source": source,
                    "icon": "fas fa-crown"
                })
            elif cat == "Anomaly":
                explanations.append({
                    "rule_id": r["rule_id"],
                    "type": "warning",
                    "title": "Cảnh báo bất thường",
                    "message": then.get("warning", ""),
                    "confidence": f"{cf*100:.0f}%",
                    "cf": cf,
                    "source": source,
                    "icon": "fas fa-exclamation-triangle"
                })
            elif cat == "Company Size":
                explanations.append({
                    "rule_id": r["rule_id"],
                    "type": "company",
                    "title": f"Công ty {then.get('characteristic', '')}",
                    "message": self._get_company_message(then),
                    "confidence": f"{cf*100:.0f}%",
                    "cf": cf,
                    "source": source,
                    "icon": "fas fa-building"
                })
            elif cat == "Meta":
                explanations.append({
                    "rule_id": r["rule_id"],
                    "type": "meta",
                    "title": "Khuyến nghị chung",
                    "message": then.get("general_advice", ""),
                    "confidence": f"{cf*100:.0f}%",
                    "cf": cf,
                    "source": source,
                    "icon": "fas fa-lightbulb",
                    "tips": then.get("salary_negotiation_tips", [])
                })
            else:
                explanations.append({
                    "rule_id": r["rule_id"],
                    "type": "general",
                    "title": cat,
                    "message": then.get("action", then.get("warning", "")),
                    "confidence": f"{cf*100:.0f}%",
                    "cf": cf,
                    "source": source,
                    "icon": "fas fa-info-circle"
                })

        return explanations

    def _get_tier_message(self, then):
        msg = f"Khuyến nghị thuộc **{then.get('tier', 'Unknown')}**"
        if then.get("salary_range"):
            msg += f"\nKhoảng lương: **${then['salary_range'][0]:,} - ${then['salary_range'][1]:,}**"
        if then.get("market_position"):
            msg += f"\nVị thế: **{then['market_position']}**"
        if then.get("action"):
            msg += f"\n\nHành động: {then['action']}"
        if then.get("warning"):
            msg += f"\n⚠️ {then['warning']}"
        return msg

    def _get_strategy_message(self, then):
        msg = f"**{then.get('strategy', 'Unknown')}**"
        if then.get("suggested_recruitment_time"):
            msg += f"\n⏱️ Thời gian tuyển: **{then['suggested_recruitment_time']}**"
        if then.get("suggested_bonus"):
            msg += f"\n💰 Signing bonus đề xuất: **{then['suggested_bonus']}**"
        if then.get("benefits_to_highlight"):
            benefits = ", ".join(then["benefits_to_highlight"])
            msg += f"\n✨ Benefits nên nhấn mạnh: **{benefits}**"
        if then.get("urgency"):
            msg += f"\n🚨 Độ khẩn: **{then['urgency']}**"
        return msg

    def _get_premium_message(self, then):
        msg = f"Vị trí: **{then.get('tier', 'Unknown')}**"
        if then.get("salary_range"):
            msg += f"\n💰 Khoảng lương: **${then['salary_range'][0]:,} - ${then['salary_range'][1]:,}**"
        if then.get("required_experience"):
            msg += f"\n📋 Exp yêu cầu: **{then['required_experience']}**"
        if then.get("action"):
            msg += f"\n💡 {then['action']}"
        return msg

    def _get_company_message(self, then):
        msg = f"**{then.get('characteristic', '')}**"
        if then.get("salary_adjustment"):
            msg += f"\n📊 Điều chỉnh lương: {then['salary_adjustment']}"
        if then.get("benefits_to_highlight"):
            benefits = ", ".join(then["benefits_to_highlight"])
            msg += f"\n✨ Benefits: **{benefits}**"
        return msg

    def _get_tier_icon(self, market_position):
        if "Top 5%" in str(market_position):
            return "fas fa-trophy"
        elif "Top 10%" in str(market_position):
            return "fas fa-medal"
        elif "Top 25" in str(market_position):
            return "fas fa-star"
        else:
            return "fas fa-signal"

    def _explain_salary(self, ml, tier):
        """Phân tích breakdown mức lương"""
        pred = ml.get("prediction", 0)
        lower = ml.get("confidence_lower", 0)
        upper = ml.get("confidence_upper", 0)
        mae = ml.get("mae", 37641)
        method = ml.get("method", "unknown")

        # Tính percentiles giả định
        return {
            "predicted": pred,
            "formatted": f"${pred:,}",
            "range": {
                "low": lower,
                "formatted_low": f"${lower:,}",
                "high": upper,
                "formatted_high": f"${upper:,}",
                "formatted": f"${lower:,} - ${upper:,}"
            },
            "mae": mae,
            "formatted_mae": f"${mae:,}",
            "accuracy_note": self._get_accuracy_note(mae, pred),
            "method": method,
            "tier_label": tier
        }

    def _get_accuracy_note(self, mae, prediction):
        pct = (mae / prediction) * 100 if prediction > 0 else 100
        if pct <= 15:
            return "Độ chính xác tốt"
        elif pct <= 25:
            return "Độ chính xác trung bình"
        else:
            return "Độ chính xác thấp, nên tham khảo khoảng rộng"

    def _explain_market_context(self, recommendation):
        """So sánh với thị trường"""
        ml = recommendation.get("ml_prediction", {})
        pred = ml.get("prediction", 0)
        facts = recommendation.get("engine_state", {}).get("working_memory_keys", {})

        # Benchmark
        market_avg = 136854  # Mean từ data
        market_median = 133000  # Median

        above_avg = pred > market_avg
        above_median = pred > market_median

        pct_vs_avg = ((pred - market_avg) / market_avg) * 100
        pct_vs_median = ((pred - market_median) / market_median) * 100

        return {
            "market_average": market_avg,
            "market_median": market_median,
            "vs_average": {
                "amount": pred - market_avg,
                "percent": round(pct_vs_avg, 1),
                "above": above_avg,
                "formatted": f"{'+' if above_avg else ''}{pct_vs_avg:.1f}%"
            },
            "vs_median": {
                "amount": pred - market_median,
                "percent": round(pct_vs_median, 1),
                "above": above_median,
                "formatted": f"{'+' if above_median else ''}{pct_vs_median:.1f}%"
            },
            "percentile_estimate": self._estimate_percentile(pred, market_avg, market_median),
            "market_summary": self._get_market_summary(pct_vs_median)
        }

    def _estimate_percentile(self, pred, avg, median):
        if pred >= avg * 1.5:
            return "Top 5%"
        elif pred >= avg * 1.25:
            return "Top 10%"
        elif pred >= avg:
            return "Top 25%"
        elif pred >= median:
            return "Top 50%"
        else:
            return "Below median"

    def _get_market_summary(self, pct_vs_median):
        if pct_vs_median >= 30:
            return "Mức lương rất cạnh tranh, thuộc nhóm cao của thị trường"
        elif pct_vs_median >= 10:
            return "Mức lương trên median thị trường"
        elif pct_vs_median >= -10:
            return "Mức lương around median thị trường"
        else:
            return "Mức lương dưới median thị trường"

    def _generate_action_items(self, recommendation):
        """Tạo action items cụ thể"""
        items = []

        # Actions từ rules
        for action in recommendation.get("actions", []):
            items.append({
                "type": "recruitment",
                "action": action,
                "priority": "high"
            })

        # Negotiation tips
        for tip in recommendation.get("negotiation_tips", []):
            items.append({
                "type": "negotiation",
                "action": tip,
                "priority": "medium"
            })

        # Benefits
        for benefit in recommendation.get("benefits_to_highlight", []):
            items.append({
                "type": "benefit",
                "action": f"Nhấn mạnh: {benefit}",
                "priority": "low"
            })

        # Warnings
        for warning in recommendation.get("warnings", []):
            items.append({
                "type": "warning",
                "action": warning,
                "priority": "high"
            })

        return items

    def _explain_confidence(self, recommendation):
        """Giải thích về confidence"""
        overall = recommendation.get("overall_confidence", 0)
        category_cf = recommendation.get("category_confidences", {})

        if overall >= 0.9:
            level = "Rất cao"
            note = "Hệ thống rất tự tin với khuyến nghị này"
        elif overall >= 0.8:
            level = "Cao"
            note = "Có thể tin tưởng vào khuyến nghị"
        elif overall >= 0.6:
            level = "Trung bình"
            note = "Nên tham khảo thêm nguồn khác"
        else:
            level = "Thấp"
            note = "Cần xem xét kỹ trước khi quyết định"

        return {
            "overall": overall,
            "level": level,
            "note": note,
            "by_category": {
                cat: {"cf": v["cf_combined"], "rules": v["rules_count"]}
                for cat, v in category_cf.items()
            }
        }

    def _generate_summary(self, recommendation, rules_explanation):
        """Tạo tóm tắt ngắn gọn"""
        ml = recommendation.get("ml_prediction", {})
        tier = recommendation.get("tier", "Unknown")
        pred = ml.get("prediction", 0)
        rules_count = recommendation.get("rules_fired_count", 0)
        warnings = recommendation.get("warnings", [])

        parts = [
            f"Hệ thống khuyến nghị mức lương **${pred:,}** cho vị trí thuộc nhóm **{tier}**.",
            f"Khuyến nghị này dựa trên **{rules_count} quy tắc** từ Knowledge Base."
        ]

        if warnings:
            parts.append(f"\n⚠️ **{len(warnings)} cảnh báo** cần lưu ý.")

        return "\n".join(parts)

    def format_for_display(self, explanation):
        """
        Format explanation để hiển thị trên web.
        Trả về HTML-friendly structured data.
        """
        return {
            "summary_html": self._markdown_to_html(explanation.get("summary", "")),
            "salary_display": {
                "main": f'<span class="text-success fw-bold">{explanation["salary_breakdown"]["formatted"]}</span>',
                "range": f'{explanation["salary_breakdown"]["range"]["formatted_low"]} - {explanation["salary_breakdown"]["range"]["formatted_high"]}',
                "mae_note": explanation["salary_breakdown"]["accuracy_note"]
            },
            "rules_display": [
                {
                    "icon": r["icon"],
                    "title": r["title"],
                    "message": self._markdown_to_html(r["message"]),
                    "confidence": r["confidence"],
                    "type": r["type"]
                }
                for r in explanation["rules_explanation"]
            ],
            "market_display": explanation["market_context"],
            "actions_display": explanation["action_items"],
            "confidence_display": explanation["confidence_narrative"]
        }

    def _markdown_to_html(self, text):
        """Convert markdown-like text to HTML"""
        if not text:
            return ""
        # Bold: **text**
        import re
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # Newlines
        text = text.replace('\n', '<br>')
        return text


def generate_explanation(recommendation):
    """Hàm tiện ích"""
    module = ExplanationModule()
    explanation = module.explain(recommendation)
    return {
        "explanation": explanation,
        "display": module.format_for_display(explanation)
    }