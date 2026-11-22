# ADR-001: Server-Side OCR for the Initial MVP

**Status:** Accepted
**Date:** 2026-11-22

## Context

AYFED must extract structured laboratory observations from PDF and image-based blood test reports.

On-device OCR offers privacy advantages but introduces additional implementation and compatibility complexity during the initial development stage.

## Decision

The initial MVP will use controlled server-side OCR and structured extraction.

The architecture must preserve the option to migrate OCR and extraction to on-device processing in a future version.

The original report should preferably remain on the user's device. If server-side OCR is selected, a temporary copy will be securely transmitted for processing.

## Security Requirements

- HTTPS/TLS for file transmission.
- Encryption at rest for temporary files.
- Restricted access to OCR processing services.
- No sensitive health information in application logs.
- Defined retention and deletion policies.
- Authentication and authorization for file access.
- No use of uploaded reports for Federated Learning without separate consent.

## Consequences

Positive:

- Simpler initial implementation.
- Centralized control over OCR processing.
- Easier integration with the initial backend.

Trade-offs:

- Health documents temporarily leave the user's device.
- Server-side processing increases privacy and security responsibilities.
- A future on-device processing implementation may be required.

## Future Review

Reassess the decision when on-device OCR becomes technically practical or privacy requirements change.
