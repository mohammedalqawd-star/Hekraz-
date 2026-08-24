# Tool Contract

A CyberGuard tool is considered real only when its handler performs the documented operation and records the result.

## Required fields
- `id`
- `name`
- `category`
- `description`
- `purpose`
- `requirements`
- `lab_only` or `authorized_scope`
- `handler`
- `result_schema`

## Result states
- `SUCCESS`: operation executed and produced a result.
- `NO_DATA`: operation executed but no data was available.
- `UNAVAILABLE`: dependency is not installed/configured.
- `DENIED`: authorization or scope check failed.
- `ERROR`: operation failed; the error is logged.

The UI must never report `SUCCESS` for an operation that was not actually executed.
