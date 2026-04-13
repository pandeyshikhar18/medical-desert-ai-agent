def calculate_score(f):
    score = 0

    if not f.equipment:
        score += 30
    if not f.capabilities:
        score += 20
    if not f.procedures:
        score += 10
    if not f.number_doctors:
        score += 20
    if not f.capacity:
        score += 10

    return min(100, score)

def severity(score):
    if score > 70:
        return "Severe"
    elif score > 40:
        return "Moderate"
    else:
        return "Low"

def apply_scores(facilities):
    for f in facilities:
        f.medical_desert_score = calculate_score(f)
    return facilities