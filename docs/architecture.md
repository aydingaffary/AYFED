# AYFED — System Architecture

**Document:** Architecture Specification
**Version:** 0.1.0
**Status:** Initial Design
**Project:** AYFED — Personalized Health Intelligence

## 1. Architectural Vision

AYFED is a privacy-conscious health intelligence platform designed to help individuals organize, understand, and monitor their longitudinal laboratory results.

The platform also provides infrastructure for collaborative machine learning across independent laboratories through Federated Learning (FL), without requiring the central collection of raw laboratory training data.

The architecture follows three principles:

- Personal Health Intelligence
- Laboratory Independence
- Privacy-Preserving Collaboration

## 2. High-Level Architecture

AYFED consists of five major components:

1. Personal Health Platform
2. AYFED Cloud Platform
3. Laboratory Infrastructure
4. Federated Learning Infrastructure
5. Security, Privacy, and Governance

## 3. Personal Health Platform

The Personal Health Platform provides user-facing health services.

Responsibilities:

- User registration and authentication
- Personal health profile management
- Blood test report upload
- Laboratory report extraction and validation
- Longitudinal laboratory history
- Biomarker trend visualization
- Personalized health information
- User consent management

Core health services must remain available independently of the Federated Learning infrastructure.

## 4. AYFED Cloud Platform

The cloud platform provides shared application services.

Responsibilities:

- API services
- User and laboratory account management
- Structured health data management
- Laboratory result normalization
- Biomarker reference range management
- Longitudinal analysis
- Report generation
- Model distribution and version management
- Audit and access management

The initial backend architecture follows a Modular Monolith approach.

## 5. Laboratory Infrastructure

Each participating laboratory operates an independent Laboratory Node.

A Laboratory Node is responsible for:

- Local data integration
- Laboratory-specific normalization
- Local data storage
- Data quality validation
- Local model training
- Federated client execution
- Local model evaluation
- Operational monitoring and auditing

Raw laboratory training records remain within the laboratory's controlled environment.

Each node must have independent configuration, access policies, and local data boundaries.

## 6. Federated Learning Infrastructure

The Federated Learning infrastructure enables participating laboratories to collaboratively train machine learning models.

Main components:

- Federated Coordinator
- Federated Clients
- Model Registry
- Aggregation Strategies
- Model Evaluation
- Training Round Management

Initial research strategies:

- FedAvg
- FedProx
- Personalized Federated Learning

The architecture must support heterogeneous and non-IID data distributions.

The coordinator receives controlled model updates rather than raw laboratory training records.

Federated Learning alone does not guarantee privacy. Additional mechanisms such as Secure Aggregation and Differential Privacy must be evaluated according to the threat model.

## 7. Data Architecture

AYFED distinguishes between three categories of data.

### 7.1 Personal Health Data

Examples:

- Personal health profile
- Laboratory observations
- Historical test results
- Biomarker trends
- User-approved reports

### 7.2 Laboratory Operational Data

Examples:

- Laboratory metadata
- Measurement methods
- Equipment information
- Reference ranges
- Data quality information

### 7.3 Federated Training Data

Examples:

- Locally prepared training datasets
- Local model parameters
- Model evaluation results
- Federated training metadata

These categories must have separate access policies, purposes, and retention rules.

Uploading a laboratory report does not constitute consent to use its data for Federated Learning.

## 8. Laboratory Report Processing Pipeline

The initial blood test processing pipeline consists of:

1. Report ingestion
2. PDF or image processing
3. OCR and text extraction
4. Structured result extraction
5. User verification
6. Biomarker identification
7. Unit normalization
8. Laboratory-specific reference range association
9. Data validation
10. Storage and longitudinal analysis

### 8.1 OCR Deployment

For the initial MVP, OCR and extraction are performed by a controlled server-side service.

The original report should preferably remain on the user's device. When server-side processing is selected, a temporary copy is transmitted securely for processing.

Temporary files must be protected by access controls and deleted according to a defined retention policy.

The architecture must allow future migration to on-device OCR and extraction.

### 8.2 Healthcare Standards

The system should use established healthcare interoperability standards:

- FHIR R4 for healthcare data exchange
- LOINC for laboratory observation identification
- UCUM for standardized measurement units

## 9. Data Storage Architecture

AYFED follows a Hybrid, Local-first storage approach.

- Original laboratory reports: preferably retained on the user's device.
- Temporary OCR copies: stored only as necessary for processing.
- Structured laboratory observations: stored in encrypted cloud infrastructure.
- Longitudinal history: available through authorized cloud services.
- Laboratory training records: retained within each laboratory's environment.
- Federated model updates: transmitted through controlled federated infrastructure.

Cloud storage of structured observations requires explicit access policies, encryption, and data retention controls.

## 10. Machine Learning Architecture

The machine learning architecture separates local model development from federated collaboration.

Initial research configurations:

- Local Training
- Centralized Training as a research baseline, where legally and ethically permitted
- Federated Averaging (FedAvg)
- Federated Proximal (FedProx)
- Personalized Federated Learning

Evaluation must consider:

- Predictive performance
- Performance across laboratories
- Non-IID robustness
- Model calibration
- Communication overhead
- Training efficiency
- Model stability under distribution shift
- Privacy risks

Clinical prediction tasks require appropriately validated outcome labels. Laboratory measurements alone must not be treated as sufficient evidence of a clinical diagnosis.

## 11. Security, Privacy, and Governance

Security and privacy are cross-cutting architectural concerns.

Required capabilities include:

- Encryption in transit and at rest
- Authentication and authorization
- Role-based access control
- Explicit and purpose-specific user consent
- Consent withdrawal
- Audit logging
- Restricted service-to-data access
- Secure model update transmission
- Data retention and deletion policies
- Protection against unauthorized model update access

OCR services must access only the files necessary for processing. Sensitive health information must not be exposed through application logs.

Consent for health data storage and consent for Federated Learning participation must be handled separately.

## 12. Software Architecture and Technology Direction

The initial software architecture follows a Modular Monolith approach for the main application.

The following components are designed for independent deployment when required:

- Personal Health Application
- Laboratory Node
- Federated Coordinator

Initial technology direction:

- Python
- FastAPI
- PostgreSQL
- React
- PyTorch
- Flower
- Docker

Technology choices and supported versions will be validated before implementation.

## 13. Initial Scope and Constraints

The first version focuses on:

- Blood test reports
- Personal health profiles
- Structured laboratory observations
- Longitudinal result tracking
- Basic biomarker analysis
- Simulated Federated Learning across independent laboratory nodes

The initial version will not provide:

- Autonomous medical diagnosis
- Medication prescriptions
- Treatment decisions
- Unvalidated disease prediction
- Production deployment across real laboratories

## 14. Research Environment

The initial research environment will simulate three independent laboratory nodes.

Each node will have its own:

- Dataset partition
- Configuration
- Local training process
- Evaluation process
- Federated client

The simulation must preserve logical isolation between nodes.

This experimental isolation must not be presented as equivalent to security isolation between independently deployed real-world infrastructures.

## 15. Architectural Evolution

The architecture will evolve through these stages:

1. Foundation and data modeling
2. Laboratory report ingestion
3. Personal health intelligence
4. Federated Learning simulation
5. Personalization and privacy enhancements
6. Evaluation and research validation
7. Controlled real-world integration

Material architectural changes affecting system boundaries, data ownership, security, or research methodology must be documented through Architecture Decision Records (ADRs).
