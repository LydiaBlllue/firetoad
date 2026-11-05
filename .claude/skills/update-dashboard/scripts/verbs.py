"""verbs.py — the one shape every script's run() returns, so a second front door can call it.

Each of the scripts a month goes through (status, update, confirm, rebuild, propose, scaffold)
used to be a main() that parsed arguments, did the work and printed as it went. The work and
the printing are now apart: `run(root, ..., say=None) -> dict` does the work and returns

    {"rc": <the exit code main() returns>, "lines": [<every line the CLI prints, in order>], ...}

plus the script's own structured result (the same keys its --json prints). `main()` parses the
arguments, calls run() with `say=print`, and prints the JSON when asked. A caller that is not a
terminal — a local server drawing a panel — calls run() and gets the lines for its progress view
and the result for its page, from the same code path, so the two doors cannot drift.

Nothing here decides anything about money: it only carries lines.
"""


def speaker(say=None, loud=None):
    """(emit, lines). emit(text, loud=False) records the line and hands it on: to `say` normally,
    to `loud` when the line has to reach the terminal even in --json mode (a refusal, a failure)
    — the CLI passes print for both, or print for loud alone when printing JSON."""
    lines = []

    def emit(text="", *, loud_line=False):
        lines.append(text)
        cb = loud if loud_line and loud is not None else say
        if cb is not None:
            cb(text)
    return emit, lines


def result(summary, rc, lines):
    """The dict run() returns: the script's own result first, then rc and lines."""
    out = dict(summary)
    out["rc"] = rc
    out["lines"] = lines
    return out


def public(res):
    """What --json prints: the result without rc and lines (the shape it printed before run())."""
    return {k: v for k, v in res.items() if k not in ("rc", "lines")}
