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
3. [Step‑by‑Step: Configure, Install, and Operate](#step-by-step-configure-install-and-operate)
   - [A. Quick Start (Binaries)](#a-quick-start-binaries)
   - [B. Run From Source (Developers)](#b-run-from-source-developers)
   - [C. Build Executables (Windows & Linux)](#c-build-executables-windows--linux)
   - [D. Operate the CLI (User Walkthrough)](#d-operate-the-cli-user-walkthrough)
4. [Database Behavior & Schema Stability](#database-behavior--schema-stability)
5. [All Relevant Files & Purpose](#all-relevant-files--purpose)
6. [Configuration](#configuration)
7. [Known Bugs / Issues](#known-bugs--issues)
8. [License](#license)
9. [Credits](#credits)

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
If you downloaded packaged builds (./dist folder), you should have two files in the same folder:
- `FredsCarRental.exe` (Windows)
- `FredsCarRentalSeeder.exe` (Optional, the package is already pre seeded)

1. **Place both executables in the same folder.**  
2. **Run the app** (`FredsCarRental.exe` or `./FredsCarRental`). On first run it creates **`carrental.db` next to the executable**.   
3. **Login as Admin**: `admin@admin.com` / `admin123` → **change password immediately**.  
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

### C. Build Executables (Windows & Linux)
Scripts in `scripts/` work **from anywhere** (they `cd` to project root). They create a local `.venv`, install **PyInstaller**, and produce binaries under `dist/`.

**Windows**  
- CMD:
  ```bat
  scripts/build_windows.bat
  ```

**Outputs**
- App: `dist/FredsCarRental(.exe)`  
- Seeder: `dist/FredsCarRentalSeeder(.exe)`

### D. Operate the CLI (User Walkthrough)
- **Home / Login Screen**  
  `1) Login` → enter email/password  
  `2) Register` → create user account  
  `0) Exit` → quit
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

**Source** (`src/carrental/`)
- `main.py` — **CLI entrypoint**; wires menus & services.  
- `__init__.py` — Package marker.
- `__main__.py` - Acts as the package entry point so python -m <package> launches the CLI app (wiring menus/services to start the program).
- `utils/ui.py` — Terminal UI helpers (boxes, prompts).
- `utils/validators.py` — Provides reusable input checks (email/password/date/number/menu) to validate and sanitize user entries consistently across the CLI. 
- `storage/db.py` — SQLite helper (**Singleton**); portable DB path; **schema lock** via `PRAGMA user_version`.  
- `storage/repositories.py` — **Repository layer** for Users, Cars, Bookings (isolates SQL).
- `storage/seed.py` — Seeds the database by creating a default admin account and topping up sample cars (idempotent, no schema changes).
- `services/auth_service.py` — Registration, login, session helpers, admin utilities.  
- `services/inventory_service.py` — Car listing/add/edit/toggle.  
- `services/rental_service.py` — Booking creation/list/cancel; pricing hook (Strategy‑ready).  

**Docs (optional)**
- `docs/` — UML diagrams, test plans, maintenance plan, etc.

> **Ignored from VCS** (recommended via `.gitignore`): `.venv/`, `dist/`, `build/`, `__pycache__/`, `*.spec`, `carrental.db`, logs, and large build archives.

---

## Configuration
The app runs without extra configuration. Defaults:
- DB filename: `carrental.db` (location logic in `storage/db.py`).
- Seeder defaults: `admin@local` / `Admin@123`, `--car-count 10`. (Optional)
- No environment variables are required for basic usage.

---

## Known Bugs / Issues / Require improvements
- **Schema mismatch stop**: If `PRAGMA user_version != 1`, the app exits with a schema version error (by design). Fix by setting `user_version=1` or applying a planned migration.
- **Unsigned binaries**: Fresh PyInstaller executables may trigger antivirus warnings. Whitelist locally or code‑sign for distribution.
- **Single‑user CLI focus**: No concurrency control for multi‑process access; simultaneous writes may contend.
- **Date validation edge cases**: Common formats are validated; extreme edge cases may require review.
- **No GUI**: The brief requires a CLI; there is no graphical UI.
- **Admin**: Admin management can have more security (Subject for enhancement)

---

## License
This project is released under the **MIT License**. You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, subject to the conditions in the `LICENSE` file. The software is provided **“as is”**, without warranty of any kind.

**SPDX‑Identifier:** MIT  
See the bundled `LICENSE` file for the full text.

---

## Credits
**Developer:** Fredierick “Fred” Saladas — GitHub: @ciastirfry https://github.com/ciastirfry/MSE800-car-rental-system-assessment
**Course/Context:** Master of Software Engineering (Yoobee) — *Professional Software Engineering: Car Rental System*  
**Acknowledgments:** Classmates and instructors for guidance and feedback.

If you use or extend this project, please retain attribution. Contributions and suggestions are welcome.

