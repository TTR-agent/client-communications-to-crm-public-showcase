# Integration Routing Plan

## Naming Conventions
- `objects`: `singular_snake_case`
- `fields`: `snake_case`
- `crm_status`: `snake_case`
- `external_id`: `client_slug:communication_date:source`
- `handoff_keys`: `team.reason.status`

## Planned Writes
- `salesforce` `upsert` `opportunity`
- `hubspot` `upsert` `deal`
- `attio` `upsert` `company`
- `generic_crm` `upsert` `account`
- `warehouse` `insert` `client_communication_event`
- `gong` `attach_note` `call_transcript`

## Review Gate
- mode: `recommendation_only`
- required_before_write: human approval, valid external ID, evidence present

