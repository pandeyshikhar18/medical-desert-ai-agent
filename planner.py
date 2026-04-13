def get_actions(f):
    if f.medical_desert_score > 70:
        return ["Immediate intervention", "Add doctors", "Provide equipment"]
    elif f.medical_desert_score > 40:
        return ["Improve capacity", "Verify claims"]
    else:
        return ["Stable facility"]

def planner_card(f):
    return {
        "actions": get_actions(f),
        "risk": f.medical_desert_score
    }