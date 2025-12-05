"""
Sistema de Gestión de Adopciones - Cloud Run
FastAPI + PostgreSQL (Supabase) + Gmail SMTP
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from datetime import datetime
import os
import uuid
from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psycopg2
from psycopg2.extras import RealDictCursor
import json

app = FastAPI()

# Configuración de base de datos
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Configuración de email
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO")
CLOUD_RUN_URL = os.getenv("CLOUD_RUN_URL")


def get_db_connection():
    """Crear conexión a PostgreSQL"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )

# Estados
ESTADOS = {
    "PENDIENTE": "Pendiente",
    "ACEPTADO": "Aceptado",
    "RECHAZADO": "Rechazado"
}


def enviar_email_gmail(destinatario: str, asunto: str, html_body: str):
    """Envía un email usando Gmail SMTP con App Password"""
    try:
        # Crear mensaje MIME
        message = MIMEMultipart('alternative')
        message['From'] = GMAIL_USER
        message['To'] = destinatario
        message['Subject'] = asunto
        
        # Agregar contenido HTML
        html_part = MIMEText(html_body, 'html')
        message.attach(html_part)
        
        # Conectar a Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(message)
        
        print(f"✅ Email enviado a {destinatario}")
        return True
    except Exception as e:
        print(f"❌ Error al enviar email: {str(e)}")
        raise


def generar_id() -> str:
    """Genera un ID único para la solicitud"""
    return f"SOL-{str(uuid.uuid4())[:8].upper()}"


def extraer_campos_db(datos: Dict[str, Any]) -> Dict[str, Any]:
    """Extrae solo los campos que van a la base de datos"""
    
    # Helper para obtener el primer valor de la lista
    def get_value(key: str) -> str:
        return datos.get(key, [""])[0] if isinstance(datos.get(key), list) else datos.get(key, "")
    
    return {
        "nombre_apellido": get_value("Nombre y Apellido"),
        "edad": get_value("Edad"),
        "ocupacion": get_value("Ocupación"),
        "email": get_value("Email"),
        "instagram": get_value("Instagram"),
        "celular": get_value("Celular de contacto"),
        "zona": get_value("Zona normalizada"),
        "tipo_vivienda": get_value("¿Vivís en casa o departamento?"),
        "tenencia_vivienda": get_value("Tipo de tenencia de la vivienda"),
        "cerramientos_url": get_value("En este espacio cargue las fotos o un video de los cerramientos. No mas de 100MB"),
        "nombre_peludo": get_value("Nombre del peludo en el que estas interesado/a.En caso de que no tenga un nombre asignado por nosotras, describir su aspecto.")
    }


def generar_html_email(solicitud_id: str, datos: Dict[str, Any]) -> str:
    """Genera el HTML del email con todos los campos del formulario"""
    
    # Helper para obtener valores
    def get_value(key: str) -> str:
        val = datos.get(key, [""])[0] if isinstance(datos.get(key), list) else datos.get(key, "")
        return val if val else "No especificado"
    
    # URLs para los botones
    url_aceptar = f"{CLOUD_RUN_URL}/action?action=aceptar&id={solicitud_id}"
    url_rechazar = f"{CLOUD_RUN_URL}/action?action=rechazar&id={solicitud_id}"
    
    html = f"""
    <html>
      <head>
        <style>
          body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; }}
          .container {{ max-width: 800px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
          .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 30px; 
            text-align: center; 
          }}
          .badge {{ 
            display: inline-block;
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 8px 15px;
            border-radius: 5px;
            font-size: 14px;
            font-family: monospace;
            margin-top: 10px;
          }}
          .content {{ padding: 30px; }}
          .section {{ margin-bottom: 30px; }}
          .section-title {{ 
            font-size: 18px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
          }}
          .field {{ 
            margin: 12px 0; 
            padding: 12px; 
            background: #f9f9f9; 
            border-left: 3px solid #667eea;
            border-radius: 3px; 
          }}
          .field-label {{ font-weight: bold; color: #555; display: block; margin-bottom: 5px; }}
          .field-value {{ color: #333; }}
          .buttons {{ 
            text-align: center; 
            padding: 30px; 
            background: #f9f9f9; 
            border-top: 2px solid #eee;
          }}
          .button {{ 
            display: inline-block; 
            padding: 15px 35px; 
            margin: 10px 5px; 
            text-decoration: none; 
            border-radius: 8px; 
            font-weight: bold;
            color: white;
            font-size: 16px;
          }}
          .btn-visto {{ background-color: #fbbc04; }}
          .btn-aceptar {{ background-color: #34a853; }}
          .btn-rechazar {{ background-color: #ea4335; }}
          .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; background: #f5f5f5; }}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>🐾 Nueva Solicitud de Adopción</h1>
            <div class="badge">ID: {solicitud_id}</div>
          </div>
          
          <div class="content">
            <!-- Datos Personales -->
            <div class="section">
              <div class="section-title">👤 Datos Personales</div>
              <div class="field">
                <span class="field-label">Nombre y Apellido:</span>
                <span class="field-value">{get_value("Nombre y Apellido")}</span>
              </div>
              <div class="field">
                <span class="field-label">Edad:</span>
                <span class="field-value">{get_value("Edad")}</span>
              </div>
              <div class="field">
                <span class="field-label">Ocupación:</span>
                <span class="field-value">{get_value("Ocupación")}</span>
              </div>
              <div class="field">
                <span class="field-label">Email:</span>
                <span class="field-value">{get_value("Email")}</span>
              </div>
              <div class="field">
                <span class="field-label">Instagram:</span>
                <span class="field-value">{get_value("Instagram")}</span>
              </div>
              <div class="field">
                <span class="field-label">Celular:</span>
                <span class="field-value">{get_value("Celular de contacto")}</span>
              </div>
              <div class="field">
                <span class="field-label">Zona:</span>
                <span class="field-value">{get_value("Zona normalizada")}</span>
              </div>
            </div>

            <!-- Vivienda -->
            <div class="section">
              <div class="section-title">🏠 Información de Vivienda</div>
              <div class="field">
                <span class="field-label">Tipo de vivienda:</span>
                <span class="field-value">{get_value("¿Vivís en casa o departamento?")}</span>
              </div>
              <div class="field">
                <span class="field-label">Tenencia:</span>
                <span class="field-value">{get_value("Tipo de tenencia de la vivienda")}</span>
              </div>
              <div class="field">
                <span class="field-label">¿Consultaste con los dueños?:</span>
                <span class="field-value">{get_value("En caso de que sea alquilada, prestada o compartida: ¿consultaste previamente con los dueños?")}</span>
              </div>
              <div class="field">
                <span class="field-label">¿Tenes cerramientos?:</span>
                <span class="field-value">{get_value("¿Tenes cerramientos/protecciones en ventanas/balcón/patio/terraza?")}</span>
              </div>
              <div class="field">
                <span class="field-label">Cerramientos (fotos/video):</span>
                <span class="field-value">{get_value("En este espacio cargue las fotos o un video de los cerramientos. No mas de 100MB")}</span>
              </div>
              <div class="field">
                <span class="field-label">Si no tiene cerramientos:</span>
                <span class="field-value">{get_value("En caso de no tener, comentanos si estás dispuesto a ponerlos y cuándo, sino no podremos considerar su solicitud de adopción.")}</span>
              </div>
            </div>

            <!-- Experiencia con animales -->
            <div class="section">
              <div class="section-title">🐕 Experiencia con Animales</div>
              <div class="field">
                <span class="field-label">¿Tenes otros animales?:</span>
                <span class="field-value">{get_value("¿Tenes otros animales?")}</span>
              </div>
              <div class="field">
                <span class="field-label">Detalles de tus animales:</span>
                <span class="field-value">{get_value("Contanos un poco más acerca de si son gatos o perros, cuantos y que edades tienen!")}</span>
              </div>
              <div class="field">
                <span class="field-label">¿Están vacunados/castrados?:</span>
                <span class="field-value">{get_value("¿Están vacunados y/o castrados?")}</span>
              </div>
              <div class="field">
                <span class="field-label">Si no están vacunados/castrados:</span>
                <span class="field-value">{get_value("En caso de no estar vacunados y/o castrados, contanos los motivos que te llevaron a esa decisión.")}</span>
              </div>
              <div class="field">
                <span class="field-label">¿Tuviste animales previamente?:</span>
                <span class="field-value">{get_value("¿Tuviste animales previamente?")}</span>
              </div>
              <div class="field">
                <span class="field-label">Qué ocurrió con ellos:</span>
                <span class="field-value">{get_value("Contanos que ocurrió con ellos")}</span>
              </div>
              <div class="field">
                <span class="field-label">Alimentación actual:</span>
                <span class="field-value">{get_value("¿Qué alimentación le/s das? (Detalle marca si es alimento balanceado)")}</span>
              </div>
              <div class="field">
                <span class="field-label">Alimento que usabas:</span>
                <span class="field-value">{get_value("¿Qué alimento le/s dabas?")}</span>
              </div>
            </div>

            <!-- Situaciones especiales -->
            <div class="section">
              <div class="section-title">🌟 Otros Datos</div>
              <div class="field">
                <span class="field-label">¿Hay niños? Edades:</span>
                <span class="field-value">{get_value("¿Hay niños pequeños en el domicilio? Aclarar sus edades.")}</span>
              </div>
              <div class="field">
                <span class="field-label">Tiempo solo en el día:</span>
                <span class="field-value">{get_value("¿Cuánto tiempo estaría solo el peludo en su vida cotidiana?")}</span>
              </div>
              <div class="field">
                <span class="field-label">¿Qué harías en vacaciones?:</span>
                <span class="field-value">{get_value("¿Qué harías con el peludo en caso de vacaciones?")}</span>
              </div>
              <div class="field">
                <span class="field-label">¿Qué harías en caso de mudanza?:</span>
                <span class="field-value">{get_value("¿Qué harías con el peludo en caso de mudanza?")}</span>
              </div>
            </div>

            <!-- Peludo de interés -->
            <div class="section">
              <div class="section-title">❤️ Peludo de Interés</div>
              <div class="field">
                <span class="field-label">Nombre/Descripción:</span>
                <span class="field-value" style="font-size: 16px; font-weight: bold; color: #667eea;">
                  {get_value("Nombre del peludo en el que estas interesado/a.En caso de que no tenga un nombre asignado por nosotras, describir su aspecto.")}
                </span>
              </div>
            </div>
          </div>
          
          <div class="buttons">
            <h3>⚡ Acciones Rápidas</h3>
            <a href="{url_aceptar}" class="button btn-aceptar">✅ Aceptar Solicitud</a>
            <a href="{url_rechazar}" class="button btn-rechazar">❌ Rechazar Solicitud</a>
          </div>
          
          <div class="footer">
            <p>💾 Sistema automático de gestión de adopciones</p>
            <p>Supabase PostgreSQL + Cloud Run + Resend</p>
          </div>
        </div>
      </body>
    </html>
    """
    
    return html


@app.post("/webhook/form")
async def handle_form_submission(request: Request):
    """Recibe los datos del formulario desde Apps Script"""
    datos_formulario = await request.json()
    
    # El timestamp viene dentro de los datos del formulario
    timestamp = datos_formulario.get("Timestamp", datetime.now().isoformat())
    
    # Generar ID único
    solicitud_id = generar_id()
    
    # Extraer campos para la base de datos
    campos_db = extraer_campos_db(datos_formulario)
    
    # Guardar en PostgreSQL
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO solicitudes_adopcion (
            id, fecha_solicitud, estado, nombre_apellido, edad, ocupacion,
            email, instagram, celular, zona, tipo_vivienda, tenencia_vivienda,
            cerramientos_url, nombre_peludo, datos_completos,
            fecha_creacion, fecha_actualizacion, fecha_aceptado, fecha_rechazado
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """, (
        solicitud_id,
        timestamp,
        ESTADOS["PENDIENTE"],
        campos_db["nombre_apellido"],
        campos_db["edad"],
        campos_db["ocupacion"],
        campos_db["email"],
        campos_db["instagram"],
        campos_db["celular"],
        campos_db["zona"],
        campos_db["tipo_vivienda"],
        campos_db["tenencia_vivienda"],
        campos_db["cerramientos_url"],
        campos_db["nombre_peludo"],
        json.dumps(datos_formulario),
        datetime.now().isoformat(),
        datetime.now().isoformat(),
        None,
        None
    ))
    conn.commit()
    cur.close()
    conn.close()
    
    # Enviar email de notificación
    html_email = generar_html_email(solicitud_id, datos_formulario)
    
    enviar_email_gmail(
        destinatario=EMAIL_DESTINO,
        asunto=f"🐾 Nueva Solicitud - {campos_db['nombre_apellido']}",
        html_body=html_email
    )
    
    return {
        "success": True,
        "id": solicitud_id,
        "message": "Solicitud procesada correctamente"
    }


def generar_email_respuesta(nombre: str, accion: str, nombre_peludo: str) -> str:
    """Genera el email de respuesta para el solicitante"""
    
    if accion == "aceptar":
        return f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #34a853;">🎉 ¡Buenas noticias, {nombre}!</h2>
              <p>Nos complace informarte que tu solicitud de adopción para <strong>{nombre_peludo}</strong> ha sido <strong style="color: #34a853;">ACEPTADA</strong>.</p>
              <p>Nos pondremos en contacto contigo en breve para coordinar los próximos pasos.</p>
              <p>¡Gracias por darle una oportunidad a nuestros rescataditos! 🐾</p>
              <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
              <p style="color: #999; font-size: 12px;">Este es un mensaje automático del sistema de adopciones.</p>
            </div>
          </body>
        </html>
        """
    else:  # rechazar
        return f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #ea4335;">Sobre tu solicitud de adopción</h2>
              <p>Hola {nombre},</p>
              <p>Lamentablemente, en este momento no podemos continuar con tu solicitud de adopción para <strong>{nombre_peludo}</strong>.</p>
              <p>Esto puede deberse a diversos factores relacionados con las necesidades específicas del animal o las condiciones de adopción.</p>
              <p>Te invitamos a seguir revisando nuestros rescataditos disponibles. ¡Seguro hay uno perfecto para ti! 🐾</p>
              <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
              <p style="color: #999; font-size: 12px;">Este es un mensaje automático del sistema de adopciones.</p>
            </div>
          </body>
        </html>
        """


def generar_email_resumen_pendientes(solicitudes: list) -> str:
    """Genera email con resumen de solicitudes pendientes"""
    
    items_html = ""
    for sol in solicitudes:
        url_aceptar = f"{CLOUD_RUN_URL}/action?action=aceptar&id={sol['id']}"
        url_rechazar = f"{CLOUD_RUN_URL}/action?action=rechazar&id={sol['id']}"
        
        items_html += f"""
        <div class="solicitud-item">
            <div class="solicitud-header">
                <strong>{sol.get('nombre_apellido', 'Sin nombre')}</strong>
                <span class="badge-pendiente">Pendiente</span>
            </div>
            <div class="solicitud-info">
                <p><strong>Email:</strong> {sol.get('email', 'N/A')}</p>
                <p><strong>Peludo:</strong> {sol.get('nombre_peludo', 'N/A')}</p>
                <p><strong>Zona:</strong> {sol.get('zona', 'N/A')}</p>
                <p><strong>ID:</strong> <code>{sol['id']}</code></p>
            </div>
            <div class="solicitud-actions">
                <a href="{url_aceptar}" class="btn btn-aceptar">✅ Aceptar</a>
                <a href="{url_rechazar}" class="btn btn-rechazar">❌ Rechazar</a>
            </div>
        </div>
        """
    
    html = f"""
    <html>
      <head>
        <style>
          body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
          .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; }}
          h1 {{ color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 15px; }}
          .solicitud-item {{ 
            background: #f9f9f9; 
            border-left: 4px solid #fbbc04; 
            padding: 20px; 
            margin: 20px 0; 
            border-radius: 5px; 
          }}
          .solicitud-header {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 15px; 
          }}
          .badge-pendiente {{ 
            background: #fbbc04; 
            color: white; 
            padding: 5px 12px; 
            border-radius: 15px; 
            font-size: 12px; 
          }}
          .solicitud-info {{ margin: 15px 0; color: #555; }}
          .solicitud-info p {{ margin: 8px 0; }}
          .solicitud-actions {{ margin-top: 15px; text-align: center; }}
          .btn {{
            display: inline-block;
            padding: 12px 25px;
            margin: 5px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: bold;
            color: white;
          }}
          .btn-aceptar {{ background-color: #34a853; }}
          .btn-rechazar {{ background-color: #ea4335; }}
          code {{ background: #eee; padding: 2px 6px; border-radius: 3px; font-size: 12px; }}
        </style>
      </head>
      <body>
        <div class="container">
          <h1>⏳ Solicitudes Pendientes ({len(solicitudes)})</h1>
          <p>Tienes <strong>{len(solicitudes)}</strong> solicitud(es) sin responder:</p>
          {items_html}
        </div>
      </body>
    </html>
    """
    return html


@app.get("/action")
async def handle_button_action(action: str, id: str):
    """Maneja los clics en los botones del email - SOLO registra fecha"""
    
    estados_map = {
        "aceptar": ("Aceptado", "ACEPTADA", "#34a853", "✅", "fecha_aceptado"),
        "rechazar": ("Rechazado", "RECHAZADA", "#ea4335", "❌", "fecha_rechazado")
    }
    
    if action not in estados_map:
        return HTMLResponse("<h2>❌ Acción no válida</h2>")
    
    nuevo_estado, mensaje, color, emoji, campo_fecha = estados_map[action]
    
    # Actualizar en PostgreSQL
    now = datetime.now().isoformat()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        UPDATE solicitudes_adopcion 
        SET estado = %s, fecha_actualizacion = %s, {campo_fecha} = %s
        WHERE id = %s
    """, (nuevo_estado, now, now, id))
    conn.commit()
    cur.close()
    conn.close()
        
        # Página de confirmación
    html = f"""
        <html>
          <head>
            <style>
              body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              }}
              .container {{
                background: white;
                padding: 60px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
                max-width: 500px;
              }}
              .icon {{ font-size: 100px; margin-bottom: 20px; }}
              h1 {{ color: {color}; margin: 20px 0; font-size: 32px; }}
              .id {{
                background: #f5f5f5;
                padding: 20px;
                border-radius: 10px;
                font-family: 'Courier New', monospace;
                margin: 25px 0;
                font-size: 20px;
              }}
              .info {{ color: #999; font-size: 14px; margin-top: 20px; }}
            </style>
          </head>
          <body>
            <div class="container">
              <div class="icon">{emoji}</div>
              <h1>Solicitud {mensaje}</h1>
              <p style="font-size: 18px;">La solicitud ha sido actualizada exitosamente</p>
              <div class="id">ID: {id}</div>
              <p>Estado: <strong style="color: {color}; font-size: 20px;">{nuevo_estado}</strong></p>
              <p class="info">El email al solicitante se enviará automáticamente en el próximo proceso programado</p>
              <p style="margin-top: 40px; color: #999;">✨ Puedes cerrar esta ventana</p>
            </div>
          </body>
        </html>
        """
        
    return HTMLResponse(html)


@app.post("/cron/enviar-notificaciones")
async def enviar_notificaciones():
    """
    Endpoint ejecutado periódicamente (por Cloud Scheduler):
    1. Envía emails a solicitantes aceptados (>24h)
    2. Envía emails a solicitantes rechazados (>2h)
    3. Envía resumen de pendientes al equipo
    """
    from datetime import timedelta, timezone
    
    ahora = datetime.now(timezone.utc)
    hace_24h = ahora - timedelta(hours=24)
    hace_2h = ahora - timedelta(hours=2)
    
    enviados = {"aceptados": 0, "rechazados": 0, "pendientes": 0}
    
    conn = get_db_connection()
    cur = conn.cursor()
        
    # 1. Buscar ACEPTADOS con >24h sin email enviado
    cur.execute("""
        SELECT * FROM solicitudes_adopcion 
        WHERE estado = 'Aceptado' 
        AND (email_respuesta_enviado IS NULL OR email_respuesta_enviado = FALSE)
        AND fecha_aceptado <= %s
    """, (hace_24h,))
    aceptados = cur.fetchall()
    
    for solicitud in aceptados:
        html = generar_email_respuesta(
            solicitud.get('nombre_apellido', 'Solicitante'),
            'aceptar',
            solicitud.get('nombre_peludo', 'el peludo')
        )
        enviar_email_gmail(
            solicitud['email'],
            "✅ Solicitud Aceptada",
            html
        )
        cur.execute("""
            UPDATE solicitudes_adopcion 
            SET email_respuesta_enviado = TRUE 
            WHERE id = %s
        """, (solicitud['id'],))
        conn.commit()
        enviados["aceptados"] += 1
    
    # 2. Buscar RECHAZADOS con >2h sin email enviado
    cur.execute("""
        SELECT * FROM solicitudes_adopcion 
        WHERE estado = 'Rechazado' 
        AND (email_respuesta_enviado IS NULL OR email_respuesta_enviado = FALSE)
        AND fecha_rechazado <= %s
    """, (hace_2h,))
    rechazados = cur.fetchall()
    
    for solicitud in rechazados:
        html = generar_email_respuesta(
            solicitud.get('nombre_apellido', 'Solicitante'),
            'rechazar',
            solicitud.get('nombre_peludo', 'el peludo')
        )
        enviar_email_gmail(
            solicitud['email'],
            "Sobre tu solicitud de adopción",
            html
        )
        cur.execute("""
            UPDATE solicitudes_adopcion 
            SET email_respuesta_enviado = TRUE 
            WHERE id = %s
        """, (solicitud['id'],))
        conn.commit()
        enviados["rechazados"] += 1
    
    # 3. Buscar PENDIENTES
    cur.execute("""
        SELECT * FROM solicitudes_adopcion 
        WHERE estado = 'Pendiente' 
        AND fecha_aceptado IS NULL 
        AND fecha_rechazado IS NULL
    """)
    pendientes = cur.fetchall()
    
    if pendientes:
        html_resumen = generar_email_resumen_pendientes(pendientes)
        enviar_email_gmail(
            EMAIL_DESTINO,
            f"⏳ {len(pendientes)} Solicitud(es) Pendiente(s)",
            html_resumen
        )
        enviados["pendientes"] = len(pendientes)
    
    cur.close()
    conn.close()
    
    return {
        "success": True,
        "enviados": enviados,
        "timestamp": ahora.isoformat()
    }


@app.get("/")
async def root():
    """Health check"""
    return {"status": "ok", "service": "adopciones-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
