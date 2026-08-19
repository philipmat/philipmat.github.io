---
layout: post
title: "TIL: bash command tracing at function level"
tags: [til, bash, tracing, best-practices]
snippet: "Enable bash xtrace (-x) for just one function using '{ local -; set -x; } 2>/dev/null' so tracing is visible inside the function, restored for the caller, and initial noise is suppressed."
---

```sh
some-function () {
  { local -; set -x; } 2>/dev/null
   some-command "$@"
}
```

`{ local -; set -x; } 2>/dev/null` enables `set -x` (command tracing/xtrace) for just this function, without leaking that setting to the caller.

As a result, `some-command "$@"` runs with full `-x` tracing visible (since the redirect only applies to the group, not to the rest of the function), and the moment the function returns, xtrace (and any other option) reverts to whatever the caller had. The debug tracing is scoped to just this one function, with no side effects on the rest of the script.

Breaking it down:

- **`local -`**: `local` inside a function, given just `-`, saves the current shell option flags (everything `set -o` would show) into a function-local scope. When the function returns, bash restores the shell options to whatever they were before the function was called. `-` is treated as a special variable name by `local` specifically for this purpose.

- **`set -x`**: turns on xtrace, so every command executed afterward gets printed to stderr prefixed with `+`, showing exactly what's running with expanded variables. This is normally a global, persistent setting.

- **`{ ... } 2>/dev/null`**: the group command wraps both statements so the `2>/dev/null` applies to both. This suppresses the trace output that `set -x` itself would otherwise immediately produce (bash echoes the `set -x` command's own invocation), and suppresses any noise from `local -`. Without this redirect we would see stray `+ local -` / `+ set -x` lines in stderr before our actual tracing starts.
