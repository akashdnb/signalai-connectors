# SignalAI Connectors Architecture

## Purpose

`signalai-connectors` isolates external provider protocols from SignalAI product logic. It converts provider-specific APIs, webhooks, authentication and failure semantics into stable normalized interfaces consumed by `signalai-server` and `signalai-worker`.

The connector service is an integration boundary, not a product-domain service.

## Responsibilities

### In scope

- provider API clients
- provider authentication/token handling
- rate limits and provider retry policy
- provider request/response normalization
- webhook verification and normalization
- provider capability discovery
- provider health/circuit state
- provider-specific pagination and cursor handling
- provider error classification
- integration telemetry

### Out of scope

- CRM/business rules
- journey decisions
- lead lifecycle ownership
- conversation truth
- workspace authorization policy
- billing rules
- LLM reasoning
- MCP tool exposure

`signalai-server` remains the source of truth. Connectors return normalized results; the caller decides what those results mean to the product.

## Layering

```text
API / webhook transport
        |
Provider adapter
        |
Normalized connector interface
        |
Resilient HTTP client
        |
Provider API
```

Keep provider-specific details below the normalized interface.

## Provider adapter model

Each provider adapter should implement a small explicit capability interface rather than exposing the provider SDK throughout the codebase.

Examples:

- `MessagingProvider`
- `SocialAccountProvider`
- `ContactLookupProvider`
- `ResearchProvider`
- `WebhookProvider`

A provider may implement several capabilities. Do not force every provider into one giant interface.

## Authentication

Credentials are workspace/account scoped and must be supplied through the server-owned connected-account model. The connector may exchange/refresh credentials but must not become the source of truth for ownership or authorization.

Secrets must be encrypted at rest by the owning platform infrastructure and redacted from logs.

## Reliability

Provider calls require:

- bounded timeouts
- retry only for retryable failures
- exponential backoff
- rate-limit awareness
- circuit breaking for sustained provider failure
- idempotency where the provider supports it

Do not retry non-idempotent operations blindly.

## Normalization

Provider payloads should be translated into stable SignalAI-neutral objects. Preserve provider identifiers and provenance so the server can map the normalized object back to the connected account.

Never silently discard provider fields that may be needed for debugging or future compatibility; retain them as explicitly scoped metadata when appropriate.

## Webhooks

Webhook processing should:

1. verify provider signature
2. validate payload version/type
3. resolve connected account
4. normalize provider event
5. publish the normalized event to the server/worker boundary
6. acknowledge according to provider requirements

Webhook handlers must be idempotent because providers may redeliver events.

## Health

Expose operational health for:

- process
- provider configuration
- provider reachability
- authentication validity
- circuit state

Health failures should identify the affected provider/account class without leaking credentials.

## Adding a provider

1. identify the provider capability set
2. define/confirm normalized interface
3. implement adapter
4. map provider errors to stable error classes
5. implement auth/refresh handling
6. add rate-limit and retry rules
7. add contract tests with fixtures
8. add webhook verification if applicable
9. expose provider health
10. document limitations and unsupported capabilities

## Extraction rule

A provider integration belongs here when its complexity is primarily protocol/integration complexity. If logic decides a SignalAI business outcome, that logic belongs in the server capability/domain layer.
