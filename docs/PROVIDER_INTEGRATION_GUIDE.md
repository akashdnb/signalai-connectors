# Provider Integration Guide

## Before coding

Confirm:

- the normalized capability already exists
- the provider is actually required
- the provider's terms and API limits are understood
- authentication ownership is clear
- webhook requirements are known
- rate and concurrency limits are documented

Do not create a provider-specific abstraction if an existing normalized interface already supports the requirement.

## Implementation checklist

### 1. Adapter

Implement only the provider-specific translation and protocol behavior.

### 2. Authentication

Support token acquisition/refresh using the platform's credential contract. Never hard-code credentials or expose tokens through logs/errors.

### 3. HTTP behavior

Use the shared resilient client. Configure:

- connect/read timeout
- retryable statuses
- provider rate limits
- maximum attempts
- circuit-breaker thresholds

### 4. Mapping

Map provider objects into normalized models. Preserve stable provider IDs.

### 5. Errors

Map known provider errors to the common error taxonomy. Unknown errors should retain enough provider metadata for diagnosis without leaking sensitive data.

### 6. Webhooks

Verify signatures before parsing business payloads. Deduplicate using provider event IDs when available.

### 7. Tests

Add:

- happy-path fixtures
- malformed payload tests
- authentication failures
- rate-limit tests
- timeout/provider outage tests
- duplicate webhook tests
- contract tests against normalized interfaces

## Operational readiness

Before enabling a provider in production, verify:

- health endpoint
- metrics and tracing
- credential refresh behavior
- rate-limit handling
- alerting
- rollback path
- provider documentation link/version
- known unsupported features

## Business logic boundary

Bad:

```text
Instagram adapter -> decide whether lead is qualified -> update CRM
```

Good:

```text
Instagram adapter -> normalized message/identity
                     |
                     v
             server capability
                     |
              CRM/journey rules
```

The connector should be replaceable without changing SignalAI product semantics.
