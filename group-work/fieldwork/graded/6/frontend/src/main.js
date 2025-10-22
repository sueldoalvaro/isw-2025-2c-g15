const form = document.getElementById('purchase-form');
const alertContainer = document.getElementById('alert-container');
const quantityInput = document.getElementById('quantity');
const visitorsContainer = document.getElementById('visitors-container');
const currentUserEl = document.getElementById('current-user');

// --- CARGAR USUARIO ACTUAL (DEMO) ---
async function cargarUsuarioActual() {
    try {
        const res = await fetch('http://127.0.0.1:5000/usuario-actual');
        if (!res.ok) return;
        const usuario = await res.json();
        if (usuario && usuario.email) {
            currentUserEl.textContent = `Comprando como: ${usuario.nombre} (${usuario.email})`;
            currentUserEl.style.display = 'block';
            sessionStorage.setItem('usuario_actual', JSON.stringify(usuario));
        }
    } catch (e) {
        // Silencioso: si no carga, no bloquea la compra
        console.warn('No se pudo cargar usuario actual', e);
    }
}

// Iniciar carga de usuario actual en cuanto carga el script
cargarUsuarioActual();

// --- LÓGICA PARA INPUTS DINÁMICOS DE VISITANTES (EDAD + TIPO) ---
function generateVisitorInputs(quantity) {
    visitorsContainer.innerHTML = ''; // Limpiar contenedor
    
    // Arrays de edades y tipos de prueba
    const testAges = [30, 8, 25, 15, 45, 12, 35, 22, 18, 50];
    const testTypes = ['REGULAR', 'VIP', 'REGULAR', 'REGULAR', 'VIP', 'REGULAR', 'VIP', 'REGULAR', 'VIP', 'REGULAR'];
    
    for (let i = 1; i <= quantity; i++) {
        const card = document.createElement('div');
        card.className = 'visitor-card';
        
        const title = document.createElement('h3');
        title.textContent = `Visitante ${i}`;
        card.appendChild(title);
        
        // Input de edad
        const ageGroup = document.createElement('div');
        ageGroup.className = 'input-group';
        
        const ageLabel = document.createElement('label');
        ageLabel.textContent = 'Edad:';
        
        const ageInput = document.createElement('input');
        ageInput.type = 'number';
        ageInput.className = 'age-input';
        ageInput.min = '1';
        ageInput.required = true;
        ageInput.dataset.visitorIndex = i - 1;
        // Pre-cargar edad de prueba
        ageInput.value = testAges[i - 1] || (20 + Math.floor(Math.random() * 30));
        
        ageGroup.appendChild(ageLabel);
        ageGroup.appendChild(ageInput);
        card.appendChild(ageGroup);
        
        // Selector de tipo de pase
        const typeGroup = document.createElement('div');
        typeGroup.className = 'input-group';
        
        const typeLabel = document.createElement('label');
        typeLabel.textContent = 'Tipo de Pase:';
        
        const typeSelect = document.createElement('select');
        typeSelect.className = 'pass-type-select';
        typeSelect.required = true;
        typeSelect.dataset.visitorIndex = i - 1;
        
        const optionRegular = document.createElement('option');
        optionRegular.value = 'REGULAR';
        optionRegular.textContent = 'Regular ($5,000)';
        
        const optionVIP = document.createElement('option');
        optionVIP.value = 'VIP';
        optionVIP.textContent = 'VIP ($10,000)';
        
        typeSelect.appendChild(optionRegular);
        typeSelect.appendChild(optionVIP);
        
        // Pre-seleccionar tipo de prueba
        typeSelect.value = testTypes[i - 1] || 'REGULAR';
        
        typeGroup.appendChild(typeLabel);
        typeGroup.appendChild(typeSelect);
        card.appendChild(typeGroup);
        
        visitorsContainer.appendChild(card);
    }
}

quantityInput.addEventListener('input', () => {
    const quantity = parseInt(quantityInput.value, 10) || 0;
    if (quantity > 0 && quantity <= 10) {
        generateVisitorInputs(quantity);
    } else {
        visitorsContainer.innerHTML = '';
    }
});

const defaultQuantity = 2;
quantityInput.value = defaultQuantity;
generateVisitorInputs(defaultQuantity); // Generar inputs iniciales con valores de prueba

const today = new Date();
const dayOfWeek = today.getDay();
const daysUntilSaturday = (6 - dayOfWeek + 7) % 7;
const nextSaturday = new Date(new Date().setDate(today.getDate() + daysUntilSaturday));
document.getElementById('visit-date').value = nextSaturday.toISOString().split('T')[0];

// --- LÓGICA PARA ALTERNAR MENSAJES DE PAGO ---
const paymentRadios = document.querySelectorAll('input[name="payment-method"]');
const infoEfectivo = document.getElementById('info-efectivo');
const infoTarjeta = document.getElementById('info-tarjeta');

function updatePaymentInfo() {
    const selectedPayment = document.querySelector('input[name="payment-method"]:checked').value;
    
    if (selectedPayment === 'EFECTIVO') {
        infoEfectivo.style.display = 'block';
        infoTarjeta.style.display = 'none';
    } else {
        infoEfectivo.style.display = 'none';
        infoTarjeta.style.display = 'block';
    }
}

// Inicializar con el valor por defecto
updatePaymentInfo();

// Agregar event listeners a los radios
paymentRadios.forEach(radio => {
    radio.addEventListener('change', updatePaymentInfo);
});


// Variables para el modal
const modal = document.getElementById('confirmation-modal');
const confirmBtn = document.getElementById('confirm-btn');
const cancelBtn = document.getElementById('cancel-btn');
const purchaseSummary = document.getElementById('purchase-summary');
let pendingPurchaseData = null;

form.addEventListener('submit', function (event) {
    event.preventDefault();
    alertContainer.style.display = 'none';

    const ageInputs = document.querySelectorAll('.age-input');
    const passSelects = document.querySelectorAll('.pass-type-select');

    const formData = new FormData(form);
    const data = {
        fecha: formData.get('visit-date'),
        entradas: Array.from(ageInputs).map((input, index) => ({ 
            edad: parseInt(input.value, 10),
            tipoEntrada: passSelects[index].value
        })),
        medioPago: formData.get('payment-method'),
    };

    // Mostrar modal de confirmación con resumen
    showConfirmationModal(data);
});

function showConfirmationModal(data) {
    pendingPurchaseData = data;
    
    // Calcular total
    const prices = { REGULAR: 5000, VIP: 10000 };
    let total = 0;
    
    // Generar HTML del resumen
    let summaryHTML = `
        <div class="summary-section">
            <p><strong>📅 Fecha de visita:</strong> ${formatDate(data.fecha)}</p>
            <p><strong>💳 Forma de pago:</strong> ${data.medioPago}</p>
        </div>
        <div class="summary-section">
            <h3>🎫 Entradas (${data.entradas.length})</h3>
            <ul class="ticket-list">
    `;
    
    data.entradas.forEach((entrada, index) => {
        const price = prices[entrada.tipoEntrada];
        total += price;
        summaryHTML += `
            <li>
                <span class="ticket-info">
                    Visitante ${index + 1}: ${entrada.edad} años - 
                    <strong>${entrada.tipoEntrada}</strong>
                </span>
                <span class="ticket-price">${formatCurrency(price)}</span>
            </li>
        `;
    });
    
    summaryHTML += `
            </ul>
        </div>
        <div class="summary-total">
            <strong>Total a pagar:</strong> 
            <span class="total-amount">${formatCurrency(total)}</span>
        </div>
    `;
    
    // Agregar advertencia para pago en efectivo
    if (data.medioPago === 'EFECTIVO') {
        summaryHTML += `
            <div class="payment-warning">
                <p>⚠️ <strong>Recordatorio:</strong> Deberás pagar este monto en la boletería del parque el día de tu visita.</p>
            </div>
        `;
    }
    
    purchaseSummary.innerHTML = summaryHTML;
    modal.style.display = 'flex';
}

function formatDate(dateString) {
    const date = new Date(dateString + 'T00:00:00');
    return date.toLocaleDateString('es-AR', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('es-AR', { 
        style: 'currency', 
        currency: 'ARS' 
    }).format(amount);
}

// Confirmar compra
confirmBtn.addEventListener('click', function() {
    if (!pendingPurchaseData) return;
    
    modal.style.display = 'none';
    
    fetch('http://127.0.0.1:5000/comprar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pendingPurchaseData),
    })
    .then(response => response.json())
    .then(apiResponse => {
        if (apiResponse.status === 'redireccion') {
            // Pago con TARJETA - Redirigir a Mercado Pago
            showMessage('Redirigiendo a Mercado Pago...', 'success');
            
            // Guardar datos para el checkout
            sessionStorage.setItem('checkout_data', JSON.stringify({
                total: apiResponse.total,
                cantidad: apiResponse.cantidad,
                compra_id: apiResponse.id_compra
            }));
            
            // Redirigir al checkout de MP después de 1 segundo
            setTimeout(() => {
                window.location.href = apiResponse.checkout_url;
            }, 1000);
            
        } else if (apiResponse.status === 'exito') {
            // Pago con EFECTIVO - Compra completada directamente
            const totalFormatted = new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(apiResponse.total);
            let successMsg = `${apiResponse.mensaje} Total: ${totalFormatted}.`;
            
            // Si es efectivo, agregar recordatorio
            if (pendingPurchaseData.medioPago === 'EFECTIVO') {
                successMsg += ' Recordá pagar en la boletería del parque el día de tu visita.';
            }
            
            showMessage(successMsg, 'success');
            form.reset();
            generateVisitorInputs(defaultQuantity);
            updatePaymentInfo(); // Actualizar mensaje de pago
        } else {
            showMessage(apiResponse.mensaje, 'error');
        }
        pendingPurchaseData = null;
    })
    .catch(error => {
        showMessage('Error de conexión con el servidor. ¿Está corriendo `python app.py`?', 'error');
        console.error('Error:', error);
        pendingPurchaseData = null;
    });
});

// Cancelar compra
cancelBtn.addEventListener('click', function() {
    modal.style.display = 'none';
    pendingPurchaseData = null;
});

function showMessage(message, type) {
    alertContainer.textContent = message;
    alertContainer.className = type;
    alertContainer.style.display = 'block';

    setTimeout(() => {
        alertContainer.style.display = 'none';
    }, 5000);
}