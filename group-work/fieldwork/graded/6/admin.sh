#!/usr/bin/env bash
# ========================================
# Admin de Base de Datos (Git Bash wrapper)
# Ejecuta el administrador desde cualquier carpeta
# Uso: ./admin.sh stats | consultar | limpiar | limpiar-todo | buscar <id> | borrar-compra <id> | borrar-usuario <id>
# ========================================

set -euo pipefail

# Ir al directorio donde está este script
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# Entrar a la carpeta del administrador
cd "$SCRIPT_DIR/db_admin" || {
  echo "[ERROR] No se encontró la carpeta db_admin relativa a este archivo: $SCRIPT_DIR/db_admin" >&2
  exit 1
}

# Elegir intérprete de Python disponible (Windows/Git Bash friendly)
choose_python() {
  if command -v python >/dev/null 2>&1; then
    echo "python"
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    echo "python3"
    return 0
  fi
  if command -v py >/dev/null 2>&1; then
    echo "py -3"
    return 0
  fi
  return 1
}

PY_CMD="$(choose_python || true)"
if [[ -z "${PY_CMD:-}" ]]; then
  echo "[ERROR] No se encontró un intérprete de Python. Instala Python 3 y asegúrate que 'python', 'python3' o 'py' esté en PATH." >&2
  exit 1
fi

# Ejecutar el script de Python con los argumentos que reciba este wrapper
exec $PY_CMD admin_db.py "$@"
