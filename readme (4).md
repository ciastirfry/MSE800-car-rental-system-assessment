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
- **Seeder**: seeds an **Admin** account and **sample cars**; **idempotent** (safe to re‑run).
- **OOP + Patterns**: `Database` (Singleton), `repositories.py` (Repository), extensible Strategy hooks for pricing/payment.
- **Core flows**: Register/Login, List Cars, Add/Edit Cars (Admin), Create/Cancel Booking, View Bookings.
- **Schema lock**: prevents silent DB schema changes (via `PRAGMA user_version=1`).

---

## System Requirements
- **Windows 11** or **Linux** (x64)
- **Binaries**: No Python required to run.
- **Developers**: Python **3.10+** and `pip` if running/building from source.

---

## Step‑by‑Step: Configure, Install, and Operate

### A. Quick Start (Binaries)
If you downloaded packaged builds (e.g., from Releases), you should have two files in the same folder:
- `FredsCarRental.exe` (Windows) / `FredsCarRental` (Linux)
- `FredsCarRentalSeeder.exe` (Windows) / `FredsCarRentalSeeder` (Linux)

1. **Place both executables in the same folder.**  
2. **Run the app** (`FredsCarRental.exe` or `./FredsCarRental`). On first run it creates **`carrental.db` next to the executable**.  
3. **Run the Seeder** (`FredsCarRentalSeeder.exe` or `./FredsCarRentalSeeder`) to insert an **Admin** and **≥ 10 cars**.  
4. **Login as Admin**: `admin@local` / `Admin@123` → **change password immediately**.  
5. Proceed to [Operate the CLI](#d-operate-the-cli-user-walkthrough).

> **Portable:** You can move the folder (including `carrental.db`) anywhere—USB‑friendly.

### B. Run From Source (Developers)
```bash
# Windows (PowerShell)
python -m venv .venv
./.venv/Scripts/Activate.ps1
pip install -r requirements.txt

# Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Run the app from the **project root**:
```bash
# Either:
python -m carrental.main
# Or:
python src/carrental/main.py
```
> In source runs, the DB is created in the **current working directory**.

### C. Build Executables (Windows & Linux)
Scripts in `scripts/` work **from anywhere** (they `cd` to project root). They create a local `.venv`, install **PyInstaller**, and produce binaries under `dist/`.

**Windows**  
- PowerShell:
  ```powershell
  ./scripts/build_windows.ps1
  ```
- CMD:
  ```bat
  scripts/build_windows.bat
  ```

**Linux**  
```bash
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
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
  Manage cars (add/edit/toggle availability), review bookings, admin utilities.
- **User**  
  List available cars, create booking, view/cancel own bookings.
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
- `README.md` — This user & developer guide.  
- `README-BUILD.md` — Detailed build & packaging instructions (binaries, seeder, troubleshooting).  
- `LICENSE` — **MIT License** text (see [License](#license)).  
- `requirements.txt` — Python dependencies when running/building from source.

**Scripts** (`scripts/`)
- `build_windows.ps1` — Windows (PowerShell) build script (creates venv, installs PyInstaller, outputs `dist/`).
- `build_windows.bat` — Windows (CMD) build script; robust path handling; uses `py -3.x` if available.
- `build_linux.sh` — Linux build script; sets `PYTHONPATH`, runs PyInstaller.

**Tools** (`tools/`)
- `seed_data.py` — **Seeder entrypoint**: creates Admin and ensures ≥ N cars (idempotent, accepts flags like `--car-count`). Compiled to `FredsCarRentalSeeder(.exe)`.

**Source** (`src/carrental/`)
- `main.py` — **CLI entrypoint**; wires menus & services.  
- `__init__.py` — Package marker.  
- `utils/ui.py` — Terminal UI helpers (boxes, prompts).  
- `storage/db.py` — SQLite helper (**Singleton**); portable DB path; **schema lock** via `PRAGMA user_version`.  
- `storage/repositories.py` — **Repository layer** for Users, Cars, Bookings (isolates SQL).  
- `services/auth_service.py` — Registration, login, session helpers, admin utilities.  
- `services/inventory_service.py` — Car listing/add/edit/toggle.  
- `services/rental_service.py` — Booking creation/list/cancel; pricing hook (Strategy‑ready).  
- `models/` — *(Optional)* Domain types if split from services.

**Docs (optional)**
- `docs/` — UML diagrams, test plans, maintenance plan, etc.

> **Ignored from VCS** (recommended via `.gitignore`): `.venv/`, `dist/`, `build/`, `__pycache__/`, `*.spec`, `carrental.db`, logs, and large build archives.

---

## Configuration
The app runs without extra configuration. Defaults:
- DB filename: `carrental.db` (location logic in `storage/db.py`).
- Seeder defaults: `admin@local` / `Admin@123`, `--car-count 10`.
- No environment variables are required for basic usage.

---

## Known Bugs / Issues
- **Schema mismatch stop**: If `PRAGMA user_version != 1`, the app exits with a schema version error (by design). Fix by setting `user_version=1` or applying a planned migration.
- **Unsigned binaries**: Fresh PyInstaller executables may trigger antivirus warnings. Whitelist locally or code‑sign for distribution.
- **Single‑user CLI focus**: No concurrency control for multi‑process access; simultaneous writes may contend.
- **Date validation edge cases**: Common formats are validated; extreme edge cases may require review.
- **No GUI**: The brief requires a CLI; there is no graphical UI.

---

## License
This project is released under the **MIT License**. You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, subject to the conditions in the `LICENSE` file. The software is provided **“as is”**, without warranty of any kind.

**SPDX‑Identifier:** MIT  
See the bundled `LICENSE` file for the full text.

---

## Credits
**Developer:** Fredierick “Fred” Saladas — GitHub: @ciastirfry  
**Course/Context:** Master of Software Engineering (Yoobee) — *Professional Software Engineering: Car Rental System*  
**Acknowledgments:** Classmates and instructors for guidance and feedback.

If you use or extend this project, please retain attribution. Contributions and suggestions are welcome.

