document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("compraForm");
  const metodo = document.getElementById("metodo_pago");
  const tarjetaFields = document.getElementById("tarjetaFields");
  const cantidadInput = document.getElementById("cantidad");
  const ageFieldsContainer = document.getElementById("ageFieldsContainer");
  const modal = document.getElementById("confirmModal");
  const confirmBtn = document.getElementById("confirmCompra");
  const cancelBtn = document.getElementById("cancelCompra");
  const fechaInput = document.getElementById("fecha");
  /**
   * Valida que la fecha seleccionada sea hoy o mañana, y que no sea domingo.
   * @param {string} dateString - La fecha en formato "YYYY-MM-DD".
   * @returns {{valid: boolean, error?: string}}
   */

  function isValidParkDate(dateString) {
    if (!dateString) {
      return { valid: false, error: "Debe seleccionar una fecha" };
    } // Parsear la fecha manualmente para evitar problemas de zona horaria

    const parts = dateString.split("-");
    const year = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10) - 1;
    const day = parseInt(parts[2], 10);
    const selectedDate = new Date(year, month, day);

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (selectedDate < today) {
      return { valid: false, error: "La fecha no puede ser anterior a hoy" };
    }

    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);

    if (selectedDate > tomorrow) {
      return {
        valid: false,
        error: "Solo se pueden comprar entradas para hoy o mañana.",
      };
    }

    if (selectedDate.getDay() === 0) {
      return { valid: false, error: "El parque está cerrado los domingos" };
    }

    return { valid: true };
  } // --- CONFIGURACIÓN INICIAL DE FECHA --- // Establecer fecha mínima (hoy)

  const today_iso = new Date().toISOString().split("T")[0];
  fechaInput.min = today_iso; // Se elimina la propiedad `max` para no bloquear el calendario // --- CORRECCIÓN: VALIDACIÓN EN TIEMPO REAL PARA EL CAMPO DE FECHA ---
  fechaInput.addEventListener("change", () => {
    const dateValidation = isValidParkDate(fechaInput.value);
    if (!dateValidation.valid) {
      fechaInput.classList.add("field-error"); // Actualizamos el mensaje de error para que se muestre debajo del campo
      fechaInput.setAttribute("data-error", dateValidation.error);
    } else {
      fechaInput.classList.remove("field-error"); // Opcional: restaurar el mensaje por defecto
      fechaInput.setAttribute(
        "data-error",
        "Seleccione una fecha válida (lunes a sábados)"
      );
    }
  }); // ---------------------------------------------------------------- // Handle payment method change
  metodo.addEventListener("change", () => {
    tarjetaFields.classList.toggle("hidden", metodo.value !== "tarjeta");
  }); // Handle quantity change

  cantidadInput.addEventListener("change", () => {
    const cantidad = Math.min(
      Math.max(parseInt(cantidadInput.value) || 0, 1),
      10
    );
    cantidadInput.value = cantidad;
    updateAgeFields(cantidad);
  });

  function updateAgeFields(cantidad) {
    ageFieldsContainer.innerHTML = "";
    for (let i = 0; i < cantidad; i++) {
      const label = document.createElement("label");
      label.innerHTML = `
                Edad visitante ${i + 1}
                <input type="number" class="age-input" min="0" max="99" required
                       placeholder="Edad" data-error="Edad requerida (0-99)" />
            `;
      ageFieldsContainer.appendChild(label);
    }
  }

  function validateForm() {
    const errors = [];
    clearValidationErrors();

    const dateValidation = isValidParkDate(fechaInput.value);
    if (!dateValidation.valid) {
      addError(dateValidation.error, fechaInput);
    }

    const cantidad = parseInt(cantidadInput.value);
    if (!cantidad || cantidad < 1 || cantidad > 10) {
      addError("La cantidad debe estar entre 1 y 10 entradas", cantidadInput);
    }

    const edades = [...document.querySelectorAll(".age-input")].map((input) =>
      parseInt(input.value)
    );
    if (edades.length !== cantidad) {
      addError(
        "Debe especificar la edad para cada visitante",
        ageFieldsContainer
      );
    } else if (edades.some((edad) => isNaN(edad) || edad < 0 || edad > 99)) {
      addError("Las edades deben ser válidas (0-99)", ageFieldsContainer);
    }

    if (metodo.value === "tarjeta") {
      const numTarjeta = document.getElementById("numTarjeta");
      const vencimiento = document.getElementById("vencimiento");
      const cvv = document.getElementById("cvv");

      if (!numTarjeta.value.match(/^\d{4}-\d{4}-\d{4}-\d{4}$/)) {
        addError(
          "Número de tarjeta inválido (XXXX-XXXX-XXXX-XXXX)",
          numTarjeta
        );
      }
      if (!vencimiento.value.match(/^(0[1-9]|1[0-2])\/\d{2}$/)) {
        addError("Vencimiento inválido (MM/AA)", vencimiento);
      }
      if (!cvv.value.match(/^\d{3}$/)) {
        addError("CVV inválido (3 dígitos)", cvv);
      }
    }

    return errors;

    function addError(message, element) {
      errors.push(message);
      if (element) {
        element.classList.add("field-error"); // Actualiza el data-error para el resumen de errores
        if (element.hasAttribute("data-error")) {
          element.setAttribute("data-error", message);
        }
      }
    }
  }

  function clearValidationErrors() {
    document
      .querySelectorAll(".field-error")
      .forEach((el) => el.classList.remove("field-error"));
    document.getElementById("validationErrors").classList.add("hidden");
  }

  function showValidationErrors(errors) {
    const errorsDiv = document.getElementById("validationErrors");
    errorsDiv.innerHTML = errors.map((err) => `<div>${err}</div>`).join("");
    errorsDiv.classList.remove("hidden");
    setTimeout(() => {
      errorsDiv.classList.add("hidden");
    }, 5000);
  }

  function getFormData() {
    return {
      fecha: fechaInput.value,
      cantidad: parseInt(cantidadInput.value),
      edades: [...document.querySelectorAll(".age-input")].map((input) =>
        parseInt(input.value)
      ),
      tipo_pase: document.getElementById("tipo_pase").value,
      metodo_pago: metodo.value,
      email: document.getElementById("email").value,
      datos_tarjeta:
        metodo.value === "tarjeta"
          ? {
              numero: document.getElementById("numTarjeta").value,
              vencimiento: document.getElementById("vencimiento").value,
              cvv: document.getElementById("cvv").value,
            }
          : null,
    };
  }

  function showConfirmationModal(data) {
    const precio = data.tipo_pase === "vip" ? 2000 : 1000;
    const total = precio * data.cantidad;
    document.getElementById("resumenCompra").innerHTML = `
            <p><strong>Fecha:</strong> ${data.fecha}</p>
            <p><strong>Cantidad:</strong> ${data.cantidad} entradas</p>
            <p><strong>Tipo:</strong> ${data.tipo_pase.toUpperCase()}</p>
            <p><strong>Total:</strong> $${total}</p>
            <p><strong>Método:</strong> ${data.metodo_pago}</p>
            ${data.email ? `<p><strong>Email:</strong> ${data.email}</p>` : ""}
        `;
    modal.classList.remove("hidden");
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const errors = validateForm();
    if (errors.length > 0) {
      showValidationErrors(errors);
      return;
    }
    showConfirmationModal(getFormData());
  });

  confirmBtn.addEventListener("click", async () => {
    try {
      const response = await fetch("/api/compra", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(getFormData()),
      });
      const data = await response.json();
      modal.classList.add("hidden");
      if (response.ok && data.ok) {
        alert("¡Compra realizada con éxito!");
        form.reset();
        updateAgeFields(1);
      } else {
        throw new Error(data.error || "Error en la compra");
      }
    } catch (err) {
      alert(err.message || "Error de conexión");
    }
  });

  cancelBtn.addEventListener("click", () => {
    modal.classList.add("hidden");
  });

  updateAgeFields(1);
});
