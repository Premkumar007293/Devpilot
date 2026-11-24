# Feedback System

## Purpose
The beta feedback system captures user-reported bugs, feature requests, and analysis-quality issues without exposing source code or secrets.

## Supported fields
- Feedback category
- Description
- Optional repository reference
- Optional related resource type/id
- Submission timestamp
- Status

## Privacy rules
- Do not include credentials, tokens, or raw secrets.
- Do not store repository source code in the feedback payload.
- Do not upload private code automatically.
- Allow users to review what they submitted before sending it.

## API
- `GET /api/v1/feedback` — list feedback submitted by the current authenticated user
- `POST /api/v1/feedback` — create a new feedback entry
- `GET /api/v1/feedback/{feedback_id}` — fetch a single item

## Frontend usage
The Settings page includes a lightweight beta feedback form for reporting issues or suggestions.

## Operational guidance
- Review submissions during the beta period.
- Classify into bug, usability, feature request, analysis-quality, or general feedback.
- Track status values such as `new`, `triaged`, `in_progress`, and `resolved`.
