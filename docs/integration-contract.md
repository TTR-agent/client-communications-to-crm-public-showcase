# Integration Contract

This repo separates the operating note from the system write contract.

The action brief answers:

- What did the client say?
- What needs to happen next?
- Who owns it?

The integration plan answers:

- Which system should receive the update?
- Which object should be updated?
- Which fields should be mapped?
- What external ID prevents duplicate writes?
- What review gate must pass before mutation?

## Destination Identification

System names are normalized before routing:

- `Sales Force`, `salesforce`, and `sfdc` map to `salesforce`.
- `HubSpot` maps to `hubspot`.
- `Attio` maps to `attio`.
- `Gong.io` maps to `gong`.
- `Client Ops DB`, `database`, and `warehouse` map to `warehouse`.

## Object Mapping

| Destination | Object | Operation | Purpose |
| --- | --- | --- | --- |
| Salesforce | `opportunity` | `upsert` | Stage, next step, evidence summary |
| HubSpot | `deal` | `upsert` | Deal stage, next step, last-contact notes |
| Attio | `company` | `upsert` | Client status, next action, last signal |
| Generic CRM | `account` | `upsert` | Portable CRM example |
| Gong | `call_transcript` | `attach_note` | Call summary and follow-up items |
| Warehouse | `client_communication_event` | `insert` | Durable analytics/audit trail |

## Naming Conventions

- Objects use `singular_snake_case`.
- Internal fields use `snake_case`.
- CRM status values use `snake_case`.
- External IDs use `client_slug:communication_date:source`.
- Handoff keys use `team.reason.status`.

## Write Mode

The public demo uses `recommendation_only`. It builds payloads a writer could use, but does not write to Salesforce, HubSpot, Attio, Gong, or any database.

That boundary matters: a reviewer can see the payload contract without granting credentials or trusting hidden side effects.

