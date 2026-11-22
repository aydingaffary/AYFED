# ADR-003: Independent Laboratory Nodes

**Status:** Accepted
**Date:** 2026-11-22

## Context

Participating laboratories may differ in:

- Patient populations
- Measurement equipment
- Laboratory procedures
- Biomarker distributions
- Data quality
- Missing data patterns

These differences create statistical heterogeneity and non-IID data distributions.

A shared centralized training environment would not adequately represent the intended operational architecture.

## Decision

Each participating laboratory will operate an independent Laboratory Node.

Each node will maintain its own:

- Local data store
- Data normalization pipeline
- Training configuration
- Local training process
- Federated client
- Evaluation process
- Access policies
- Operational audit records

Raw laboratory training records must not be transferred to the Federated Coordinator.

The coordinator will manage federated training rounds and receive controlled model updates.

## Research Implementation

The initial research environment will simulate three independent laboratory nodes.

Each simulated node must have:

- An independently defined dataset partition.
- Its own configuration.
- An independent local training process.
- Independent local evaluation.
- A federated client communicating with the coordinator.

Logical isolation in a simulation must not be described as equivalent to security isolation in independently deployed infrastructures.

## Consequences

Positive:

- Supports realistic non-IID experiments.
- Enables laboratory-specific evaluation.
- Provides a foundation for FedAvg, FedProx, and Personalized FL.
- Preserves laboratory data boundaries in the target architecture.

Trade-offs:

- More complex orchestration.
- Additional configuration and monitoring.
- More demanding integration and testing.

## Future Review

Review node deployment, authentication, secure aggregation, and operational isolation before integrating real laboratories.
