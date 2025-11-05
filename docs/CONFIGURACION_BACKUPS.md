# Sistema de Respaldos y Recuperación - Clínica

## Descripción General

Este sistema implementa respaldos automáticos diarios utilizando **Bacula**, cumpliendo con los requisitos no funcionales de:
- Copias de seguridad automáticas diarias
- Retención de 7 días de historial
- Respaldo de BD, configuración, uploads y logs
- Verificación automática de integridad

## 📋 Requisitos Previos

### Software Necesario
- **Bacula** 9.x o superior
- **MySQL/MariaDB** para catálogo de Bacula
- **mysqldump** para respaldos de BD
- **Bash** 4.0 o superior
- **cron** para programación de tareas



## 🔧 Configuración Inicial

### 1. Configurar Base de Datos de Bacula

```bash
# Crear base de datos para Bacula
sudo mysql -u root -p

CREATE DATABASE bacula;
GRANT ALL PRIVILEGES ON bacula.* TO 'bacula'@'localhost' IDENTIFIED BY 'TU_PASSWORD_AQUI';
FLUSH PRIVILEGES;
EXIT;

# Importar esquema de Bacula
sudo mysql -u root -p bacula < /opt/bacula/scripts/make_mysql_tables
```

### 2. Configurar Archivos de Bacula

#### Copiar archivo de configuración principal

```bash
# Copiar configuración del proyecto
sudo cp config/bacula-dir.conf /opt/bacula/etc/bacula-dir.conf

# Ajustar permisos
sudo chown bacula:bacula /opt/bacula/etc/bacula-dir.conf
sudo chmod 640 /opt/bacula/etc/bacula-dir.conf
```

#### Editar configuración según tu instalación

```bash
sudo nano /opt/bacula/etc/bacula-dir.conf
```

**IMPORTANTE**: Cambiar los siguientes valores:

1. **Passwords**: Reemplazar todos los `TU_PASSWORD_*` por contraseñas seguras
2. **Rutas**: Ajustar las rutas de archivos según tu instalación:
   - `/ruta/del/proyecto` → Ruta real del proyecto
   - Rutas de configuración (nginx, supervisor, etc.)

3. **Email**: Cambiar `admin@clinica.com` por tu email real

### 3. Crear Directorios Necesarios

```bash
# Directorio para backups de MySQL
sudo mkdir -p /var/backups/mysql
sudo chown bacula:bacula /var/backups/mysql

# Directorio para bootstrap files
sudo mkdir -p /var/lib/bacula/bootstrap
sudo chown bacula:bacula /var/lib/bacula/bootstrap

# Directorio para storage de Bacula
sudo mkdir -p /var/lib/bacula/storage
sudo chown bacula:bacula /var/lib/bacula/storage

# Directorio para logs
sudo mkdir -p /var/log/bacula
sudo chown bacula:bacula /var/log/bacula
```

### 4. Configurar Scripts de Backup

```bash
# Copiar scripts
sudo cp scripts/backup_database.sh /opt/bacula/scripts/
sudo cp scripts/restore_database.sh /opt/bacula/scripts/

# Dar permisos de ejecución
sudo chmod +x /opt/bacula/scripts/backup_database.sh
sudo chmod +x /opt/bacula/scripts/restore_database.sh

# Configurar permisos
sudo chown bacula:bacula /opt/bacula/scripts/*.sh
```

### 5. Programar Ejecución Automática

#### Opción A: Usando Cron (Recomendado)

```bash
# Editar crontab de bacula
sudo crontab -u bacula -e

# Agregar línea para ejecutar backup diario a las 1:30 AM
30 1 * * * /opt/bacula/scripts/backup_database.sh

# Guardar y salir
```

#### Opción B: Script de Bacula ClientRunBeforeJob

Editar `/opt/bacula/etc/bacula-dir.conf` y agregar en cada Job:

```
Job {
  Name = "BackupBaseDatos"
  ...
  ClientRunBeforeJob = "/opt/bacula/scripts/backup_database.sh"
}
```

### 6. Configurar Bacula Storage Daemon

Editar `/opt/bacula/etc/bacula-sd.conf`:

```
Storage {
  Name = clinica-sd
  SDPort = 9103
  WorkingDirectory = "/var/lib/bacula"
  Pid Directory = "/var/run/bacula"
  Maximum Concurrent Jobs = 20
}

Device {
  Name = FileStorage
  Media Type = File
  Archive Device = /var/lib/bacula/storage
  LabelMedia = yes
  Random Access = Yes
  AutomaticMount = yes
  RemovableMedia = no
  AlwaysOpen = no
}
```

### 7. Configurar Bacula File Daemon

Editar `/opt/bacula/etc/bacula-fd.conf`:

```
Director {
  Name = clinica-dir
  Password = "TU_PASSWORD_DIRECTOR_AQUI"  # Mismo que en bacula-dir.conf
}

FileDaemon {
  Name = clinica-fd
  FDport = 9102
  WorkingDirectory = /var/lib/bacula
  Pid Directory = /var/run/bacula
  Maximum Concurrent Jobs = 20
}

Messages {
  Name = Standard
  director = clinica-dir = all, !skipped, !restored
}
```

## 🚀 Iniciar Servicios

```bash
# Iniciar servicios de Bacula
sudo systemctl start bacula-dir
sudo systemctl start bacula-sd
sudo systemctl start bacula-fd

# Habilitar inicio automático
sudo systemctl enable bacula-dir
sudo systemctl enable bacula-sd
sudo systemctl enable bacula-fd

# Verificar estado
sudo systemctl status bacula-dir
sudo systemctl status bacula-sd
sudo systemctl status bacula-fd
```

## ✅ Verificar Configuración

```bash
# Probar configuración de Director
sudo bacula-dir -t -c /opt/bacula/etc/bacula-dir.conf

# Probar configuración de Storage
sudo bacula-sd -t -c /opt/bacula/etc/bacula-sd.conf

# Probar configuración de File Daemon
sudo bacula-fd -t -c /opt/bacula/etc/bacula-fd.conf
```

Si no hay errores, la configuración es correcta.

## 📊 Monitoreo y Administración

### Usar Consola de Bacula

```bash
# Abrir consola de Bacula
sudo bconsole

# Comandos útiles en la consola:
status dir          # Estado del Director
status client       # Estado del Cliente
status storage      # Estado del Storage
list jobs           # Listar trabajos ejecutados
list volumes        # Listar volúmenes de backup
messages            # Ver mensajes del sistema
```

### Ejecutar Backup Manual

```bash
sudo bconsole

# En la consola:
run job=BackupBaseDatos
yes

# Verificar progreso
status dir
```

### Ver Logs

```bash
# Log principal de Bacula
sudo tail -f /var/log/bacula/bacula.log

# Log de backup de BD
sudo tail -f /var/backups/mysql/backup.log
```

## 🔄 Procedimiento de Restauración

### Restauración Completa de Base de Datos

```bash
# 1. Listar backups disponibles
ls -lh /var/backups/mysql/

# 2. Ejecutar restauración
sudo /opt/bacula/scripts/restore_database.sh /var/backups/mysql/clinica_backup_YYYYMMDD_HHMMSS.sql.gz

# 3. Confirmar cuando se solicite escribiendo: SI

# 4. Esperar a que termine el proceso
```

### Restauración desde Bacula

```bash
sudo bconsole

# En la consola:
restore all
# Seleccionar el backup a restaurar
# Confirmar la restauración
```

## 🔔 Configurar Notificaciones por Email

### 1. Configurar servidor de correo

```bash
# Instalar postfix
sudo apt-get install postfix mailutils

# Configurar postfix para envío
sudo dpkg-reconfigure postfix
```

### 2. Probar envío de email

```bash
echo "Prueba de notificación de backup" | mail -s "Test Bacula" admin@clinica.com
```

### 3. Las notificaciones se enviarán automáticamente en estos casos:
- Backup completado exitosamente
- Error en el backup
- Problemas de almacenamiento
- Anomalías detectadas

## 📈 Mantenimiento

### Verificación Semanal

```bash
# Verificar espacio en disco
df -h /var/lib/bacula/storage
df -h /var/backups/mysql

# Verificar integridad de backups
sudo /opt/bacula/scripts/verify_backups.sh
```

### Limpieza de Backups Antiguos

Los backups se eliminan automáticamente después de 7 días según la configuración de retención.

Para limpieza manual:

```bash
# Eliminar backups de BD con más de 7 días
find /var/backups/mysql -name "clinica_backup_*.sql.gz" -type f -mtime +7 -delete

# En Bacula, la limpieza es automática según Pool configuration
```

## 🛟 Recuperación de Desastres

### Escenario 1: Pérdida Total de Base de Datos

```bash
# 1. Identificar el backup más reciente
ls -lt /var/backups/mysql/ | head -n 5

# 2. Restaurar
sudo /opt/bacula/scripts/restore_database.sh /var/backups/mysql/[archivo_mas_reciente]
```

### Escenario 2: Pérdida de Archivos del Sistema

```bash
# 1. Usar Bacula para restaurar
sudo bconsole

# 2. En la consola:
restore all
# Seleccionar job: BackupUploads o BackupConfiguracion
# Confirmar restauración
```

### Escenario 3: Restaurar a un Punto Específico en el Tiempo

```bash
# Bacula mantiene 7 días de backups
# Cada backup está etiquetado con fecha/hora
# Seleccionar el backup correspondiente al momento deseado
```

## 📞 Soporte y Contacto

Para problemas con el sistema de backups:
1. Revisar logs: `/var/log/bacula/bacula.log`
2. Verificar estado de servicios: `systemctl status bacula-*`
3. Revisar espacio en disco
4. Contactar al administrador del sistema

## 🔐 Seguridad

### Recomendaciones:
1. ✅ Cambiar TODOS los passwords por defecto
2. ✅ Restringir permisos de archivos de configuración (640)
3. ✅ Almacenar backups en ubicación segura
4. ✅ Considerar cifrado de backups (ver documentación de Bacula)
5. ✅ Mantener copias offsite (en otra ubicación física)
6. ✅ Probar restauraciones regularmente

## 📚 Referencias

- [Documentación oficial de Bacula](https://www.bacula.org/documentation/)
- [Guía de administración de Bacula](https://www.bacula.org/documentation/Bacula-Admin-Guide.pdf)
- [Community Bacula](https://www.bacula.org/community/)

---

**Última actualización**: 4 de noviembre de 2025
**Versión**: 1.0
**Autor**: Sistema Clínica - Equipo de Desarrollo
