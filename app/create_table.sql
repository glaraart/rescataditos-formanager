-- Script de creación de tabla para Supabase
-- Ejecutar en: Dashboard > SQL Editor

CREATE TABLE IF NOT EXISTS solicitudes_adopcion (
    -- Identificadores
    id TEXT PRIMARY KEY,
    
    -- Timestamps del sistema
    fecha_solicitud TIMESTAMPTZ NOT NULL,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Estado y timestamps de acciones
    estado TEXT NOT NULL DEFAULT 'Pendiente',
    fecha_aceptado TIMESTAMPTZ,
    fecha_rechazado TIMESTAMPTZ,
    email_respuesta_enviado BOOLEAN DEFAULT FALSE,
    
    -- Datos del solicitante
    nombre_apellido TEXT,
    edad TEXT,
    ocupacion TEXT,
    email TEXT,
    instagram TEXT,
    celular TEXT,
    zona TEXT,
    
    -- Datos de vivienda
    tipo_vivienda TEXT,
    tenencia_vivienda TEXT,
    cerramientos_url TEXT,
    
    -- Mascota de interés
    nombre_peludo TEXT,
    
    -- JSON completo del formulario (backup de todos los campos)
    datos_completos JSONB
);

-- Índices para mejorar rendimiento de queries
CREATE INDEX IF NOT EXISTS idx_solicitudes_estado ON solicitudes_adopcion(estado);
CREATE INDEX IF NOT EXISTS idx_solicitudes_fecha_solicitud ON solicitudes_adopcion(fecha_solicitud DESC);
CREATE INDEX IF NOT EXISTS idx_solicitudes_email ON solicitudes_adopcion(email);
CREATE INDEX IF NOT EXISTS idx_solicitudes_nombre_peludo ON solicitudes_adopcion(nombre_peludo);

-- Comentarios para documentación
COMMENT ON TABLE solicitudes_adopcion IS 'Tabla principal de solicitudes de adopción';
COMMENT ON COLUMN solicitudes_adopcion.id IS 'ID único generado con formato SOL-XXXXXXXX';
COMMENT ON COLUMN solicitudes_adopcion.estado IS 'Estados posibles: Pendiente, Aceptado, Rechazado';
COMMENT ON COLUMN solicitudes_adopcion.datos_completos IS 'JSON con todos los campos del formulario original';
COMMENT ON COLUMN solicitudes_adopcion.fecha_aceptado IS 'Timestamp cuando se marcó como Aceptado';
COMMENT ON COLUMN solicitudes_adopcion.fecha_rechazado IS 'Timestamp cuando se marcó como Rechazado';
