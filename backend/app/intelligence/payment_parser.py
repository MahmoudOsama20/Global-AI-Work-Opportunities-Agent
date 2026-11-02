import re
from typing import Optional, Dict, Any, Tuple

class PaymentParser:
    """Parses compensation, rates, budgets, and payment models accurately from listings."""

    CURRENCY_MAP = {
        "$": "USD",
        "usd": "USD",
        "€": "EUR",
        "eur": "EUR",
        "£": "GBP",
        "gbp": "GBP",
        "egp": "EGP",
        "le": "EGP",
    }

    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parses payment information.
        Returns a dict with:
        payment_model: str (hourly, fixed, per_task, monthly, not_disclosed)
        hourly_rate_min: float | None
        hourly_rate_max: float | None
        fixed_budget_min: float | None
        fixed_budget_max: float | None
        currency: str
        payment_details: str | None
        """
        result = {
            "payment_model": "not_disclosed",
            "hourly_rate_min": None,
            "hourly_rate_max": None,
            "fixed_budget_min": None,
            "fixed_budget_max": None,
            "currency": "USD",
            "payment_details": None,
        }

        if not text:
            return result

        # Detect currency
        for symbol, code in self.CURRENCY_MAP.items():
            if symbol in text.lower():
                result["currency"] = code
                break

        # 1. Hourly rate patterns: e.g. "$25 - $45 / hr", "$35/hour", "20 to 40 USD per hour"
        hourly_range = re.search(
            r"[$€£]?\s*(\d+(?:\.\d+)?)\s*(?:-|to)\s*[$€£]?\s*(\d+(?:\.\d+)?)\s*(?:/|\s*per\s*)\s*(?:hr|hour|h)\b",
            text,
            re.IGNORECASE,
        )
        if hourly_range:
            result["payment_model"] = "hourly"
            result["hourly_rate_min"] = float(hourly_range.group(1))
            result["hourly_rate_max"] = float(hourly_range.group(2))
            result["payment_details"] = f"{result['currency']} {result['hourly_rate_min']} - {result['hourly_rate_max']} per hour"
            return result

        hourly_single = re.search(
            r"[$€£]?\s*(\d+(?:\.\d+)?)\s*(?:/|\s*per\s*)\s*(?:hr|hour|h)\b",
            text,
            re.IGNORECASE,
        )
        if hourly_single:
            rate = float(hourly_single.group(1))
            # sanity check: rates above $500/hr are often annual salaries mistakenly written or typos
            if rate < 500:
                result["payment_model"] = "hourly"
                result["hourly_rate_min"] = rate
                result["hourly_rate_max"] = rate
                result["payment_details"] = f"{result['currency']} {rate} per hour"
                return result

        # 2. Per-task compensation: e.g. "$15 per task", "$2.50 per accepted submission"
        per_task = re.search(
            r"[\$€£]?\s*(\d+(?:\.\d+)?)\s*(?:/|\s*per\s*)(?:task|prompt|annotation|hit|item|accepted\s+task)\b",
            text,
            re.IGNORECASE,
        )
        if per_task:
            result["payment_model"] = "per_task"
            val = float(per_task.group(1))
            result["payment_details"] = f"{result['currency']} {val} per task"
            return result

        # 3. Monthly / Annual salary patterns: e.g. "$3,000 - $5,000 / month", "$80,000 / year"
        monthly_range = re.search(
            r"[\$€£]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:-|to)\s*[\$€£]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:/|\s*per\s*)(?:mo|month)\b",
            text,
            re.IGNORECASE,
        )
        if monthly_range:
            result["payment_model"] = "monthly"
            min_val = float(monthly_range.group(1).replace(",", ""))
            max_val = float(monthly_range.group(2).replace(",", ""))
            result["fixed_budget_min"] = min_val
            result["fixed_budget_max"] = max_val
            result["payment_details"] = f"{result['currency']} {min_val} - {max_val} per month"
            return result

        # 4. Fixed project budget: e.g. "Budget: $500", "Fixed price: $1,200"
        fixed_match = re.search(
            r"(?:budget|fixed\s*price|fixed\s*budget|est\.?\s*budget)\s*[:\-]?\s*[\$€£]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)",
            text,
            re.IGNORECASE,
        )
        if fixed_match:
            result["payment_model"] = "fixed"
            val = float(fixed_match.group(1).replace(",", ""))
            result["fixed_budget_min"] = val
            result["fixed_budget_max"] = val
            result["payment_details"] = f"{result['currency']} {val} fixed budget"
            return result

        # If keywords indicate hourly or fixed without exact numbers
        if re.search(r"\bhourly\b", text, re.IGNORECASE):
            result["payment_model"] = "hourly"
            result["payment_details"] = "Hourly (rate not disclosed)"
        elif re.search(r"\bfixed[- ]price\b", text, re.IGNORECASE):
            result["payment_model"] = "fixed"
            result["payment_details"] = "Fixed price (budget not disclosed)"
        elif re.search(r"\bper[- ]task\b", text, re.IGNORECASE):
            result["payment_model"] = "per_task"
            result["payment_details"] = "Per task (rate not disclosed)"

        return result
