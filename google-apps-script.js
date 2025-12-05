/**
 * Apps Script para Google Forms - Enviar datos a Cloud Run
 */

// ⚠️ REEMPLAZA ESTA URL CON TU URL DE CLOUD RUN
const CLOUD_RUN_URL = "https://tu-servicio-xxxxxx.run.app";

function onFormSubmit(e) {
  try {
    // Obtener las respuestas del formulario
    const itemResponses = e.response.getItemResponses();
    
    // Crear objeto con los datos del formulario
    const datos = {};
    
    for (let i = 0; i < itemResponses.length; i++) {
      const itemResponse = itemResponses[i];
      const pregunta = itemResponse.getItem().getTitle();
      const respuesta = itemResponse.getResponse();
      
      datos[pregunta] = respuesta;
    }
    
    // Preparar el payload
    const payload = datos
    
    // Enviar al webhook de Cloud Run
    const options = {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    };
    
    const response = UrlFetchApp.fetch(CLOUD_RUN_URL + "/webhook/form", options);
    const responseCode = response.getResponseCode();
    const responseBody = response.getContentText();
    
    // Logging
    if (responseCode === 200) {
      Logger.log("✅ Solicitud enviada exitosamente");
      Logger.log("Respuesta: " + responseBody);
    } else {
      Logger.log("❌ Error al enviar. Status: " + responseCode);
      Logger.log("Respuesta: " + responseBody);
    }
    
  } catch (error) {
    Logger.log("❌ Error en onFormSubmit: " + error.toString());
  }
}