# Failed mutations

Use this whenever a Quandora tool that creates, submits, starts, controls or changes something
returns an error. The error's `error.details` may carry two fields:

- `mutation_outcome`: `committed` or `unknown`.
- `confirm_with`: the read tools that show whether the mutation took effect. The list in the
  error is the authority; use those tools, not a different read.

## The three cases

1. `mutation_outcome: committed`: do not repeat the call. Read with `confirm_with` and continue
   from what the read shows.
2. `mutation_outcome: unknown`: read with `confirm_with` first. Only if the read shows no effect,
   repeat the identical call (same arguments) once, within ten minutes of the first attempt.
3. Neither field: the request was refused. Follow `retryable` and the error's other details.

## What makes a repeat safe

- Create and submit tools: an identical call inside ten minutes of the first resolves to the same
  operation and cannot create a duplicate. A changed argument, or the same call after ten
  minutes, is a new operation.
- Controls and setters (pause, resume, stop, favorites, moves, renames, archive/restore) are a
  new operation on every call and are safe to repeat.
- No tool accepts an idempotency key. Where a tool has a `client_request_id` argument, choose it
  before the first call and send the same value with the same arguments for the same intent.

## Edges

- More specific recovery details in the same error or result (`recovery_action`, `next_action`,
  `acceptance_state`, `run_id`) come first; the owning Skill explains them.
- `mutation_outcome` without `confirm_with`: no read confirms that tool. `committed` is done;
  for `unknown`, repeat the identical call once within ten minutes.
- No response at all (host timeout, dropped connection): treat it as `unknown` and read with the
  tool the owning Skill names for that object.
- If the read still shows no effect after ten minutes, do not repeat on your own: report what the
  read shows and let the user decide.
- Never change arguments, create a replacement object, or pick a merely similar object as proof.
