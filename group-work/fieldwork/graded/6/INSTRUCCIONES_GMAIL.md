# 📧 Configuración de Gmail para envío de emails

## Paso 1: Habilitar verificación en 2 pasos

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. En el menú izquierdo, selecciona **"Seguridad"**
3. En la sección "Cómo inicias sesión en Google", busca **"Verificación en 2 pasos"**
4. Si no está activada, actívala siguiendo las instrucciones

## Paso 2: Generar App Password (Contraseña de aplicación)

1. Ve a: https://myaccount.google.com/apppasswords
   - O busca "App Passwords" en la configuración de seguridad
2. En "Seleccionar app", elige **"Correo"**
3. En "Seleccionar dispositivo", elige **"Otro (nombre personalizado)"**
4. Escribe: `Parque Tematico Python`
5. Haz clic en **"Generar"**
6. Google te mostrará una contraseña de 16 caracteres (ej: `abcd efgh ijkl mnop`)
7. **¡COPIA ESTA CONTRASEÑA!** No la podrás ver de nuevo

## Paso 3: Configurar en el proyecto

### Opción A: Archivo de configuración (recomendado)

Crea un archivo `.env` en la raíz del proyecto:

```bash
GMAIL_USER=alvarosueldoc@gmail.com
GMAIL_APP_PASSWORD=yikz cvhv nvcr zvyf
```

**⚠️ IMPORTANTE:** Agrega `.env` a tu `.gitignore` para no compartir tus credenciales

### Opción B: Variables de entorno de Windows

Ejecuta en PowerShell:

```powershell
$env:GMAIL_USER = "alvarosueldoc@gmail.com"
$env:GMAIL_APP_PASSWORD = "abcdefghijklmnop"
```

## Paso 4: Probar el envío

Ejecuta el script de prueba (desde la carpeta graded/6):

```bash
# Git Bash / WSL
python tools/manual-tests/enviar_email_real.py

# PowerShell / CMD
python .\tools\manual-tests\enviar_email_real.py
```

## Notas de seguridad

- **NUNCA** subas tu App Password al repositorio Git
- Si compartes el código, usa variables de entorno
- Puedes revocar el App Password en cualquier momento desde tu cuenta de Google
- La App Password solo funciona para aplicaciones, no para iniciar sesión en Google

## Solución de problemas

### Error: "Username and Password not accepted"
- Verifica que la verificación en 2 pasos esté activada
- Asegúrate de copiar la App Password completa (sin espacios)
- Intenta generar una nueva App Password

### Error: "SMTP Authentication Error"
- Revisa que el email sea correcto
- Verifica que no haya espacios extras en la contraseña

### Error: "Less secure app access"
- Usa App Password en lugar de habilitar "Acceso de apps menos seguras"
- La opción de apps menos seguras ya no está disponible en Gmail
