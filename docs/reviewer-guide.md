# Reviewer Guide

Review this repo like an operating-system sample, not a polished SaaS product.

What to inspect:

- `src/client_ops/normalize.py`: how unstructured inputs become a shared schema.
- `src/client_ops/analyze.py`: how client signals become actions, feedback loops, and CRM recommendations.
- `src/client_ops/route.py`: how work is routed across sales, marketing, engineering, and customer success.
- `src/client_ops/integrations.py`: how parsed notes become Salesforce, HubSpot, Attio, Gong, generic CRM, and warehouse write plans.
- `src/client_ops/render.py`: how the system produces human-readable handoff notes.
- `tests/test_client_ops.py`: the expected behavior and edge boundaries.

The important engineering idea is not the keyword rules themselves. In a production system those rules can be replaced or augmented by LLM extraction, structured parsers, or CRM-native workflows. The important part is the contract:

- evidence first
- owner-team next step
- CRM recommendation with reason
- destination-specific payload mapping
- naming conventions and external IDs
- feedback loop capture
- no blind write to CRM
