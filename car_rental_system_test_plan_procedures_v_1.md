# Car Rental System — Test Plan & Procedures
**Version:** 1.0  
**Date:** 17 Sep 2025 (Pacific/Auckland)  
**Owner:** Fredierick Saladas  
**Project:** Professional Software Engineering – Car Rental System (CLI, Python ≥3.10, SQLite)

---

## 1. Purpose & Scope
This document defines the test strategy and step‑by‑step procedures for the Car Rental System, including compiled executables for Windows/Linux and the separate Seeder executable. It verifies:
- Successful build on Windows & Linux
- DB location behavior (DB beside EXE/frozen build; CWD for source runs)
- Schema stability via `PRAGMA user_version = 1`
- Functional flows (Register, Login, List Cars, Booking lifecycle, Admin maintenance)
- Seeder behavior (admin creation, car top‑ups, idempotency)
- Error handling and basic non‑functional checks

Out of scope: UI automation for interactive CLI (beyond manual/procedural steps), distributed/concurrent testing.

---

## 2. Test Environment
**Operating Systems**  
- Windows 11 Pro (64‑bit)  
- Linux (e.g., Ubuntu 22.04 LTS or Debian 12)

**Runtimes/Tools**  
- Compiled binaries produced via PyInstaller (app + seeder)  
- Optional: Python 3.10+ for source runs and quick DB checks  
- Optional: SQLite CLI or DB Browser for SQLite

**Artifacts under test**  
- `dist/FredsCarRental(.exe)` — main app  
- `dist/FredsCarRentalSeeder(.exe)` — seeder  
- `carrental.db` — SQLite DB file created beside executable  
- `README-BUILD.md` — build/usage reference

---

## 3. Entry / Exit Criteria
**Entry**  
- Build completed successfully for target OS  
- Test workstation has read/write permissions in the app folder

**Exit**  
- All Smoke tests (S0) pass  
- No Sev‑1/Sev‑2 defects open; Sev‑3 acceptable with workaround  
- Regression rerun green after fixes

---

## 4. Risk & Mitigations
- **DB placed in wrong directory** → Verify with DB Location tests (§8)  
- **Schema drift** → Enforced by `user_version=1`; mismatch test in §9  
- **Seeder duplication** → Idempotency test in §7  
- **PyInstaller hidden imports** → Add flags during build; rebuild and retest

---

## 5. Test Data
Use Seeder defaults unless otherwise specified:  
- **Admin**: `admin@local` / `Admin@123`  
- **Cars**: Ensure at least **10** seeded; random makes/models; available by default  
- **User for booking tests**: create during tests (e.g., `user1@test.local` / `User@123`)

---

## 6. Pre‑Test Setup
1) **Prepare clean folder** for binaries (e.g., `C:\Apps\CarRentalTest\` or `/opt/carrental/`).  
2) Copy **both binaries** into the same folder: `FredsCarRental(.exe)` and `FredsCarRentalSeeder(.exe)`.  
3) Ensure no existing `carrental.db` in that folder (start clean for Smoke tests).  
4) If running from **source** instead of binaries, ensure Python 3.10+ and `PYTHONPATH=src`.

---

## 7. Smoke Test Suite (S0)
**S0‑1: First run creates DB**  
**Steps**: Launch app binary.  
**Expected**: App starts; `carrental.db` appears in the **same folder**.

**S0‑2: Seed admin + cars**  
**Steps**: Run seeder binary in the same folder.  
**Expected**: Console shows admin created (or exists) and cars added; total cars ≥ 10.

**S0‑3: Admin login**  
**Steps**: In app, choose Login → enter `admin@local` / `Admin@123`.  
**Expected**: Login success; admin‑level options visible (if applicable), or at least session shows admin identity.

**S0‑4: List cars**  
**Steps**: Navigate to Inventory/List Cars.  
**Expected**: ≥ 10 cars displayed with sensible fields (make/model/year/rate/availability).

**S0‑5: Basic booking**  
**Steps**: Register a new user; login as user; book an available car for a valid date range.  
**Expected**: Booking confirmed; total price computed; car becomes unavailable if system enforces exclusive rentals.

---

## 8. DB Location Tests (L)
**L‑1: DB beside executable (frozen mode)**  
**Steps**: Ensure no `carrental.db` exists; run app exe.  
**Expected**: `./carrental.db` created next to the exe.

**L‑2: Source run uses CWD**  
**Steps**: From project root, run `python -m carrental.main` (or `python src/carrental/main.py`) from a new folder using `cwd` redirection.  
**Expected**: `carrental.db` created in that **current working directory**.

**L‑3: Move folder portability**  
**Steps**: Copy binaries + DB to a new folder/USB; run app.  
**Expected**: App opens the DB in the **new** folder without errors.

---

## 9. Schema Stability Tests (SC)
**SC‑1: Version set on first run**  
**Steps**: After first launch, open DB and check: `PRAGMA user_version;`  
**Expected**: `1`.

**SC‑2: Mismatch blocks execution**  
**Steps**: Temporarily set `PRAGMA user_version=2;` then run app.  
**Expected**: App refuses to run with clear schema version mismatch message.

**SC‑3: Restore**  
**Steps**: Reset `PRAGMA user_version=1;` and relaunch.  
**Expected**: App works normally.

> Tip: Without SQLite CLI, you can run a tiny Python script to check/set `user_version`.

---

## 10. Seeder Tests (SD)
**SD‑1: Creates admin if missing**  
**Steps**: Delete DB, run seeder.  
**Expected**: Admin `admin@local` created; message confirms.

**SD‑2: Idempotency**  
**Steps**: Run seeder **twice**.  
**Expected**: Second run reports admin already exists; cars are **topped up** only to the requested count (no duplicates beyond target).

**SD‑3: Custom flags**  
**Steps**: Run `--admin-email`, `--admin-password`, `--car-count 15`.  
**Expected**: New admin created accordingly; cars ≥ 15; rerun preserves idempotency.

---

## 11. Functional Tests (F)
### F‑A: Authentication & Authorization
- **F‑A1 Register new user**: Register → confirmation; then login succeeds.
- **F‑A2 Wrong password**: Login with incorrect password → error; no session.
- **F‑A3 Password storage**: Inspect DB `users.password_hash` not equal to plaintext (SHA‑256 hex).  
- **F‑A4 Admin vs User**: Normal user cannot access admin‑only actions (if menu guards exist).

### F‑B: Inventory
- **F‑B1 List available cars**: Shows cars with `available=1` by default.
- **F‑B2 Admin add car**: Add car with valid fields → listed immediately.
- **F‑B3 Edit car**: Update fields; verify persisted.
- **F‑B4 Toggle availability**: Set `available=0`; list excludes car in default view.

### F‑C: Booking Flow
- **F‑C1 Create booking**: Valid dates (start ≤ end), available car → booking created; price computed.
- **F‑C2 Prevent booking unavailable**: Try booking already booked car → blocked with message.
- **F‑C3 Cancel/Return (if supported)**: Change status; car becomes available.
- **F‑C4 List my bookings**: Shows bookings filtered by user.

### F‑D: Input Validation
- **F‑D1 Non‑numeric menu**: Enter letters where numbers expected → graceful error & reprompt.
- **F‑D2 Bad date**: Invalid format or reversed range → validation error.
- **F‑D3 Required fields blank**: Prompts again or error message.

---

## 12. Error Handling & Recovery (E)
- **E‑1 Missing DB**: No `carrental.db` → created automatically on first run.
- **E‑2 Corrupted DB**: Replace with a zero‑byte file → app fails with clear error; recreate after deletion.
- **E‑3 File lock**: Open DB in external tool then run app → app should error gracefully or retry.
- **E‑4 Unexpected crash**: Verify DB integrity post‑crash (no partial rows for atomic ops).

---

## 13. Non‑Functional Checks (N)
- **N‑1 Performance (list)**: With ≥ 100 cars, listing completes within ~1s on local machine.
- **N‑2 Performance (booking)**: Booking insert < 500ms.
- **N‑3 Portability**: Binaries run without external install (no Python required).
- **N‑4 Logging/Console UX**: Prompts readable; no stack traces during normal use.

---

## 14. Cross‑Platform Procedures
### Windows
1) Place app + seeder EXEs in the same folder.  
2) Run app → DB appears in folder.  
3) Run seeder → admin + cars.  
4) Repeat functional suite.

### Linux
1) `chmod +x FredsCarRental FredsCarRentalSeeder`.  
2) Run app; then seeder.  
3) Repeat functional suite.

---

## 15. Detailed Test Cases (sample format)
Use the following format for execution logging.

**TC‑F‑C1 Create booking (happy path)**  
**Pre‑req**: Logged in as normal user; ≥ 1 available car.  
**Steps**: Choose “Book Car” → select car → enter start/end dates → confirm.  
**Expected**: Booking ID shown; price computed; car availability updated.

**TC‑SD‑2 Seeder idempotency**  
**Pre‑req**: DB exists with admin and ≥ 10 cars.  
**Steps**: Run seeder again.  
**Expected**: “Admin exists”; cars count remains at target (no duplicates beyond requested count).

**TC‑SC‑2 Schema mismatch**  
**Pre‑req**: DB present.  
**Steps**: Set `PRAGMA user_version=2;` then start app.  
**Expected**: App aborts with schema mismatch error; no destructive changes.

---

## 16. Regression Suite (R)
Run after any code change:
- S0 smoke suite  
- F‑A (Auth) full  
- F‑B (Inventory) add/edit/toggle  
- F‑C (Bookings) create/block/cancel  
- L & SC (location + schema)

---

## 17. Acceptance Criteria
- Smoke suite passes on Windows & Linux  
- DB created alongside binary; schema version locked to 1  
- Seeder is idempotent and honors flags  
- Core flows (register, login, list, book) fully functional

---

## 18. Bug Report Template
**Title**: Short summary  
**Environment**: OS, build ID/date  
**Pre‑conditions**: State of DB, user, etc.  
**Steps to Reproduce**: 1…n  
**Expected Result**:  
**Actual Result**:  
**Severity/Priority**:  
**Attachments/Logs**: console output, DB snapshot

---

## 19. Test Execution Log (sample)
| Date | Tester | TC ID | Result | Notes |
|---|---|---|---|---|
| 2025‑09‑17 | Fred | S0‑1 | Pass | DB created beside exe |
| 2025‑09‑17 | Fred | SD‑2 | Pass | Seeder idempotent |

---

## 20. Traceability Matrix (excerpt)
| Requirement | Test(s) |
|---|---|
| DB beside executable | L‑1 |
| Source run uses CWD | L‑2 |
| Schema version locked | SC‑1/SC‑2 |
| Admin & cars seeded | SD‑1/SD‑3 |
| Auth & Roles | F‑A1…F‑A4 |
| Booking lifecycle | F‑C1…F‑C4 |

---

## 21. Sign‑Off Checklist
- [ ] S0 smoke suite passed on both OSes  
- [ ] L/SC tests passed (location + schema)  
- [ ] Seeder tests passed (idempotent)  
- [ ] Functional core passed (Auth, Inventory, Booking)  
- [ ] No Sev‑1/2 open defects  
- [ ] Regression green after last fix

**Approved by:** ____________________  
**Date:** ____________________

