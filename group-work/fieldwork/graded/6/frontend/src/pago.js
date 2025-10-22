/**
 * CHECKOUT DE MERCADO PAGO - JAVASCRIPT
 * Maneja validaciones, formateo y envío de pagos
 */

// ========== CONSTANTES ==========
const CARD_BRANDS = {
    visa: /^4/,
    mastercard: /^5[1-5]/,
    amex: /^3[47]/,
    discover: /^6(?:011|5)/
};

const CARD_ICONS = {
    visa: '💳',
    mastercard: '💳',
    amex: '💳',
    discover: '💳',
    default: '💳'
};

// ========== VARIABLES GLOBALES ==========
let compraData = {
    compra_id: null,
    preference_id: null,
    total: 0,
    cantidad: 0
};

// ========== INICIALIZACIÓN ==========
document.addEventListener('DOMContentLoaded', () => {
    cargarDatosCompra();
    configurarEventListeners();
    autoFillTestData(); // Para testing
});

// ========== CARGAR DATOS DE COMPRA ==========
function cargarDatosCompra() {
    const urlParams = new URLSearchParams(window.location.search);
    compraData.preference_id = urlParams.get('preference_id');
    compraData.compra_id = urlParams.get('compra_id');
    
    // Obtener datos de sessionStorage (pasados desde el frontend principal)
    const datosGuardados = sessionStorage.getItem('checkout_data');
    if (datosGuardados) {
        const datos = JSON.parse(datosGuardados);
        compraData.total = datos.total || 0;
        compraData.cantidad = datos.cantidad || 0;
        
        actualizarResumenCompra();
    } else {
        // Valores por defecto si no hay datos
        compraData.total = 10000;
        compraData.cantidad = 2;
        actualizarResumenCompra();
    }
}

function actualizarResumenCompra() {
    document.getElementById('cantidad-entradas').textContent = 
        `${compraData.cantidad} entrada(s)`;
    document.getElementById('total-pago').textContent = 
        `$${compraData.total.toLocaleString('es-AR')}`;
}

// ========== EVENT LISTENERS ==========
function configurarEventListeners() {
    const form = document.getElementById('payment-form');
    const numeroTarjeta = document.getElementById('numero-tarjeta');
    const vencimientoMes = document.getElementById('vencimiento-mes');
    const vencimientoAnio = document.getElementById('vencimiento-anio');
    const cvv = document.getElementById('cvv');
    const titular = document.getElementById('titular');
    
    // Formateo automático de número de tarjeta
    numeroTarjeta.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\s/g, '');
        let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
        e.target.value = formattedValue;
        
        detectarMarcaTarjeta(value);
    });
    
    // Solo números en vencimiento
    vencimientoMes.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/\D/g, '');
        if (e.target.value.length === 2 && parseInt(e.target.value) > 0) {
            vencimientoAnio.focus();
        }
    });
    
    vencimientoAnio.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/\D/g, '');
    });
    
    // Solo números en CVV
    cvv.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/\D/g, '');
    });
    
    // Capitalizar titular
    titular.addEventListener('input', (e) => {
        e.target.value = e.target.value.toUpperCase();
    });
    
    // Submit del formulario
    form.addEventListener('submit', handleSubmit);
}

// ========== DETECTAR MARCA DE TARJETA ==========
function detectarMarcaTarjeta(numero) {
    const cardBrandElement = document.getElementById('card-brand');
    
    for (const [brand, pattern] of Object.entries(CARD_BRANDS)) {
        if (pattern.test(numero)) {
            cardBrandElement.textContent = CARD_ICONS[brand];
            return;
        }
    }
    
    cardBrandElement.textContent = CARD_ICONS.default;
}

// ========== VALIDACIONES ==========
function validarNumeroTarjeta(numero) {
    const clean = numero.replace(/\s/g, '');
    
    if (clean.length < 13 || clean.length > 19) {
        return false;
    }
    
    // Algoritmo de Luhn
    let sum = 0;
    let isEven = false;
    
    for (let i = clean.length - 1; i >= 0; i--) {
        let digit = parseInt(clean.charAt(i), 10);
        
        if (isEven) {
            digit *= 2;
            if (digit > 9) {
                digit -= 9;
            }
        }
        
        sum += digit;
        isEven = !isEven;
    }
    
    return (sum % 10) === 0;
}

function validarVencimiento(mes, anio) {
    const mesInt = parseInt(mes, 10);
    const anioInt = parseInt(anio, 10);
    
    if (mesInt < 1 || mesInt > 12) {
        return false;
    }
    
    const now = new Date();
    const currentYear = now.getFullYear() % 100;
    const currentMonth = now.getMonth() + 1;
    
    if (anioInt < currentYear) {
        return false;
    }
    
    if (anioInt === currentYear && mesInt < currentMonth) {
        return false;
    }
    
    return true;
}

function validarCVV(cvv) {
    return /^\d{3,4}$/.test(cvv);
}

// ========== MANEJO DE SUBMIT ==========
async function handleSubmit(e) {
    e.preventDefault();
    
    // Obtener valores
    const numeroTarjeta = document.getElementById('numero-tarjeta').value;
    const titular = document.getElementById('titular').value;
    const vencimientoMes = document.getElementById('vencimiento-mes').value;
    const vencimientoAnio = document.getElementById('vencimiento-anio').value;
    const cvv = document.getElementById('cvv').value;
    
    // Validaciones
    if (!validarNumeroTarjeta(numeroTarjeta)) {
        mostrarError('Número de tarjeta inválido');
        return;
    }
    
    if (!validarVencimiento(vencimientoMes, vencimientoAnio)) {
        mostrarError('Fecha de vencimiento inválida');
        return;
    }
    
    if (!validarCVV(cvv)) {
        mostrarError('Código de seguridad inválido');
        return;
    }
    
    if (titular.trim().length < 3) {
        mostrarError('Nombre del titular inválido');
        return;
    }
    
    // Preparar datos
    const datosPago = {
        numero_tarjeta: numeroTarjeta.replace(/\s/g, ''),
        titular: titular.trim(),
        vencimiento_mes: vencimientoMes,
        vencimiento_anio: vencimientoAnio,
        cvv: cvv,
        monto: compraData.total,
        compra_id: compraData.compra_id,
        preference_id: compraData.preference_id
    };
    
    // Enviar pago
    await procesarPago(datosPago);
}

// ========== PROCESAR PAGO ==========
async function procesarPago(datosPago) {
    const btnPagar = document.getElementById('btn-pagar');
    const btnText = btnPagar.querySelector('.btn-text');
    const btnSpinner = btnPagar.querySelector('.btn-spinner');
    
    // Deshabilitar botón y mostrar spinner
    btnPagar.disabled = true;
    btnText.textContent = 'Procesando...';
    btnSpinner.classList.remove('oculto');
    
    mostrarMensaje('Procesando tu pago de forma segura...', 'loading');
    
    try {
        const response = await fetch('http://127.0.0.1:5000/procesar-pago', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(datosPago)
        });
        
        const resultado = await response.json();
        
        if (resultado.status === 'approved') {
            mostrarExito('¡Pago aprobado! Redirigiendo...');
            
            // Guardar datos para la página de éxito
            sessionStorage.setItem('pago_resultado', JSON.stringify(resultado));
            
            // Redirigir después de 2 segundos
            setTimeout(() => {
                window.location.href = `/pago-exitoso?transaction_id=${resultado.transaction_id}`;
            }, 2000);
            
        } else if (resultado.status === 'pending') {
            mostrarAdvertencia('Pago pendiente de autorización');
            
            setTimeout(() => {
                window.location.href = `/pago-pendiente?transaction_id=${resultado.transaction_id}`;
            }, 2000);
            
        } else {
            mostrarError(resultado.message || 'Pago rechazado. Intenta con otra tarjeta.');
            
            // Re-habilitar botón
            btnPagar.disabled = false;
            btnText.textContent = 'Pagar';
            btnSpinner.classList.add('oculto');
        }
        
    } catch (error) {
        console.error('Error al procesar pago:', error);
        mostrarError('Error de conexión. Por favor, intenta nuevamente.');
        
        // Re-habilitar botón
        btnPagar.disabled = false;
        btnText.textContent = 'Pagar';
        btnSpinner.classList.add('oculto');
    }
}

// ========== MENSAJES DE ESTADO ==========
function mostrarMensaje(texto, tipo) {
    const mensaje = document.getElementById('mensaje-estado');
    mensaje.textContent = texto;
    mensaje.className = `mensaje-estado ${tipo}`;
}

function mostrarError(texto) {
    mostrarMensaje('❌ ' + texto, 'error');
}

function mostrarExito(texto) {
    mostrarMensaje('✅ ' + texto, 'success');
}

function mostrarAdvertencia(texto) {
    mostrarMensaje('⚠️ ' + texto, 'loading');
}

// ========== AUTO-FILL PARA TESTING ==========
function autoFillTestData() {
    // Solo en modo desarrollo
    const isDev = window.location.hostname === 'localhost' || 
                  window.location.hostname === '127.0.0.1';
    
    if (!isDev) return;
    
    // Llenar con tarjeta de prueba aprobada
    setTimeout(() => {
        document.getElementById('numero-tarjeta').value = '4509 9535 6623 3704';
        document.getElementById('titular').value = 'JUAN PEREZ';
        document.getElementById('vencimiento-mes').value = '12';
        document.getElementById('vencimiento-anio').value = '28';
        document.getElementById('cvv').value = '123';
        
        detectarMarcaTarjeta('4509953566233704');
    }, 500);
}

// ========== HELPERS ==========
function limpiarFormulario() {
    document.getElementById('payment-form').reset();
    document.getElementById('card-brand').textContent = CARD_ICONS.default;
}
