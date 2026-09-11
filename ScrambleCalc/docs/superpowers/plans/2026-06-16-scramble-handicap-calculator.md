# Scramble Handicap Calculator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A single-file HTML web app for calculating scramble golf handicaps, managing scoresheets, and determining winners.

**Architecture:** Single `index.html` file with embedded CSS and JS. Uses localStorage for persistence with JSON export/import. All state managed in-memory with a simple data store pattern, rendered via DOM manipulation.

**Tech Stack:** Plain HTML5, CSS3, Vanilla JavaScript (ES modules via `<script type="module">` or IIFE), localStorage API.

---
## Calculation Rules

**2-person team:** Team Handicap = A×0.35 + B×0.10 (A = lowest handicap)
**3-person team:** Team Handicap = A×0.20 + B×0.15 + C×0.10
**4-person team:** Team Handicap = A×0.20 + B×0.15 + C×0.10 + D×0.05

Team handicap is rounded to one decimal place. Net Score = Total Score − Team Handicap. Lowest net score wins.

---

## Data Model

```js
{
  id: "uuid-string",
  name: "Tournament Name",
  courseName: "Augusta National",
  slope: 113,
  playersPerTeam: 4,
  teams: [
    {
      id: "team-uuid",
      name: "Team Alpha",        // user-editable, optional
      players: [
        { name: "Player 1", handicap: 6.0 }
      ],
      totalScore: 72              // entered at scoring stage
    }
  ],
  createdAt: "2026-06-16T12:00:00Z",
  updatedAt: "2026-06-16T14:00:00Z"
}
```

---

## Files

- Create: `index.html` (entire app — HTML, CSS, JS)

---

### Task 1: Create the HTML skeleton and CSS

**File:** `index.html` (lines 1-150)

- [ ] **Step 1: Write the HTML skeleton**

Document structure:
- `#app` container with three screen divs: `#screen-home`, `#screen-setup`, `#screen-scoresheet`
- `#screen-home`: title, "Create New Scoresheet" button, saved scoresheets list, import button
- `#screen-setup`: form with name, course, slope, players-per-team selector, team builder
- `#screen-scoresheet`: teams table with score inputs, "Calculate Winner" button, results display

- [ ] **Step 2: Write the CSS**

- Clean, golf-themed design (green headers, white cards, subtle shadows)
- Screen switching via `.hidden` class (`display: none`)
- Responsive layout using flexbox
- Highlighted winner row with green background + bold text
- BEM-like class naming for readability

---

### Task 2: Implement the app shell and routing

**File:** `index.html` (JS section, lines 150-250)

- [ ] **Step 1: State management**

```js
const state = {
  currentScreen: 'home',    // 'home' | 'setup' | 'scoresheet'
  currentScoresheetId: null,
  scoresheets: []            // loaded from localStorage
};
```

Functions:
- `loadScoresheets()` — reads from localStorage key `scramble_scoresheets`
- `saveScoresheets()` — writes to localStorage
- `switchScreen(screenName)` — toggles `.hidden` on screen divs

- [ ] **Step 2: Navigation helpers**

```js
function switchScreen(name) {
  document.querySelectorAll('.screen').forEach(s => s.classList.add('hidden'));
  document.getElementById(`screen-${name}`).classList.remove('hidden');
  state.currentScreen = name;
}

function generateId() {
  return crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).slice(2);
}
```

---

### Task 3: Implement Home Screen

**File:** `index.html` (JS, lines 250-320)

- [ ] **Step 1: Render saved scoresheets list**

Function `renderHome()`:
- Iterate `state.scoresheets`
- For each: show name, course, date, playersPerTeam
- "Open" button → switches to scoresheet screen with that scoresheet
- "Delete" button → removes from array, re-saves, re-renders
- "Export" button → triggers JSON download

- [ ] **Step 2: "Create New Scoresheet" button**

Clears setup form fields and switches to setup screen.

- [ ] **Step 3: JSON import**

File input → `FileReader.readAsText()` → JSON.parse → validate → push to scoresheets → save → re-render.

---

### Task 4: Implement Setup Screen

**File:** `index.html` (JS, lines 320-450)

- [ ] **Step 1: Players-per-team selector**

A `<select>` with options 2, 3, 4. On change → regenerate the team template (the number of player name/handicap input pairs per team).

- [ ] **Step 2: Team builder**

- An "Add Team" button
- Each team block has:
  - Team name input (optional)
  - N player rows (name + handicap number input), where N = playersPerTeam
  - A "Remove Team" button
- Clicking "Add Team" appends a new team block
- Player inputs are sorted within each team block visually by handicap order

- [ ] **Step 3: Save button**

Collects form data → builds scoresheet object → pushes to `state.scoresheets` → saves to localStorage → switches to scoresheet screen.

---

### Task 5: Implement Scoresheet (Scoring) Screen

**File:** `index.html` (JS, lines 450-580)

- [ ] **Step 1: Render scoresheet**

Load the current scoresheet from state. Display:
- Tournament name, course, slope
- Table: Team Name | Players (with handicaps) | Team Handicap | Total Score | Net Score

Team Handicap calculation:
```js
function calcTeamHandicap(players, playersPerTeam) {
  const sorted = [...players].sort((a, b) => a.handicap - b.handicap);
  const rates = { 2: [0.35, 0.10], 3: [0.20, 0.15, 0.10], 4: [0.20, 0.15, 0.10, 0.05] };
  const rate = rates[playersPerTeam];
  const total = sorted.reduce((sum, p, i) => sum + (rate[i] || 0) * p.handicap, 0);
  return Math.round(total * 10) / 10;
}
```

- [ ] **Step 2: Score input**

Each team row has a number input for Total Score. On change/input, recalculate Net Score for that row.

- [ ] **Step 3: "Calculate Winner" button**

- Validate all team scores are entered
- Find team(s) with lowest Net Score
- Highlight that team row with green background
- Display winner banner with team name and player names

- [ ] **Step 4: Save updated scoresheet**

After any score change, call `saveScoresheets()` to persist.

---

### Task 6: JSON Export/Import

**File:** `index.html` (JS, lines 580-620)

- [ ] **Step 1: Export function**

```js
function exportScoresheet(id) {
  const sheet = state.scoresheets.find(s => s.id === id);
  const blob = new Blob([JSON.stringify(sheet, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${sheet.name.replace(/\s+/g, '_')}_scoresheet.json`;
  a.click();
  URL.revokeObjectURL(url);
}
```

- [ ] **Step 2: Import function**

```js
function importScoresheet(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    const sheet = JSON.parse(e.target.result);
    // Validate structure
    if (!sheet.name || !sheet.teams || !sheet.playersPerTeam) {
      alert('Invalid scoresheet file');
      return;
    }
    sheet.id = generateId();
    sheet.updatedAt = new Date().toISOString();
    state.scoresheets.push(sheet);
    saveScoresheets();
    renderHome();
  };
  reader.readAsText(file);
}
```

---

### Task 7: Self-Review Against Spec

- [ ] **User selects number of players per team** → Setup screen dropdown (2/3/4)
- [ ] **Enter player names and handicaps** → Input fields per team per player
- [ ] **Add another team** → "Add Team" button
- [ ] **Save scoresheet for later retrieval** → localStorage + JSON export
- [ ] **Retrieve scoresheet** → Home screen list → Open
- [ ] **Enter team scores** → Scoresheet screen table inputs
- [ ] **Calculate winner** → Button triggers net score comparison
- [ ] **Highlight winner** → Green background on winning team row
- [ ] **Course slope input** → Setup screen field
- [ ] **2-person formula (35%/10%)** → In calcTeamHandicap
- [ ] **3-person formula (20%/15%/10%)** → In calcTeamHandicap
- [ ] **4-person formula (20%/15%/10%/5%)** → In calcTeamHandicap
- [ ] **No build step / plain HTML/CSS/JS** → Single file
- [ ] **JSON export/import** → Task 6

---

## Verification

1. Open `index.html` in browser — home screen renders
2. Create scoresheet with 4-person teams, fill players, save
3. Verify returned to home, scoresheet appears in list
4. Open scoresheet, enter total scores, calculate winner
5. Verify correct team highlighted
6. Export, delete, re-import — verify data integrity
7. Test 2-person and 3-person formulas independently
8. Reload page — verify localStorage persisted
