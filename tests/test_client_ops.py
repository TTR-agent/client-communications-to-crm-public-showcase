from src.client_ops.analyze import analyze_threads
from src.client_ops.normalize import normalize_communications
from src.client_ops.render import render_action_brief, render_crm_updates
from src.client_ops.route import route_handoffs


def test_normalize_communications_keeps_public_safe_fields_only():
    raw = [
        {
            "source": "email",
            "from": "client@example.com",
            "speaker": "Client Lead",
            "body": "Need pricing and a migration owner before Friday.",
            "private_metadata": "never-keep-this",
            "thread_id": "private-thread-id",
        }
    ]

    normalized = normalize_communications(raw)

    assert normalized == [
        {
            "source": "email",
            "speaker": "Client Lead",
            "text": "Need pricing and a migration owner before Friday.",
            "timestamp": "",
        }
    ]


def test_analyze_threads_extracts_actions_feedback_and_crm_status():
    items = normalize_communications(
        [
            {
                "source": "call",
                "speaker": "Client Lead",
                "body": "We are ready for proposal if pricing is clarified.",
            },
            {
                "source": "notes",
                "speaker": "Engineer",
                "body": "Integration blocker: SSO requirements are unclear.",
            },
            {
                "source": "email",
                "speaker": "Client Lead",
                "body": "Feedback: onboarding felt too generic for our team.",
            },
        ]
    )

    analysis = analyze_threads(items)

    assert "proposal_requested" in analysis["signals"]
    assert "technical_blocker" in analysis["signals"]
    assert analysis["crm"]["recommended_status"] == "proposal_requested"
    assert analysis["actions"][0]["owner_team"] == "sales"
    assert any(item["team"] == "engineering" for item in analysis["handoffs"])
    assert any(item["type"] == "feedback" for item in analysis["feedback_loop"])


def test_route_handoffs_sends_work_to_right_teams():
    analysis = analyze_threads(
        normalize_communications(
            [
                {"source": "email", "speaker": "Client", "body": "Can you send case studies and pricing?"},
                {"source": "call", "speaker": "Client", "body": "Our API mapping is blocked."},
                {"source": "notes", "speaker": "AE", "body": "They asked for launch messaging support."},
            ]
        )
    )

    routed = route_handoffs(analysis)

    assert routed["sales"][0]["reason"] == "pricing_or_proposal"
    assert routed["engineering"][0]["reason"] == "technical_blocker"
    assert routed["marketing"][0]["reason"] == "proof_or_messaging"


def test_render_outputs_action_notes_and_crm_updates():
    analysis = analyze_threads(
        normalize_communications(
            [
                {"source": "call", "speaker": "Client", "body": "Ready for proposal after pricing."},
                {"source": "email", "speaker": "Client", "body": "Need customer proof and onboarding feedback captured."},
            ]
        )
    )

    action_brief = render_action_brief(analysis)
    crm_updates = render_crm_updates(analysis)

    assert "# Client Communication Action Brief" in action_brief
    assert "## Next Steps" in action_brief
    assert "## Team Handoffs" in action_brief
    assert "# CRM Status Change Recommendations" in crm_updates
    assert "proposal_requested" in crm_updates
