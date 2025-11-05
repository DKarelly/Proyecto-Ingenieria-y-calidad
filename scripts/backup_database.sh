#!/bin/bash
#
# Script de respaldo automático de base de datos MySQL
# Se ejecuta antes del backup de Bacula para crear dump de la BD
#

# Configuración
DB_HOST="trolley.proxy.rlwy.net"
DB_PORT="40902"
DB_USER="root"
DB_PASSWORD="EOFxUnNipaqUHGATGeTGjiOzlcdEvKwL"
DB_NAME="CLINICA"

# Directorio de respaldos
BACKUP_DIR="/var/backups/mysql"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/clinica_backup_$TIMESTAMP.sql"

# Retención: eliminar backups con más de 7 días
RETENTION_DAYS=7

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Función de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $BACKUP_DIR/backup.log
}

# Función para enviar notificación por email (opcional)
send_notification() {
    SUBJECT="$1"
    MESSAGE="$2"
    
    # Descomentar y configurar si tienes servidor de correo
    # echo "$MESSAGE" | mail -s "$SUBJECT" admin@clinica.com
    
    log "$SUBJECT: $MESSAGE"
}

# ============================================
# INICIO DEL PROCESO DE RESPALDO
# ============================================

log "=========================================="
log "Iniciando respaldo de base de datos"
log "=========================================="

# Verificar que mysqldump está disponible
if ! command -v mysqldump &> /dev/null; then
    log "ERROR: mysqldump no está instalado"
    send_notification "ERROR: Backup BD" "mysqldump no está disponible en el sistema"
    exit 1
fi

# Realizar dump de la base de datos
log "Creando dump de la base de datos $DB_NAME..."

mysqldump \
    -h $DB_HOST \
    -P $DB_PORT \
    -u $DB_USER \
    -p$DB_PASSWORD \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    --hex-blob \
    --opt \
    $DB_NAME > $BACKUP_FILE 2>&1

# Verificar si el backup fue exitoso
if [ $? -eq 0 ]; then
    # Comprimir el archivo
    log "Comprimiendo backup..."
    gzip $BACKUP_FILE
    BACKUP_FILE="${BACKUP_FILE}.gz"
    
    # Calcular tamaño del backup
    BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
    
    log "✓ Backup completado exitosamente"
    log "  Archivo: $BACKUP_FILE"
    log "  Tamaño: $BACKUP_SIZE"
    
    # Verificar integridad del archivo comprimido
    if gzip -t $BACKUP_FILE 2>/dev/null; then
        log "✓ Verificación de integridad exitosa"
    else
        log "⚠ ADVERTENCIA: El archivo comprimido podría estar corrupto"
        send_notification "ADVERTENCIA: Backup BD" "La verificación de integridad falló"
    fi
    
    # Limpiar backups antiguos
    log "Eliminando backups con más de $RETENTION_DAYS días..."
    find $BACKUP_DIR -name "clinica_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
    
    OLD_COUNT=$(find $BACKUP_DIR -name "clinica_backup_*.sql.gz" -type f | wc -l)
    log "Backups actuales en el sistema: $OLD_COUNT"
    
    send_notification "Backup BD Exitoso" "Backup completado correctamente. Tamaño: $BACKUP_SIZE"
    
else
    log "✗ ERROR: El backup falló"
    send_notification "ERROR: Backup BD" "El proceso de backup ha fallado. Revisar logs."
    exit 1
fi

log "=========================================="
log "Proceso de respaldo finalizado"
log "=========================================="

exit 0
