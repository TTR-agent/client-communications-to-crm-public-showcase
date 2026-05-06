SIGNAL_RULES = {
    "proposal_requested": ("proposal", "pricing", "commercial terms", "ready to move"),
    "technical_blocker": ("blocked", "blocker", "api", "integration", "sso", "data mapping"),
    "customer_proof_needed": ("case study", "case studies", "reference", "proof", "roi"),
    "onboarding_feedback": ("feedback", "onboarding", "confusing", "generic", "handoff"),
    "launch_or_messaging": ("launch", "messaging", "announcement", "positioning"),
}

TEAM_BY_SIGNAL = {
    "proposal_requested": "sales",
    "technical_blocker": "engineering",
    "customer_proof_needed": "marketing",
    "onboarding_feedback": "customer_success",
    "launch_or_messaging": "marketing",
}

REASON_BY_SIGNAL = {
    "proposal_requested": "pricing_or_proposal",
    "technical_blocker": "technical_blocker",
    "customer_proof_needed": "proof_or_messaging",
    "onboarding_feedback": "client_feedback",
    "launch_or_messaging": "proof_or_messaging",
}


def analyze_threads(communications):
    signals = []
    evidence_by_signal = {}

    for item in communications:
        text = item["text"].lower()
        for signal, keywords in SIGNAL_RULES.items():
            if any(keyword in text for keyword in keywords):
                if signal not in signals:
                    signals.append(signal)
                evidence_by_signal.setdefault(signal, []).append(item["text"])

    actions = [_action_for_signal(signal, evidence_by_signal[signal][0]) for signal in signals]
    handoffs = [_handoff_for_signal(signal, evidence_by_signal[signal][0]) for signal in signals]
    feedback_loop = _feedback_loop(signals, evidence_by_signal)
    crm = _crm_recommendation(signals)

    return {
        "signals": signals,
        "actions": actions,
        "handoffs": handoffs,
        "feedback_loop": feedback_loop,
        "crm": crm,
        "evidence": evidence_by_signal,
    }


def _action_for_signal(signal, evidence):
    team = TEAM_BY_SIGNAL[signal]
    action_by_signal = {
        "proposal_requested": "Clarify pricing, package next step, and send proposal-ready summary.",
        "technical_blocker": "Confirm technical owner, unblock requirements, and define integration path.",
        "customer_proof_needed": "Attach relevant proof, case study, or reference narrative.",
        "onboarding_feedback": "Convert feedback into onboarding improvement and client-facing recovery note.",
        "launch_or_messaging": "Prepare launch/messaging support and assign content owner.",
    }
    return {"owner_team": team, "next_step": action_by_signal[signal], "evidence": evidence}


def _handoff_for_signal(signal, evidence):
    return {
        "team": TEAM_BY_SIGNAL[signal],
        "reason": REASON_BY_SIGNAL[signal],
        "evidence": evidence,
        "handoff_note": f"Review client signal `{signal}` and confirm owner, deadline, and closure criteria.",
    }


def _feedback_loop(signals, evidence_by_signal):
    loop = []
    for signal in signals:
        if signal in {"onboarding_feedback", "technical_blocker", "customer_proof_needed"}:
            loop.append(
                {
                    "type": "feedback",
                    "source_signal": signal,
                    "learning": evidence_by_signal[signal][0],
                    "process_update": "Add this pattern to future qualification, onboarding, or handoff checks.",
                }
            )
    return loop


def _crm_recommendation(signals):
    if "proposal_requested" in signals:
        status = "proposal_requested"
        reason = "Client asked for pricing/proposal movement."
    elif "technical_blocker" in signals:
        status = "technical_review"
        reason = "Client progress depends on engineering clarification."
    elif "customer_proof_needed" in signals:
        status = "proof_requested"
        reason = "Client needs confidence material before advancing."
    else:
        status = "active_follow_up"
        reason = "There is communication activity but no closing-stage trigger."

    return {
        "recommended_status": status,
        "reason": reason,
        "write_mode": "recommendation_only",
    }

