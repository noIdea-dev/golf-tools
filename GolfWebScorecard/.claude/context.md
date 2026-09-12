# Project: GolfWebScorecard

**Created:** 2026-09-12
**Last Updated:** 2026-09-12
**Iterations:** 1

## Project Overview

A collection of browser-based golf tools served as static HTML. No build step, no backend — pure HTML/CSS/JS. Lives at `/Users/m4/Development/Golf Stuff/GolfWebScorecard/`. GitHub: `drgreenland/golf-tools` (private).

Primary tools:
- **Scorecard builder** — single-round scorecard entry and export
- **EzyGolfer Recovery** — multi-round entry for EzyGolfer data recovery; exports EzyGolfer backup JSON

## Current Status

- **EzyGolfer Recovery section:** Complete and verified. Multi-round entry with localStorage persistence, Lombok Kosaido par row, export as EzyGolfer backup JSON, Clear All Rounds with confirmation. 43 rounds successfully recovered via this tool.
- **Latest commit:** `33056d0` — 2026-09-12

## Development History

### Iteration 1 - 2026-09-12
- **Goal:** Build multi-round EzyGolfer recovery tool for re-entering 15+ lost rounds
- **Changes:** `index.html` — full EzyGolfer Recovery section with rounds state, localStorage, renderRounds(), exportEzyGolferJSON(), clearRounds(); divider fix (i===9); Add Round button moved to bottom; Clear All Rounds added
- **Outcome:** 43 rounds recovered and imported into EzyGolfer successfully. iPhone confirmed clean.
- **Learnings:** localStorage is mandatory for stateful web tools. EzyGolfer backup format requires `isComplete: true` and ISO8601 fractional-second dates. 0-indexed divider must use `i === 9` for after-hole-9 visual split.

## Active Context

### Current Focus
Tool is stable and complete. No active development.

### Open Questions
- None

### Next Steps
1. No planned changes — tool served its recovery purpose

## Technical Context

### Architecture
Single `index.html` — no build tooling, no dependencies, no frameworks. All state in JS variables + localStorage. All rendering via `innerHTML` assignment in render functions.

### Key Patterns
- **State:** `rounds[]` array; mutated by `addRound()`, `removeRound()`, `setRoundMeta()`, `setRoundScore2()`
- **Persistence:** Every mutation calls `saveRounds()` → `localStorage.setItem('ezygolfer_recovery_rounds', JSON.stringify(rounds))`; boot calls `loadRounds()`
- **Export format:** `{ courses: [], rounds: [{ id, courseName, teeName, date, isComplete, totalScore, scoreEntries: [{holeNumber, strokes, putts, fir, gir, penalties}] }] }`
- **date field:** `new Date(dateStr + 'T00:00:00.000Z').toISOString()` — ISO8601 with fractional seconds required by EzyGolfer parser

### Known Issues
- None
