TEAMS = ("sales", "marketing", "engineering", "customer_success")


def route_handoffs(analysis):
    routed = {team: [] for team in TEAMS}
    for handoff in analysis["handoffs"]:
        routed[handoff["team"]].append(
            {
                "reason": handoff["reason"],
                "evidence": handoff["evidence"],
                "handoff_note": handoff["handoff_note"],
            }
        )
    return routed

