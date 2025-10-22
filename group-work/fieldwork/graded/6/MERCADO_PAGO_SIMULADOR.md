# 💳 Simulador de Mercado Pago - Instrucciones

## ✅ ¡Todo Implementado!

Se ha creado un **simulador completo de Mercado Pago** que incluye:

### 🎯 Características Implementadas

1. **Backend (`api/mercadopago_service.py`)**
   - ✅ Validación de tarjetas con algoritmo de Luhn
   - ✅ Generación de IDs únicos de transacción
   - ✅ Simulación de estados: `approved`, `rejected`, `pending`
   - ✅ Validación de CVV, fecha de vencimiento
   - ✅ Historial de transacciones

2. **Frontend Checkout (`frontend/pago.html`)**
   - ✅ Diseño tipo Mercado Pago (azul, logo, badges de seguridad)
   - ✅ Formulario de tarjeta con validación en tiempo real
   - ✅ Detección automática de marca de tarjeta (Visa, Mastercard, Amex)
   - ✅ Resumen de compra con total
   - ✅ Auto-fill con datos de prueba (en desarrollo)
   - ✅ Responsive (funciona en mobile)

3. **Integración Flask (`app.py`)**
   - ✅ Ruta `/pago-mercadopago` - Página de checkout
   - ✅ Ruta `/procesar-pago` - Procesa pagos con tarjeta
   - ✅ Ruta `/pago-exitoso` - Confirmación de pago
   - ✅ Ruta `/pago-pendiente` - Para pagos pendientes
   - ✅ Redirección automática desde formulario principal

4. **Tests (`test/test_mercado_pago.py`)**
   - ✅ **20 tests** cubriendo:
     - Integración con mocks
     - Servicio real de simulación
     - Validaciones de tarjeta
     - Procesamiento de pagos
     - Estados aprobado/rechazado/pendiente

---

## 🚀 Cómo Probarlo

### 1. Iniciar el servidor (si no está corriendo)

```bash
cd "c:\Users\sueldoalvaro\Documents\UTN\Cuarto año\ISW\isw-2025-2c-g14\group-work\fieldwork\graded\6"
python app.py
```

### 2. Abrir el navegador

Ir a: **http://127.0.0.1:5000**

### 3. Realizar una compra con TARJETA

1. **Llenar formulario principal:**
   - Fecha: cualquier sábado futuro
   - Cantidad: 2 visitantes (ya viene pre-llenado)
   - Edades y tipos: ya vienen auto-completados
   - **Medio de pago: TARJETA** ⚠️ (importante)

2. **Hacer clic en "Comprar"**
   - Se abre modal de confirmación
   - Verificar datos
   - Clic en "Confirmar Compra"

3. **Serás redirigido al checkout de Mercado Pago**
   - URL: `http://127.0.0.1:5000/pago-mercadopago`
   - Verás un formulario estilo MP (azul, seguro)

4. **El formulario ya viene PRE-LLENADO con:**
   - Tarjeta: `4509 9535 6623 3704` (aprobada)
   - Titular: `JUAN PEREZ`
   - Vencimiento: `12/28`
   - CVV: `123`

5. **Hacer clic en "Pagar"**
   - Verás "Procesando..." con spinner
   - Simulación de demora de red (0.5 segundos)
   - Redirige a página de éxito

6. **¡Pago Exitoso!** ✅
   - Muestra ID de transacción
   - **Recibirás email de confirmación** en `alvarosueldoc@gmail.com`

---

## 🧪 Tarjetas de Prueba

El simulador incluye estas tarjetas de prueba:

### ✅ Aprobadas (Status: `approved`)
```
4509 9535 6623 3704  (Visa)
5031 4332 1540 6351  (Mastercard)
3711 8030 3259 4270  (Amex)
```

### ❌ Rechazadas (Status: `rejected`)
```
4111 1111 1111 1111  (Fondos insuficientes)
5555 5555 5555 4444  (Tarjeta expirada)
```

### ⏳ Pendientes (Status: `pending`)
```
4000 0000 0000 0002  (Requiere autorización)
```

**Para cualquier tarjeta:**
- CVV: cualquier 3 dígitos (ej: `123`)
- Vencimiento: cualquier fecha futura (ej: `12/28`)
- Titular: cualquier nombre (ej: `JUAN PEREZ`)

---

## 📊 Tests

Ejecutar todos los tests:

```bash
pytest test\test_mercado_pago.py -v
```

**Resultado esperado:** ✅ 20 passed

---

## 🎨 Flujo Completo

```
Usuario en index.html
    ↓
Selecciona medio de pago: TARJETA
    ↓
Clic en "Comprar" → Modal de confirmación
    ↓
Clic en "Confirmar Compra"
    ↓
POST /comprar → Backend crea compra en DB
    ↓
Backend retorna: status="redireccion" + checkout_url
    ↓
Frontend redirige a: /pago-mercadopago
    ↓
Usuario ve checkout simulado de MP (pre-llenado)
    ↓
Clic en "Pagar" → POST /procesar-pago
    ↓
Backend valida tarjeta (Luhn) y procesa
    ↓
Retorna status: approved/rejected/pending
    ↓
Frontend redirige según resultado:
    ✅ /pago-exitoso  (con email)
    ❌ /pago-rechazado
    ⏳ /pago-pendiente
```

---

## 📁 Archivos Creados/Modificados

### Nuevos archivos:
- ✅ `api/mercadopago_service.py` - Servicio de simulación (300+ líneas)
- ✅ `frontend/pago.html` - Página de checkout (200+ líneas)
- ✅ `frontend/src/pago.css` - Estilos del checkout (400+ líneas)
- ✅ `frontend/src/pago.js` - Lógica del checkout (250+ líneas)

### Archivos modificados:
- ✅ `app.py` - Agregadas rutas `/pago-mercadopago`, `/procesar-pago`, etc.
- ✅ `frontend/src/main.js` - Manejo de redirección a MP
- ✅ `test/test_mercado_pago.py` - 20 tests para el simulador

---

## 🔒 Seguridad

El simulador incluye:
- ✅ Validación Luhn (algoritmo de tarjetas real)
- ✅ Validación de CVV (3-4 dígitos)
- ✅ Validación de fecha de vencimiento
- ✅ Sanitización de inputs
- ✅ IDs únicos por transacción
- ✅ Simulación de tiempo de procesamiento

---

## 💡 Ventajas del Simulador vs SDK Real

| Simulador Propio | SDK Real de MP |
|-----------------|----------------|
| ✅ No requiere cuenta de MP | ❌ Requiere cuenta + credenciales |
| ✅ Testing fácil y rápido | ❌ Testing complejo con sandbox |
| ✅ Control total del flujo | ❌ Flujo manejado por MP |
| ✅ Sin webhooks externos | ❌ Requiere webhook público |
| ✅ Ideal para proyectos académicos | ✅ Necesario para producción |
| ✅ Validaciones reales (Luhn) | ✅ Validaciones reales |

---

## 🎓 Para el Proyecto Académico

Este simulador demuestra que entiendes:
- ✅ Flujo de pagos con tarjeta
- ✅ Validaciones de datos sensibles
- ✅ Redirección entre páginas
- ✅ Manejo de estados de pago
- ✅ Integración frontend-backend
- ✅ Testing exhaustivo

---

## 📞 Próximos Pasos

Si quieres mejorar aún más:
1. **Agregar timeout de preferencia** (preferencia expira en X minutos)
2. **Guardar estado de pago en DB** (campo `estado_pago` en compras)
3. **Enviar email diferente según estado** (aprobado/rechazado/pendiente)
4. **Agregar cuotas** (1, 3, 6, 12 cuotas)
5. **Integrar SDK real** (para deploy en producción)

---

## ✨ ¡Listo para Usar!

El servidor ya está corriendo en **http://127.0.0.1:5000**

**Prueba el flujo completo ahora mismo:**
1. Abre el navegador
2. Selecciona TARJETA como medio de pago
3. Confirma la compra
4. Completa el pago en el checkout simulado
5. ¡Recibe tu email de confirmación!

🎉 **Todo funcionando perfectamente**
