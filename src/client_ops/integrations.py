SYSTEM_ALIASES = {
    "sales force": "salesforce",
    "salesforce": "salesforce",
    "sfdc": "salesforce",
    "hubspot": "hubspot",
    "attio": "attio",
    "crm": "generic_crm",
    "gong": "gong",
    "gong.io": "gong",
    "database": "warehouse",
    "warehouse": "warehouse",
    "client ops db": "warehouse",
}

NAMING_CONVENTIONS = {
    "objects": "singular_snake_case",
    "fields": "snake_case",
    "crm_status": "snake_case",
    "external_id": "client_slug:communication_date:source",
    "handoff_keys": "team.reason.status",
}

DESTINATION_CONTRACTS = {
    "salesforce": {
        "object": "opportunity",
        "operation": "upsert",
        "id_field": "external_account_key",
        "field_map": {
            "StageName": "recommended_status",
            "NextStep": "next_step_summary",
            "Description": "evidence_summary",
        },
    },
    "hubspot": {
        "object": "deal",
        "operation": "upsert",
        "id_field": "external_account_key",
        "field_map": {
            "dealstage": "recommended_status",
            "next_step": "next_step_summary",
            "notes_last_contacted": "evidence_summary",
        },
    },
    "attio": {
        "object": "company",
        "operation": "upsert",
        "id_field": "external_account_key",
        "field_map": {
            "client_status": "recommended_status",
            "next_action": "next_step_summary",
            "last_client_signal": "evidence_summary",
        },
    },
    "generic_crm": {
        "object": "account",
        "operation": "upsert",
        "id_field": "external_account_key",
        "field_map": {
            "client_status": "recommended_status",
            "next_step": "next_step_summary",
            "last_signal": "evidence_summary",
        },
    },
    "gong": {
        "object": "call_transcript",
        "operation": "attach_note",
        "id_field": "call_external_id",
        "field_map": {
            "call_summary": "evidence_summary",
            "follow_up_items": "next_step_summary",
            "crm_status_recommendation": "recommended_status",
        },
    },
    "warehouse": {
        "object": "client_communication_event",
        "operation": "insert",
        "id_field": "event_external_id",
        "field_map": {
            "source": "source",
            "speaker": "speaker",
            "text": "text",
            "detected_signals": "signals",
            "recommended_status": "recommended_status",
        },
    },
}


def normalize_system_name(name):
    return SYSTEM_ALIASES.get(name.strip().lower(), name.strip().lower().replace(" ", "_"))


def build_integration_plan(analysis, communications, requested_systems=None):
    systems = requested_systems or _infer_destinations(analysis, communications)
    writes = []
    for system in systems:
        normalized = normalize_system_name(system)
        contract = DESTINATION_CONTRACTS[normalized]
        writes.append(_build_write(normalized, contract, analysis, communications))

    return {
        "naming_conventions": NAMING_CONVENTIONS,
        "writes": writes,
        "review_gate": {
            "mode": "recommendation_only",
            "required_before_write": ["human_approval", "valid_external_id", "evidence_present"],
        },
    }


def _infer_destinations(analysis, communications):
    destinations = ["salesforce", "hubspot", "attio", "generic_crm", "warehouse"]
    if any(item["source"] == "call" for item in communications):
        destinations.append("gong")
    return destinations


def _build_write(system, contract, analysis, communications):
    return {
        "destination": system,
        "object": contract["object"],
        "operation": contract["operation"],
        "id_field": contract["id_field"],
        "external_id": _external_id(communications),
        "field_map": contract["field_map"],
        "payload": _payload_for(contract, analysis, communications),
    }


def _payload_for(contract, analysis, communications):
    summary = _evidence_summary(analysis)
    next_steps = "; ".join(action["next_step"] for action in analysis["actions"])
    first = communications[0] if communications else {"source": "", "speaker": "", "text": ""}
    values = {
        "recommended_status": analysis["crm"]["recommended_status"],
        "next_step_summary": next_steps,
        "evidence_summary": summary,
        "source": first["source"],
        "speaker": first["speaker"],
        "text": first["text"],
        "signals": ", ".join(analysis["signals"]),
    }
    return {target: values[source] for target, source in contract["field_map"].items()}


def _evidence_summary(analysis):
    lines = []
    for signal, evidence_items in analysis["evidence"].items():
        lines.append(f"{signal}: {evidence_items[0]}")
    return " | ".join(lines)


def _external_id(communications):
    if not communications:
        return "demo-client:unknown-date:generated"
    first = communications[0]
    date = first.get("timestamp", "")[:10] or "unknown-date"
    source = first.get("source", "unknown")
    return f"demo-client:{date}:{source}"
