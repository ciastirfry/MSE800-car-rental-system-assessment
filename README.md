# Fred's Car Rental System (CLI, Python + SQLite)

A cross‑platform **command‑line car rental system** built in Python (≥ 3.10) with SQLite storage. It ships with:
- A **portable database** design (DB file is created next to the executable in packaged builds; in source runs it is created in the current working directory).
- A **separate Seeder executable** to create an Admin user and sample cars.
- A clean, OOP‑based code structure using **Singleton**, **Repository**, and **Strategy** patterns.

This README is written for **Users** and **Programmers** and covers configuration, installation, operation, files & purposes, licensing, known issues, and credits.

---

## Table of Contents
1. [Features](#features)
2. [System Requirements](#system-requirements)
3. [Step‑by‑Step: Configure, Install, and Operate](#stepbystep-configure-install-and-operate)
   - [A. Quick Start (Binaries)](#a-quick-start-binaries)
   - [B. Run From Source (Developers)](#b-run-from-source-developers)
   - [C. Build Executables (Windows)](#c-build-executables-windows)
   - [D. Operate the CLI (User Walkthrough)](#d-operate-the-cli-user-walkthrough)
4. [Database Behavior & Schema Stability](#database-behavior--schema-stability)
5. [All Relevant Files & Purpose](#all-relevant-files--purpose)
6. [Project Structure & File Purposes](#project-structure--file-purposes)
7. [Configuration](#configuration)
8. [Testing](#testing)
9. [Known Bugs / Issues](#known-bugs--issues)
10. [License](#license)
11. [What I Learned](#what-i-learned)
12. [Credits](#credits)

---

## Features
- **CLI‑only** application with clear, guided menus.
- **SQLite** file‑based storage (easy to copy/backup).
- **Portable DB**: packaged builds create/use `carrental.db` next to the executable.
- **Seeder**: seeds an **Admin** account and **sample cars**; **idempotent** (safe to re‑run and optional).
- **OOP + Patterns**: `Database` (Singleton), `repositories.py` (Repository), extensible Strategy hooks for pricing/payment.
- **Core flows**: Register/Login, List Cars, Add/Edit Cars (Admin), Create/Cancel Booking, View Bookings.
- **Schema lock**: prevents silent DB schema changes (via `PRAGMA user_version=1`).

---

## System Requirements
- **Windows 11**
- **Binaries**: No Python required to run.
- **Developers**: Python **3.10+** and `pip` if running/building from source.

---

## Step‑by‑Step: Configure, Install, and Operate

### A. Quick Start (Binaries)
If you downloaded the packaged (ZIP) executable build from Blackboard, you should see two files in the same folder:
- `FredsCarRental.exe` (Windows)
- `FredsCarRentalSeeder.exe` (Optional, the package is already pre seeded)

1. **Place both executables in the same folder.**  
2. **Run the app** (`FredsCarRental.exe`).   
3. **Login as Admin**: `admin@admin.com` / `admin123`
4. Proceed to [Operate the CLI](#d-operate-the-cli-user-walkthrough).

> **Portable:** You can move the folder (including `carrental.db`) anywhere—USB‑friendly. (Optional)

### B. Run From Source (Developers)
```bash
# Windows (CMD)
CALL .venv\Scripts\activate
pip install -r requirements.txt
set PYTHONPATH=src
python -m carrental.main

```
Run the app from the **project root**:
**Windows**  
- CMD:
  ```bat
  run_carrental.bat
  ```

### C. Build Executables (Windows)
Scripts in `scripts/` work **from anywhere** (they `cd` to project root). They create a local `.venv`, install **PyInstaller**, and produce binaries under `dist/`.

**Windows**  
- CMD:
  ```bat
  scripts/build_windows.bat
  ```

**Outputs**
- App: `dist/FredsCarRental(.exe)`  
- Seeder: `dist/FredsCarRentalSeeder(.exe)`

## Seeding Data (Admin & Cars)
Use the **Seeder executable** (or run `tools/seed_data.py` from source). It is **idempotent** (safe to run multiple times).

**Defaults**:
- Admin: `admin@admin.com` / `admin123`
- Cars: ensures at least **13** cars

**Custom flags (packaged or source)**: (Optional not required)
```bash
./FredsCarRentalSeeder \
  --admin-email admin@local \
  --admin-name "Administrator" \
  --admin-password "ChangeMe@123" \
  --car-count 12
```

### D. Operate the CLI (User Walkthrough)
- **Home / Login Screen**  
  `1) Login` → enter email/password  
  `2) Register` → create user account  
  `0) Exit` → quit
- **Demo Video**  
  A short demo video is included as part of the submission to demonstrate how to navigate the car rental system.
- **Admin**  
  Manage cars (add/update/delete), review bookings, view cars.
- **User**  
  List available cars, create booking, view own bookings.
- **Validation**  
  The CLI reprompts on invalid input and shows clear messages for common mistakes (e.g., wrong date format).

---

## Database Behavior & Schema Stability
- **Location**  
  - **Packaged (frozen)**: creates/uses `./carrental.db` **beside the executable**.  
  - **Source run**: creates/uses `carrental.db` in the **current working directory**.
- **Schema Lock**  
  On first run, the app sets `PRAGMA user_version=1`. If a different version is later detected, the app **refuses to run**, protecting your data from accidental migrations. If you intentionally change schema, add a migration and bump the version consciously.
- **Backup/Restore**  
  Stop the app and copy `carrental.db` like any file. To restore, place it next to the executable and start the app.

---

## All Relevant Files & Purpose

**Top Level**
- `README.md` — Detailed build & packaging instructions (binaries, seeder, troubleshooting).  
- `LICENSE` — **MIT License** text (see [License](#license)).  
- `requirements.txt` — Python dependencies when running/building from source.

**Scripts** (`scripts/`)
- `build_windows.bat` — Windows (CMD) build script; robust path handling; uses `py -3.x` if available.

---

## Project Structure & File Purposes

```
.
├─ LICENSE                       # MIT License text
├─ README.md                     # This file (place at repo root)
├─ requirements.txt              # Python dependencies
├─ docs/
│  ├─ uml/
│  │  ├─ class.md                # Class Diagram
│  │  ├─ sequence.md             # Sequence Diagram
│  │  └─ use_case.md             # Use Case Diagram
│  └─ maintenance_support.md     # Maintenance & Support Strategy
├─ scripts/
│  └─ build_windows.bat          # Windows (CMD) packager
├─ tools/
│  ├─ seed_runner.py             # Seeder entrypoint (Admin + cars; idempotent)
│  └─ app_runner.py              # Uses absolute imports (avoids relative-import issues in PyInstaller)
├─ tests/
│  ├─ test_services.py           # pytest setup
│  ├─ conftest.py                # Isolates temp DB & resets DB singleton 
│  ├─ run_tests.bat              # One-click: setup venv + run pytest (verbose)  
│  └─ test_report.bat            # One-click: tests + coverage + HTML report  
└─ src/
   └─ carrental/
      ├─ __init__.py             # Package marker
      ├─ __main__.py             # Acts as the package entry point
      ├─ main.py                 # CLI entrypoint; wires menus & services
      ├─ utils/
      │  ├─ ui.py                # Helper functions for pretty CLI (boxes, prompts)
      │  └─ validators.py        # Provides reusable input checks
      ├─ storage/
      │  ├─ db.py                # SQLite helper (Singleton); portable DB path + schema lock
      │  ├─ repositories.py      # Repositories for Users, Cars, Bookings (SQL isolated here)
      │  └─ seed.py              # Seeds the database by creating a default admin account and topping up sample cars
      ├─ services/
      │  ├─ auth_service.py      # Register/Login/Session; admin helpers
      │  ├─ inventory_service.py # Car listing/add/edit/toggle
      │  └─ rental_service.py    # Booking creation/list/cancel; price logic hook
      ├─ core/                   
      │   ├─ factories.py        # Factory that builds Car objects in one place
      │   ├─ models.py           # Data models for User, Car, and Booking
      │   └─ strategies.py       # Pricing and payment strategies (Strategy pattern)
      └─ cli/
          └─ commands.py         # Command objects for each menu action (Command pattern)
``` 

**Docs (optional)**
`docs/` — UML diagrams, test plans, maintenance plan, etc.

- See the [Use Case Diagram][usecase].

[usecase]: docs/uml/UML_Use_Case_Diagram.png
- See the [Sequence Diagram][usecase1].

[usecase1]: docs/uml/UML_Sequence_Diagram.png
- See the [Class Diagram][usecase2].

[usecase2]: docs/uml/UML_Class_Diagram.png


> **Ignored from VCS** (recommended via `.gitignore`): `.venv/`, `dist/`, `build/`, `__pycache__/`, `*.spec`, `carrental.db`, logs, and large build archives.

---

## Configuration
The app runs without extra configuration. Defaults:
- DB filename: `carrental.db` (location logic in `storage/db.py`).
- Seeder defaults: `admin@admin.com` / `admin123`, `--car-count 10`. (Optional)
- No environment variables are required for basic usage.

---

## Testing
This project uses pytest. Tests run in temp folders with a fresh SQLite DB, so your real data is safe.

**Quick start:**
```bash
python -m venv .venv
# Windows: .\.venv\Scripts\activate 
pip install -r requirements.txt pytest
python -m pytest -vv

```

**Coverage & HTML report:**
```bash
pip install pytest-cov pytest-html
python -m pytest -vv --cov=src/carrental --cov-report=term-missing:skip-covered \
  --html=pytest_report.html --self-contained-html

```
**Shortcuts (Windows):**
- `run_tests.bat` — setup + run tests (verbose)
- `test_report.bat` — coverage + HTML report (auto-opens) 

---

## Known Bugs / Issues / Require improvements
- **Schema mismatch stop**: If `PRAGMA user_version != 1`, the app exits with a schema version error (by design). Fix by setting `user_version=1` or applying a planned migration.
- **Unsigned binaries**: Fresh PyInstaller executables may trigger antivirus warnings. Whitelist locally or code‑sign for distribution.
- **Single‑user CLI focus**: No concurrency control for multi‑process access; simultaneous writes may contend.
- **Date validation edge cases**: Common formats are validated; extreme edge cases may require review.
- **No payments/invoicing**:no email notifications.
- **No GUI**: The brief requires a CLI; there is no graphical UI.
- **Admin**: Admin management can have more security (Subject for enhancement)
These are acceptable limitations for the assessment scope and noted for future work.

---

## License
This project is released under the **MIT License**. You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, subject to the conditions in the `LICENSE` file. The software is provided **“as is”**, without warranty of any kind.

**SPDX‑Identifier:** MIT  
See the bundled `LICENSE` file for the full text.

---

## What I Learned

**Architecture & Design**
- Designed a clean, layered architecture (CLI → Services → Repositories → SQLite) that keeps UI, business logic, and data access separate.
- Applied patterns intentionally:
  - **Repository** to isolate SQL and make services testable.
  - **Strategy** for pricing so the system can switch between daily or weekday/weekend rates without rewriting services.
- Modeled the system with UML (Use Case, Class, Sequence).

**Data & Seeding**
- Controlled schema changes using SQLite `PRAGMA user_version` to **freeze the DB structure**.
- Wrote an **idempotent seeder** to create an admin and sample cars without altering the schema.
- Ensured the DB file is created **next to the executable** in packaged builds and in the **current working directory** when running from source.

**Packaging & Tooling**
- Built cross-platform executables with **PyInstaller** and handled common pitfalls (missing entry paths, venv isolation, Windows launcher detection).
- Created robust **build and test batch scripts** that set up a venv, install dependencies, and run commands consistently on Windows.

**Testing & Quality**
- Set up **pytest** with fixtures that isolate each test in a temp folder and **reset the DB singleton** to avoid cross-test contamination.
- Generated **coverage** and **HTML test reports**; learned how to make verbose and focused test runs (`-vv`, `-k`, `--tb=short`, `-l`).

**Documentation & Communication**
- Produced a comprehensive **README**, a **Maintenance & Support** guide, and a **presentation** that explain installation, operation, testing, and known limitations.
- Learned to link images as **clickable links** (not embedded) in Markdown when needed.

**Challenges I Solved**
- Fixed PyInstaller path and environment issues (e.g., “pyinstaller not recognized”, conda/venv conflicts).
- Clarified DB path logic for both source and frozen (packaged) modes.

**Current Limitations (Accepted for Coursework)**
- **CLI only** (no GUI/Web); **no payments** or email notifications.
- **Basic** booking overlap checks; simplified date handling.
- SQLite is **single-writer** oriented—fine for demos but not for heavy concurrency.

**Next Steps (If Continued)**
- Add stronger booking conflict checks and richer admin reports.
- Introduce a lightweight GUI/Web front end.
- Formalize DB **migrations** for future schema changes and expand the test suite for edge cases.

---

## Credits
**Developer:** Fredierick “Fred” Saladas — (GitHub: [@ciastirfry](https://github.com/ciastirfry/MSE800-car-rental-system-assessment))  
**Course/Context:** Master of Software Engineering (Yoobee) — *Professional Software Engineering: Car Rental System*  
**Acknowledgments:** Classmates and instructors for guidance and feedback.

If you use or extend this project, please retain attribution. Contributions and suggestions are welcome.
