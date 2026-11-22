# ADR-002: Hybrid Local-First Data Storage

**Status:** Accepted
**Date:** 2026-11-22

## Context

AYFED must support longitudinal laboratory history while minimizing unnecessary exposure of original health documents.

A purely local architecture would complicate synchronization and cross-device access.

A purely cloud-based architecture would increase the amount of sensitive information centrally stored.

## Decision

AYFED will follow a Hybrid, Local-first storage architecture.

- Original PDF and image reports should preferably remain on the user's device.
- Temporary copies may be transmitted to the OCR service when necessary.
- Structured laboratory observations may be synchronized with encrypted cloud infrastructure.
- Longitudinal health history will be accessible through authorized cloud services.
- Laboratory training records will remain within laboratory-controlled environments.

## Security and Governance Requirements

- Encryption in transit and at rest.
- Purpose-specific access control.
- User-controlled synchronization where practical.
- Explicit consent for data processing.
- Defined retention and deletion policies.
- Separate consent for Federated Learning participation.

## Consequences

Positive:

- Supports longitudinal health services.
- Reduces unnecessary central storage of original documents.
- Enables authorized access across devices.

Trade-offs:

- Requires secure synchronization.
- Requires clear ownership and retention policies.
- Cloud storage still introduces privacy and security responsibilities.

## Future Review

Review the storage model when implementing multi-device synchronization, backup, and user-controlled data export and deletion.
