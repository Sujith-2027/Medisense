from config import BLOCKED_DRUGS

def filter_response(response: dict) -> dict:
    """Remove blocked/prescription drugs from OTC suggestions."""
    raw_otc  = response.get("otc", [])
    safe_otc = []

    for item in raw_otc:
        is_blocked = any(drug in item.lower() for drug in BLOCKED_DRUGS)
        if not is_blocked:
            safe_otc.append(item)

    warnings = list(response.get("warning", []))
    if len(safe_otc) < len(raw_otc):
        warnings.append(
            "Some medication suggestions were removed. "
            "Only use medications prescribed or recommended by your doctor."
        )

    response["otc"]     = safe_otc
    response["warning"] = warnings
    return response