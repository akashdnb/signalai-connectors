# Connector Contracts

## Contract principles

Connector interfaces must be provider-neutral, typed, explicit about capabilities and stable across provider implementations.

A normalized operation should answer: what SignalAI needs to do, not how a provider happens to expose it.

## Request context

Every operation should carry enough context to correlate and authorize the request:

```json
{
  "workspaceId": "ws_123",
  "connectedAccountId": "acct_123",
  "requestId": "req_123",
  "correlationId": "corr_123"
}
```

Authorization remains owned by `signalai-server`; connector authentication proves access to the external provider.

## Normalized result

Prefer structured results:

```json
{
  "provider": "instagram",
  "connectedAccountId": "acct_123",
  "providerObjectId": "123456",
  "status": "SUCCESS",
  "data": {},
  "metadata": {}
}
```

## Error taxonomy

Map provider errors into stable categories:

- `AUTHENTICATION_FAILED`
- `AUTHORIZATION_FAILED`
- `RATE_LIMITED`
- `VALIDATION_FAILED`
- `NOT_FOUND`
- `CONFLICT`
- `PROVIDER_UNAVAILABLE`
- `TIMEOUT`
- `UNSUPPORTED_CAPABILITY`
- `UNKNOWN_PROVIDER_ERROR`

Include provider error codes as metadata where useful, but callers should not need provider-specific codes to decide whether a retry is safe.

## Retry semantics

The connector must classify whether a request is retryable. Callers should not guess from HTTP status alone.

A normalized error should include:

```json
{
  "code": "RATE_LIMITED",
  "retryable": true,
  "retryAfterSeconds": 30
}
```

## Messaging contract direction

Messaging operations should eventually support normalized operations such as:

- send message
- fetch conversation
- fetch messages
- mark/read state where supported
- resolve account identity

Provider-specific message formats remain inside adapters.

## Research contract direction

Research providers should return structured facts with provenance, confidence where available, source references and timestamps. The connector must not present model-generated guesses as verified provider facts.

## Compatibility

Breaking changes require a new contract version. Provider adapters may evolve independently as long as they continue implementing the normalized interface.

Contract tests must run against every provider implementation before release.
