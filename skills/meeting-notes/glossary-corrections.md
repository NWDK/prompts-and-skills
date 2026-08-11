# Glossary Corrections — meeting transcripts

Common misspellings, mishearings, and artifacts your AI transcriber produces. Apply these during Step 2 cleanup. This file holds **corrections only** — point at your own people/product/terminology reference for anything not listed here.

> **Customize this file for your own context.** Transcribers reliably mangle the same proper nouns every time — names, product names, tools, jargon, fonts. List the ones yours gets wrong, with the correction and (optionally) a note on when it happens. Build it up over time: every time you catch a new mangling, add a row.

## Pattern + examples

### People
| Transcriber variant | Correct |
|---|---|
| `Sean` (when the person is `Shaun`) | `Shaun` — a name the transcriber reliably hears as a more common spelling |
| `Jon` / `Jonny` | `[teammate's correct name]` |
| `B` (single letter when context is a person) | the person whose name starts with B — some transcribers collapse short names to a letter |

### Tools / products
| Transcriber variant | Correct |
|---|---|
| `CL` / `Cloud` (when context is the AI) | `Claude` — transcribers garble "Claude" to "CL" / "Cloud" / fragments |
| `Codeex` / `code-x` | `Codex` |
| `[product mishearing]` | `[Your Product Name]` |

### Fonts / jargon
| Transcriber variant | Correct |
|---|---|
| `[font name mangled]` | `[your font name]` (watch for weight-suffix mangling, e.g. "400") |
| `[internal term mangled]` | `[your term]` |

### How to use this
- Apply as straight find-replace during cleanup, mindful of context (don't replace "cloud" when it genuinely means cloud storage).
- When uncertain, leave the original and flag `[possible mishearing]` for the user.
- Keep adding rows — the file pays for itself after a few transcripts.
