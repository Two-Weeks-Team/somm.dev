PASS_THRESHOLD = 70
CONCERNS_THRESHOLD = 50
COVERAGE_THRESHOLD = 0.5


def get_quality_gate(normalized_score: float, coverage_rate: float) -> str:
    if coverage_rate < COVERAGE_THRESHOLD:
        return "INCOMPLETE"
    if normalized_score >= PASS_THRESHOLD:
        return "PASS"
    if normalized_score >= CONCERNS_THRESHOLD:
        return "CONCERNS"
    return "FAIL"
