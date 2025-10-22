# EcoHarmony Park – Grado 6

Pequeña app Flask + frontend para compras de entradas con simulador de Mercado Pago y envío de email de confirmación.

## Estructura principal

- `api/` — Lógica de dominio y servicios (compras, entradas, Mercado Pago simulado, email)
- `frontend/` — Sitio y checkout (index, pago)
- `db_admin/` — Administrador de base de datos (consultas, estadísticas, limpieza, borrado selectivo)
- `tools/manual-tests/` — Scripts de pruebas manuales (p.ej., envío de email real)
- `instance/` — Base de datos SQLite local (no se versiona)
- `test/` — Tests automatizados de la app

## Administración de la base de datos

Wrappers desde la raíz de este módulo (graded/6):

- PowerShell / CMD:
  - `./admin.bat stats`
  - `./admin.bat consultar`
  - `./admin.bat limpiar`

- Git Bash:
  - `./admin.sh stats`
  - `./admin.sh consultar`
  - `./admin.sh limpiar`

O directo con Python:

- `python db_admin/admin_db.py stats|consultar|limpiar|limpiar-todo|buscar <id>`

## Prueba de envío de email real

Lee `INSTRUCCIONES_GMAIL.md` y luego ejecutá el script manual:

- Git Bash / WSL: `python tools/manual-tests/enviar_email_real.py`
- PowerShell / CMD: `python .\tools\manual-tests\enviar_email_real.py`

## Housekeeping / buenas prácticas

- `.gitignore` ya excluye:
  - `venv/`, `__pycache__/`, `.pytest_cache/`, `.env`
  - `instance/` y cualquier `*.db`/`*.sqlite`
- No subas credenciales reales (`.env`) ni bases de datos locales (`instance/*.db`).
- Usá los wrappers `admin.bat` / `admin.sh` en lugar de scripts antiguos.
- Para pruebas manuales, usá `tools/manual-tests/` (no mezclar con `test/`).
- Si necesitás limpiar artefactos locales: borrar `__pycache__/`, `.pytest_cache/`, `frontend/dist/` si existiera.

## Dependencias

Instalá dependencias de Python en tu entorno/venv:

```powershell
# PowerShell
python -m pip install -r requirements.txt
```

```bash
# Git Bash / WSL
python -m pip install -r requirements.txt
```
