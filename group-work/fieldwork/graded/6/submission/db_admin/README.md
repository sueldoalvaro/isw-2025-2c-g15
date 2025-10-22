# 🗃️ Administrador de Base de Datos

Herramienta completa para administrar la base de datos del sistema EcoHarmony Park.

## 📁 Ubicación

```
db_admin/
├── admin_db.py      # Script principal
└── README.md        # Esta documentación
```

---

## 🚀 Uso Rápido

### Wrappers desde la raíz del proyecto

Si estás en Windows y quieres ejecutar desde cualquier carpeta:

- PowerShell / CMD:
  - `./admin.bat stats`
  - `./admin.bat consultar`

- Git Bash:
  - `./admin.sh stats`
  - `./admin.sh consultar`

Ambos wrappers cambian al directorio correcto y ejecutan `db_admin/admin_db.py` por ti.

### Menú Interactivo (Recomendado)
```bash
cd db_admin
python admin_db.py
```

### Comandos Directos
```bash
# Ver todos los registros
python admin_db.py consultar

# Ver estadísticas
python admin_db.py stats

# Buscar una compra
python admin_db.py buscar 5

# Limpiar compras y entradas (mantener usuarios)
python admin_db.py limpiar

# Limpiar TODO (incluyendo usuarios)
python admin_db.py limpiar-todo

# Borrar una compra específica
python admin_db.py borrar-compra 5

# Borrar un usuario específico
python admin_db.py borrar-usuario 2

# Ver ayuda
python admin_db.py help
```

---

## 📋 Funciones Disponibles

### 1. **Consultar Registros**

#### `consultar`
Muestra todos los registros de:
- ✅ Usuarios (ID, email, nombre)
- ✅ Compras (ID, usuario, fecha, medio de pago)
- ✅ Entradas (edad, tipo, precio)

**Ejemplo:**
```bash
python admin_db.py consultar
```

**Salida:**
```
═══════════════════════════════════════════════════════
👥 USUARIOS
═══════════════════════════════════════════════════════
  ID: 1
  Email: cliente@demo.com
  Nombre: Cliente Demo
  ------------------------------------------------------
  
🛒 COMPRAS
═══════════════════════════════════════════════════════
  ID Compra: 5
  Usuario: Alvaro Sueldo (alvarosueldoc@gmail.com)
  Fecha visita: 2025-11-02
  Cantidad: 2
  Medio de pago: TARJETA
  Entradas:
    • Edad 30 años - REGULAR ($5,000)
    • Edad 8 años - VIP ($10,000)
  TOTAL: $15,000
```

---

### 2. **Estadísticas**

#### `stats`
Muestra resumen estadístico:
- 📊 Total de usuarios, compras, entradas
- 💳 Distribución por medio de pago
- 🎫 Distribución por tipo de entrada
- 💰 Total recaudado
- 📅 Última compra

**Ejemplo:**
```bash
python admin_db.py stats
```

**Salida:**
```
═══════════════════════════════════════════════════════
📊 ESTADÍSTICAS DE LA BASE DE DATOS
═══════════════════════════════════════════════════════

📈 RESUMEN GENERAL:
   • Total de usuarios: 2
   • Total de compras: 13
   • Total de entradas: 25
   • Promedio entradas/compra: 1.9

💳 MEDIOS DE PAGO:
   • Efectivo: 6 (46.2%)
   • Tarjeta: 7 (53.8%)

🎫 TIPOS DE ENTRADAS:
   • Regular: 12 ($60,000)
   • VIP: 13 ($130,000)

💰 RECAUDACIÓN:
   • Total: $190,000
   • Promedio por compra: $14,615
```

---

### 3. **Buscar Compra**

#### `buscar <id>`
Muestra el detalle completo de una compra específica.

**Ejemplo:**
```bash
python admin_db.py buscar 5
```

---

### 4. **Limpiar Base de Datos**

#### `limpiar` (Mantiene usuarios)
Elimina todas las compras y entradas, pero **conserva los usuarios**.

**Uso recomendado:** Cuando quieres resetear las ventas pero mantener los clientes.

**Ejemplo:**
```bash
python admin_db.py limpiar
```

**¿Estás seguro?** Requiere confirmación escribiendo `SI`

**Resultado:**
```
✅ Limpieza completada:
   • 13 compras eliminadas
   • 25 entradas eliminadas
   • 2 usuarios conservados
   • IDs reseteados a 1
```

---

#### `limpiar-todo` (Elimina TODO)
Elimina **todos los registros** incluyendo usuarios.

**⚠️ PELIGRO:** Esta acción borra TODO. Úsala con cuidado.

**Ejemplo:**
```bash
python admin_db.py limpiar-todo
```

**¿Estás seguro?** Requiere confirmación escribiendo `SI BORRAR TODO`

---

### 5. **Borrado Selectivo**

#### `borrar-compra <id>`
Elimina una compra específica y sus entradas asociadas.

**Ejemplo:**
```bash
python admin_db.py borrar-compra 5
```

**Confirmación:** Requiere `S` para confirmar

---

#### `borrar-usuario <id>`
Elimina un usuario y **todas sus compras y entradas**.

**Ejemplo:**
```bash
python admin_db.py borrar-usuario 2
```

**Confirmación:** Requiere `S` para confirmar

**Resultado:**
```
✅ Usuario #2 eliminado correctamente
   • 5 compra(s) eliminada(s)
   • 10 entrada(s) eliminada(s)
```

---

## 🎯 Casos de Uso Comunes

### Resetear ventas para testing
```bash
python admin_db.py limpiar
```

### Ver resumen rápido
```bash
python admin_db.py stats
```

### Verificar una compra específica
```bash
python admin_db.py buscar 3
```

### Eliminar compra duplicada
```bash
python admin_db.py borrar-compra 8
```

### Empezar completamente de cero
```bash
python admin_db.py limpiar-todo
```

---

## 📊 Menú Interactivo

Si ejecutas sin argumentos, verás un menú completo:

```bash
python admin_db.py
```

**Opciones del menú:**
```
═══════════════════════════════════════════════════════
🗃️  ADMINISTRADOR DE BASE DE DATOS - EcoHarmony Park
═══════════════════════════════════════════════════════

📋 CONSULTAS:
  1. Ver todos los registros
  2. Ver estadísticas
  3. Buscar compra por ID

🗑️  LIMPIEZA:
  4. Limpiar compras y entradas (mantener usuarios)
  5. Limpiar TODO (incluyendo usuarios)

❌ BORRADO SELECTIVO:
  6. Borrar una compra específica
  7. Borrar un usuario específico

  0. Salir
═══════════════════════════════════════════════════════
```

---

## 🔒 Seguridad

- ✅ Todas las operaciones destructivas requieren confirmación
- ✅ Los IDs se validan antes de borrar
- ✅ Se muestra resumen antes de eliminar
- ✅ Mensajes claros de lo que se va a borrar

---

## 💡 Tips

1. **Antes de limpiar**, ejecuta `stats` para ver qué hay
2. **Para testing**, usa `limpiar` (mantiene usuarios)
3. **Para producción**, NUNCA uses `limpiar-todo`
4. **Busca antes de borrar** para verificar el ID correcto
5. **Usa el menú interactivo** si no recuerdas los comandos

---

## 🆘 Ayuda

```bash
python admin_db.py help
```

---

**¡Todo en un solo archivo y carpeta!** 🎉
