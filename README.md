# Rural Household PMT Calculator

Calculates a **Proxy Means Test (PMT)** score and poverty level for every household in an Excel survey extract, and writes the results to a new Excel workbook.

---

## 1. What you need

- **Python 3.11 or newer** — download from <https://www.python.org/downloads/>.
  On Windows, tick **"Add python.exe to PATH"** during installation.
- The project files (this folder), either cloned with Git or copied as a ZIP.
- One or more input Excel files (`.xlsx`) in the format described in [section 4](#4-input-file-format).

Check that Python is installed by opening a terminal (PowerShell on Windows, Terminal on macOS/Linux) and running:

```bash
python --version
```

On macOS/Linux you may need to use `python3` instead of `python` in every command below.

---

## 2. One-time setup

Open a terminal **in the project folder** (the folder containing `main.py`), then:

### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> If PowerShell says running scripts is disabled, run this once and try again:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

When the virtual environment is active, your prompt starts with `(venv)`.
You only need to create it and install packages once. In later sessions, just run the **activate** line again.

---

## 3. Running the tool

Make sure the virtual environment is active (`(venv)` in your prompt) and you are in the project folder.

### Option A — Batch mode (process a whole folder)

1. Put your input workbooks in the `Input` folder (create it if it doesn't exist).
2. Run:

   ```bash
   python main.py
   ```

3. Each file `Input/<name>.xlsx` produces `Output/Output_<name>.xlsx`. The `Output` folder is created automatically.

Notes:
- Only files directly inside `Input/` are processed — subfolders (e.g. `Input/Archive`) are ignored.
- Files whose names start with `Output_` are skipped.
- Existing output files with the same name are **overwritten**. Close them in Excel first, otherwise you'll get a `PermissionError`.

### Option B — Single file

```bash
python main.py path/to/input.xlsx path/to/output.xlsx
```

Example:

```bash
python main.py Input/Telle_Extract.xlsx Output/Telle_results.xlsx
```

---

## 4. Input file format

Each input workbook must contain **two sheets** with these exact names:

| Sheet | Contents |
|---|---|
| `EnumeratedHouseholds` | One row per household |
| `EnumeratedHouseholdMembers` | One row per household member |

Both sheets must have a `HouseholdId` column, which links members to their household.

**`EnumeratedHouseholds`** columns used:

- `HouseholdId`
- `Household Information_# Stoves`
- `Household Information_# Radios`
- `Household Information_# Sheep`
- `Household Information_# Cattle`
- `Household Information_# Horses`
- `Household Information_# Poultry`

**`EnumeratedHouseholdMembers`** columns used:

- `HouseholdId`, `HouseholdMemberId`, `HouseholdMember_Status`
- `Household Information_Heating Fuel`
- `Household Roster_Highest LOE`
- `Household Roster_Main Activity`
- `Household Roster_Living Elsewhere`
- `Household Roster_Where Member Living`
- `Household Roster_Date of Birth`, `Household Roster_Age in Years`

Values may be either the text labels from the survey (e.g. `Gas`, `Primary Complete (Grade 7)`) or their numeric codes. The full label-to-code mappings are in `constants.py`. Blank cells and `9998 NO VALUE` are treated as missing.

---

## 5. Understanding the output

Each output workbook has two sheets:

- **`PMT_Results`** — one row per household with:
  - the inputs that went into the model (household size, education, employment, assets, …),
  - the derived dummy variables (`var_*`),
  - `PMT_Score` and `Poverty_Level` (`Poor` if the score is below 361, otherwise `Better-Off`),
  - `Parameter_Status` / `Missing` / `Missing_Reason` — flags households where some data was missing, and what was missing,
  - `Used_Values` — the raw values actually used in the calculation, for auditing.
- **`Summary`** — total households, number classified as poor, and number with missing data.

Model coefficients, the poverty cut-off and other business rules are all defined in `constants.py`.

---

## 6. Troubleshooting

| Problem | Fix |
|---|---|
| `'python' is not recognized…` | Python isn't on your PATH. Reinstall with "Add to PATH" ticked, or use `py` instead of `python` on Windows. |
| `ModuleNotFoundError: No module named 'pandas'` | The virtual environment isn't active, or packages weren't installed. Activate it and run `pip install -r requirements.txt`. |
| `ValueError: Worksheet named '…' not found` | The input file is missing the `EnumeratedHouseholds` or `EnumeratedHouseholdMembers` sheet, or it's named differently. |
| `KeyError: 'HouseholdId'` (or another column) | A required column is missing or misspelled — compare against [section 4](#4-input-file-format). |
| `PermissionError` when writing output | The output file is open in Excel. Close it and run again. |
| `No input files found in 'Input'.` | The `Input` folder is empty or missing, or you're not running the command from the project folder. |
