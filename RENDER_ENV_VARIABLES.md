# 🔧 Variables de Entorno para Render

## 📋 Configuración en Render Dashboard

Cuando despliegues en Render, configura estas variables de entorno en el panel de configuración:

### Variables Requeridas:

| Key (Clave) | Value (Valor) |
|-------------|---------------|
| `SMTP_EMAIL` | `clinicaunion.cix.1@gmail.com` |
| `SMTP_PASSWORD` | `snkzldzsgsarwwqa` |
| `SMTP_SERVER` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `FRONTEND_URL` | `https://proyecto-ingenieria-y-calidad.onrender.com` |
| `SECRET_KEY` | `b043cf0a10195176cc01b2dcbb94850baed51b78a47591ac37b62c23dd92feea` |

### 📝 Instrucciones para Render:

1. Ve a tu servicio en Render Dashboard
2. Navega a **Environment** (Entorno)
3. Agrega cada variable de entorno usando el formato:
   - **Key**: `SMTP_EMAIL`
   - **Value**: `clinicaunion.cix.1@gmail.com`
4. Repite para todas las variables de la tabla
5. Guarda los cambios
6. Reinicia el servicio

### ⚠️ Importante:

- **NO** subas el archivo `.env` al repositorio (debe estar en `.gitignore`)
- Las variables de entorno en Render sobrescriben las del archivo `.env`
- `FRONTEND_URL` debe apuntar a tu URL de producción en Render
- `SECRET_KEY` debe ser única y secreta (no compartir públicamente)

### ✅ Verificación:

Después de configurar, verifica que:
- ✅ El servicio se inicia sin errores
- ✅ Los emails se envían correctamente
- ✅ La recuperación de contraseña funciona
- ✅ Los enlaces en los emails apuntan a la URL correcta

