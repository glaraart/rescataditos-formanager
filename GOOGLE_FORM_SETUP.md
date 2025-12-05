# Configuración del Google Form con Apps Script

## Paso 1: Preparar el Google Form

Asegúrate de que tu Google Form tenga estos campos **EXACTAMENTE** con estos títulos:

- `Nombre y Apellido`
- `Edad`
- `Ocupación`
- `Email`
- `Instagram`
- `Celular de contacto`
- `Zona normalizada`
- `¿Vivís en casa o departamento?`
- `Tipo de tenencia de la vivienda`
- `En este espacio cargue las fotos o un video de los cerramientos. No mas de 100MB`
- `Nombre del peludo en el que estas interesado/a.En caso de que no tenga un nombre asignado por nosotras, describir su aspecto.`

## Paso 2: Agregar el Apps Script

1. Abre tu Google Form
2. Click en los 3 puntos verticales (⋮) en la esquina superior derecha
3. Selecciona **Editor de secuencia de comandos** (Apps Script)
4. Se abrirá una nueva pestaña con el editor
5. Borra todo el código que aparece por defecto
6. Copia y pega el código del archivo `google-apps-script.js`
7. **IMPORTANTE:** Reemplaza esta línea:
   ```javascript
   const CLOUD_RUN_URL = "https://tu-servicio-xxxxxx.run.app";
   ```
   Con tu URL real de Cloud Run (sin el `/` al final)

8. Guarda el proyecto (Ctrl+S o File → Save)
9. Dale un nombre al proyecto (ej: "Webhook Adopciones")

## Paso 3: Configurar el Activador (Trigger)

1. En el editor de Apps Script, click en el ícono del reloj ⏰ (Activadores) en el menú izquierdo
2. Click en **+ Agregar activador** (abajo a la derecha)
3. Configura así:
   - **Función que se ejecutará:** `onFormSubmit`
   - **Origen del evento:** `Desde el formulario`
   - **Tipo de evento:** `Al enviar el formulario`
4. Click en **Guardar**
5. Te pedirá autorización:
   - Selecciona tu cuenta de Google
   - Click en "Avanzado"
   - Click en "Ir a [nombre del proyecto] (no seguro)"
   - Click en "Permitir"

## Paso 4: Probar la Integración

### Opción A: Prueba Manual
1. En el editor de Apps Script, selecciona la función `testWebhook` del menú desplegable
2. Click en el botón ▶️ Ejecutar
3. Revisa los logs (View → Logs o Ctrl+Enter)
4. Deberías ver un mensaje de éxito

### Opción B: Prueba Real
1. Llena el formulario de Google Forms normalmente
2. Envía la respuesta
3. Verifica que:
   - Llegue un email a `EMAIL_DESTINO` con los datos de la solicitud
   - Se cree un registro en la base de datos de Supabase

## Paso 5: Monitoreo

Para ver si hay errores:
1. Ve al editor de Apps Script
2. Click en ⚙️ (Ejecuciones del proyecto)
3. Verás todas las ejecuciones con sus resultados

## Solución de Problemas

### Error 403 o 401
- Verifica que Cloud Run tenga `--allow-unauthenticated`
- Comando: `gcloud run services update rescataditos-formanager --region=us-central1 --allow-unauthenticated`

### Error 500
- Revisa los logs de Cloud Run: `gcloud run services logs read rescataditos-formanager --region=us-central1`
- Verifica que todas las variables de entorno estén configuradas

### No llega el email
- Verifica `GMAIL_USER` y `GMAIL_APP_PASSWORD` en Cloud Run
- Verifica `EMAIL_DESTINO` en Cloud Run

### Los datos no se guardan
- Verifica las variables de conexión a la base de datos (`DB_HOST`, `DB_USER`, `DB_PASSWORD`)
- Verifica que la tabla `solicitudes_adopcion` exista en Supabase
