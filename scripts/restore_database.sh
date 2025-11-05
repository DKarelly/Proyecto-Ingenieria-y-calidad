#!/bin/bash
#
# Script de restauración de base de datos desde backup
# Uso: ./restore_database.sh [archivo_backup.sql.gz]
#

# Configuración
DB_HOST="trolley.proxy.rlwy.net"
DB_PORT="40902"
DB_USER="root"
DB_PASSWORD="EOFxUnNipaqUHGATGeTGjiOzlcdEvKwL"
DB_NAME="CLINICA"

BACKUP_DIR="/var/backups/mysql"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función de logging con colores
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[ADVERTENCIA]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ============================================
# VALIDACIONES INICIALES
# ============================================

# Verificar si se proporcionó archivo de backup
if [ -z "$1" ]; then
    log_error "Debe especificar el archivo de backup a restaurar"
    echo ""
    echo "Uso: $0 [archivo_backup.sql.gz]"
    echo ""
    echo "Backups disponibles:"
    ls -lh $BACKUP_DIR/clinica_backup_*.sql.gz 2>/dev/null || echo "  No hay backups disponibles"
    exit 1
fi

BACKUP_FILE="$1"

# Verificar que el archivo existe
if [ ! -f "$BACKUP_FILE" ]; then
    log_error "El archivo $BACKUP_FILE no existe"
    exit 1
fi

log_info "=========================================="
log_info "RESTAURACIÓN DE BASE DE DATOS"
log_info "=========================================="
log_info "Archivo: $BACKUP_FILE"
log_info "Base de datos: $DB_NAME"
log_info "Servidor: $DB_HOST:$DB_PORT"
log_info "=========================================="

# ============================================
# CONFIRMACIÓN DEL USUARIO
# ============================================

log_warning "⚠️  ADVERTENCIA ⚠️"
log_warning "Esta operación ELIMINARÁ todos los datos actuales de la base de datos"
log_warning "y los reemplazará con los datos del backup."
echo ""
read -p "¿Está seguro de continuar? (escriba 'SI' para confirmar): " confirmacion

if [ "$confirmacion" != "SI" ]; then
    log_info "Operación cancelada por el usuario"
    exit 0
fi

# ============================================
# RESPALDO DE SEGURIDAD
# ============================================

log_info "Creando respaldo de seguridad de la BD actual..."
SAFETY_BACKUP="$BACKUP_DIR/safety_backup_before_restore_$(date +%Y%m%d_%H%M%S).sql.gz"

mysqldump \
    -h $DB_HOST \
    -P $DB_PORT \
    -u $DB_USER \
    -p$DB_PASSWORD \
    --single-transaction \
    $DB_NAME | gzip > $SAFETY_BACKUP

if [ $? -eq 0 ]; then
    log_info "✓ Respaldo de seguridad creado: $SAFETY_BACKUP"
else
    log_error "Fallo al crear respaldo de seguridad"
    exit 1
fi

# ============================================
# RESTAURACIÓN
# ============================================

log_info "Descomprimiendo archivo de backup..."

# Determinar si el archivo está comprimido
if [[ $BACKUP_FILE == *.gz ]]; then
    TEMP_FILE="/tmp/restore_temp_$(date +%s).sql"
    gunzip -c $BACKUP_FILE > $TEMP_FILE
    
    if [ $? -ne 0 ]; then
        log_error "Error al descomprimir el archivo"
        exit 1
    fi
    
    RESTORE_FILE=$TEMP_FILE
else
    RESTORE_FILE=$BACKUP_FILE
fi

log_info "Restaurando base de datos..."
log_warning "Este proceso puede tardar varios minutos..."

mysql \
    -h $DB_HOST \
    -P $DB_PORT \
    -u $DB_USER \
    -p$DB_PASSWORD \
    $DB_NAME < $RESTORE_FILE

if [ $? -eq 0 ]; then
    log_info "=========================================="
    log_info "✓ RESTAURACIÓN COMPLETADA EXITOSAMENTE"
    log_info "=========================================="
    log_info "La base de datos ha sido restaurada correctamente"
    log_info "Respaldo de seguridad guardado en:"
    log_info "  $SAFETY_BACKUP"
    
    # Limpiar archivo temporal
    if [ "$RESTORE_FILE" == "/tmp/restore_temp_"* ]; then
        rm -f $RESTORE_FILE
    fi
    
else
    log_error "=========================================="
    log_error "✗ ERROR EN LA RESTAURACIÓN"
    log_error "=========================================="
    log_error "La restauración ha fallado"
    log_warning "Para recuperar el estado anterior, ejecute:"
    log_warning "  $0 $SAFETY_BACKUP"
    
    # Limpiar archivo temporal
    if [ "$RESTORE_FILE" == "/tmp/restore_temp_"* ]; then
        rm -f $RESTORE_FILE
    fi
    
    exit 1
fi

# ============================================
# VERIFICACIÓN POST-RESTAURACIÓN
# ============================================

log_info "Verificando integridad de la base de datos..."

# Contar tablas
TABLE_COUNT=$(mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD -N -B -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '$DB_NAME';" 2>/dev/null)

if [ ! -z "$TABLE_COUNT" ] && [ "$TABLE_COUNT" -gt 0 ]; then
    log_info "✓ Base de datos verificada: $TABLE_COUNT tablas encontradas"
else
    log_warning "No se pudo verificar la integridad de la base de datos"
fi

log_info "=========================================="
log_info "Proceso completado"
log_info "=========================================="

exit 0
