# Maintenance & Support Strategy (Student Edition) — Fred's Car Rental

*Purpose-built for coursework and easy demonstration on lab or personal machines.*

---

## 1) Audience & Goals

- **Audience:** students, markers, and classmates reviewing the project.  
- **Goal:** keep maintenance tasks **simple, fast, and doable** without admin rights or paid tools.  
- Everything should work **offline** with Python + SQLite and optional one-click scripts.

---

## 2) Scope (What We Maintain)

- Source code under `src/carrental` (CLI, services, repositories).
- SQLite database file (`carrental.db`) created in the **current folder** (source) or **next to the EXE** (packaged).
- Build scripts for Windows (PyInstaller).
- Tests (`pytest`) that run locally and **do not touch your real data**.

---

## 3) Versioning for Students (Simple SemVer) (This will be apply on future changes)
A simplified Semantic Versioning (SemVer) system will be applied to future updates. For the initial release, version v1.0.0 has been published.

We use a light Semantic Versioning: **MAJOR.MINOR.PATCH**

- **PATCH (x.y.Z):** tiny fixes, no behavior or schema changes.  
- **MINOR (x.Y.z):** small features that don’t break old usage (**additive** only).  
- **MAJOR (X.y.z):** rare; only if we change the **database schema** or CLI in breaking ways.

---

## 4) Branching & Collaboration (Minimal)

- `main` = stable branch used for submission.  
- For changes, create a short-lived branch: `dev/<short-name>` then merge via PR or fast-forward.  
- Keep commits **small and meaningful**. Avoid big refactors right before submission.

---

## 5) Database Policy (Student-Friendly)

- Default schema version: `PRAGMA user_version = 1`. **Do not** change it during the course.  
- If you must add a column for a demo, prefer an **additive** change and note it in README.  
- Seeder **never** alters schema; it only inserts data **if missing**.  
- Back up by copying the `carrental.db` file while the app is closed.

*If the app sees a newer DB version than it expects, it will refuse to run and ask to restore a backup or use a matching app version.*

---

## 6) Routine Maintenance (What to actually do)

1. **Before coding:** run tests once to ensure a clean baseline (`run_tests.bat` or `python -m pytest -vv`).  
2. Make your change in a **small commit**; run tests again.  
3. If you changed data behavior, also run the **seeder** and do a quick **manual smoke test**.  
4. Update **README** (1–3 bullet points).  
5. If needed, **rebuild executables** and verify they create `carrental.db` next to the binary.

---

## 7) Testing & Quality Gates (Doable)

- Use **pytest** with the provided tests. Each test runs in a **temp folder** with a **fresh DB**.  
- Aim for basic coverage of **services & repositories** (≈70–80% is fine for coursework).  
- Quick commands:

**Windows**
```bat
run_tests.bat        :: setup + run tests (verbose)
test_report.bat      :: coverage + HTML report
```

---

## 8) Packaging & Releases (Student Mode)

- **Windows:** `scripts\build_windows.bat` (creates `.venv`, installs PyInstaller, outputs to `dist/`).  
- After build: copy the **EXE** and run it in a **fresh folder**

---

## 9) Support & Troubleshooting (For Markers/Peers)

- If something crashes, re-run from a **fresh empty folder** to ensure a clean DB.  
- Run tests with more detail: `python -m pytest -vv -ra --tb=short -l`.  
- Common issues:
  - **Imports fail** → run from repo root; ensure `src/` exists; venv is activated.  
  - **Database locked** → close other instances; try again in a new folder.  
  - **Login fails in tests** → duplicate email or stale DB; tests isolate DB, but delete stray `carrental.db` if needed.

---

## 10) Limitations (Known & Acceptable for Coursework)

- **CLI only** (no web/GUI).  
- Booking **overlap checks** are basic; edge cases may exist.  
- No **payments** or email notifications.  
- SQLite is **single-user** oriented; concurrent writes are limited.  
- Schema changes are **discouraged** during the course to keep grading simple.

---

## 11) Future Student-Friendly Improvements

- Add more unit tests for edge cases (date ranges, availability toggles).  
- **CSV import/export** for cars and bookings to speed up demos.  
- A lightweight **TUI/GUI wrapper** (e.g., Textual) if time allows.  
- Basic **reports** (utilization, revenue) computed from bookings.

---

## 12) Quick FAQ

- **How do I reset the app?**  
  Delete the `carrental.db` file in the same folder where the app runs, then relaunch the application or execute the seed file to regenerate the default data..  

- **Does the folder name matter when running the app?**  
  Yes, it's **recommended to use a short folder name and path** (e.g., `C:\FCR` instead of `C:\Users\YourName\Documents\SchoolProjects\FredsCarRentalSystem`). Long folder paths can cause issues when running scripts or generating virtual environments, especially on Windows.

- **Can I rename the executable or seed file?**  
  It’s not recommended. These files are internally linked to specific names and logic. Renaming them may cause execution errors or break database connections.

---

## 13) Mini Checklists

### Release Checklist (Student)
- All tests pass locally; `run_tests.bat` completes with **exit code 0**.  
- Manual smoke test of packaged EXE on a **fresh folder**.  
- **README* updated (1–3 bullets).  
- Zip the `dist/` outputs and include in submission.

### Troubleshooting Checklist
- Try in a **clean folder**; remove any old `carrental.db`.  
- Activate venv; reinstall requirements; **run tests again**.  
- Capture console output (Windows CMD):  
  ```bat
  .\FredsCarRental.exe *> log.txt
  ```
