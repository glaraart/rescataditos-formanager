# 🐾 Sistema de Gestión de Adopciones

Sistema automatizado para gestionar solicitudes de adopción de animales mediante Google Forms, Supabase, Gmail API y Cloud Run.

## 📋 Características

- ✅ Captura automática de formularios desde Google Forms
- ✅ Almacenamiento en Supabase PostgreSQL
- ✅ Envío automático de emails con Gmail API
- ✅ Botones de acción rápida en emails (Aceptar/Rechazar)
- ✅ Tracking de timestamps para cada estado
- ✅ Arquitectura serverless con Cloud Run

## 🏗️ Arquitectura

```
Google Forms → Apps Script → Cloud Run → Supabase
                                  ↓
                              Gmail API
```
1. Usuario llena el formulario en Google Forms
2. Apps Script detecta el envío y llama al webhook de Cloud Run
3. Cloud Run procesa y guarda en Supabase
4. Cloud Run envía email con botones de acción
5. Click en botones actualiza el estado en Supabase

## 📁 Estructura del Proyecto

```
adopciones/
├── cloud-run/
│   ├── main.py               # API FastAPI
│   ├── requirements.txt      # Dependencias Python
└── README.md                 # Este archivo
```

## 📄 Licencia

Este proyecto es de código abierto. Úsalo libremente para tu organización de rescate animal. 🐶🐱

**Hecho con ❤️ para ayudar a los rescataditos**
