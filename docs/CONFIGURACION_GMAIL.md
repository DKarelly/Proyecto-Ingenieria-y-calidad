# 📧 Guía de Configuración de Gmail para Envío de Emails

## 🔍 Verificación de Configuración Actual

### Paso 1: Verificar Variables de Entorno en Render

1. Ve a tu dashboard de Render: https://dashboard.render.com
2. Selecciona tu servicio web
3. Ve a la sección **"Environment"** o **"Variables de Entorno"**
4. Verifica que tengas configuradas estas variables:

```
SMTP_EMAIL=tu_email@gmail.com
SMTP_PASSWORD=tu_contraseña_de_aplicacion
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Paso 2: Verificar que NO estés usando tu contraseña normal

❌ **INCORRECTO:**
```
SMTP_PASSWORD=mi_contraseña_normal_de_gmail
```

✅ **CORRECTO:**
```
SMTP_PASSWORD=abcd efgh ijkl mnop  (16 caracteres, con espacios o sin espacios)
```

---

## 🔐 Configuración de Gmail App Password (Contraseña de Aplicación)

### Requisitos Previos

1. **Verificación en dos pasos activada** en tu cuenta de Gmail
2. Acceso a la cuenta de Gmail que usarás para enviar emails

### Pasos Detallados

#### 1. Activar Verificación en Dos Pasos

1. Ve a: https://myaccount.google.com/security
2. Busca la sección **"Verificación en dos pasos"**
3. Si no está activada, haz clic en **"Activar"** y sigue las instrucciones
4. **IMPORTANTE:** Sin esto, no podrás generar contraseñas de aplicación

#### 2. Generar Contraseña de Aplicación

**Opción A: Desde la página de seguridad de Google**

1. Ve a: https://myaccount.google.com/apppasswords
   - Si no ves esta opción, primero activa la verificación en dos pasos
2. En **"Seleccionar app"**, elige **"Correo"**
3. En **"Seleccionar dispositivo"**, elige **"Otro (nombre personalizado)"**
4. Escribe: `Clínica Unión - Render`
5. Haz clic en **"Generar"**
6. **Copia la contraseña de 16 caracteres** que aparece (ejemplo: `abcd efgh ijkl mnop`)

**Opción B: Desde la configuración de seguridad**

1. Ve a: https://myaccount.google.com/security
2. Busca **"Contraseñas de aplicaciones"** (puede estar en "Iniciar sesión en Google")
3. Si no la ves, activa primero la verificación en dos pasos
4. Sigue los pasos de la Opción A

#### 3. Configurar en Render

1. Ve a tu servicio en Render
2. Ve a **"Environment"** o **"Variables de Entorno"**
3. Actualiza o crea estas variables:

```
SMTP_EMAIL=clinicaunion.cix.1@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**NOTA:** La contraseña puede tener espacios o no. Ambas formas funcionan:
- `abcd efgh ijkl mnop` ✅
- `abcdefghijklmnop` ✅

#### 4. Reiniciar el Servicio

Después de actualizar las variables de entorno:
1. Ve a la sección **"Manual Deploy"** o **"Events"**
2. Haz clic en **"Clear build cache & deploy"** o simplemente espera el auto-deploy
3. El servicio se reiniciará con las nuevas credenciales

---

## 🧪 Verificación y Pruebas

### Verificar en los Logs de Render

Después de reiniciar, busca en los logs:

```
📧✅ EmailService inicializado: clinicaunion.cix.1@gmail.com en smtp.gmail.com:587
```

Si ves esto, la configuración está correcta.

### Probar Envío de Email

1. Crea una reserva desde la aplicación
2. Revisa los logs de Render para ver si hay errores
3. Busca mensajes como:
   - `📧✅ Email enviado exitosamente` ✅
   - `📧❌ Error conectando al servidor SMTP` ❌
   - `📧❌ Error de autenticación SMTP` ❌

---

## ❌ Errores Comunes y Soluciones

### Error: `[Errno 101] La red es inalcanzable`

**Causa:** Render no puede conectarse a Gmail SMTP

**Soluciones:**
1. Verifica que `SMTP_SERVER=smtp.gmail.com` esté correcto
2. Verifica que `SMTP_PORT=587` esté correcto
3. Verifica que no haya restricciones de firewall en Render
4. **Alternativa:** Considera usar un servicio de email profesional (SendGrid, Mailgun)

### Error: `Error de autenticación SMTP`

**Causa:** La contraseña es incorrecta o no es una App Password

**Soluciones:**
1. Verifica que estés usando una **Contraseña de Aplicación**, no tu contraseña normal
2. Regenera la contraseña de aplicación en Google
3. Asegúrate de copiar la contraseña completa (16 caracteres)
4. Verifica que no haya espacios extra al inicio o final

### Error: `Verificación en dos pasos no activada`

**Causa:** No puedes generar App Passwords sin verificación en dos pasos

**Solución:**
1. Activa la verificación en dos pasos en: https://myaccount.google.com/security
2. Luego genera la contraseña de aplicación

---

## 🔒 Seguridad

### ✅ Buenas Prácticas

1. **Nunca** compartas tu App Password públicamente
2. **Nunca** la subas a Git (debe estar en `.env` o variables de entorno de Render)
3. Si sospechas que está comprometida, **regenera** la contraseña inmediatamente
4. Usa una cuenta de Gmail dedicada para la aplicación (no tu cuenta personal)

### 🛡️ Verificación de Seguridad

1. Revisa periódicamente las **"Actividades recientes"** en tu cuenta de Google
2. Si ves accesos sospechosos, cambia la contraseña de aplicación
3. Considera usar una cuenta de Gmail Workspace (más segura para aplicaciones)

---

## 📝 Checklist de Configuración

- [ ] Verificación en dos pasos activada en Gmail
- [ ] Contraseña de aplicación generada (16 caracteres)
- [ ] Variables de entorno configuradas en Render:
  - [ ] `SMTP_EMAIL` configurado
  - [ ] `SMTP_PASSWORD` configurado (App Password)
  - [ ] `SMTP_SERVER=smtp.gmail.com`
  - [ ] `SMTP_PORT=587`
- [ ] Servicio reiniciado después de configurar variables
- [ ] Logs muestran: `EmailService inicializado`
- [ ] Prueba de envío de email exitosa

---

## 🔄 Alternativas si Gmail no Funciona

Si después de seguir todos los pasos Gmail sigue sin funcionar desde Render, considera:

1. **SendGrid** (Recomendado para producción)
   - Plan gratuito: 100 emails/día
   - Más confiable que Gmail SMTP
   - Mejor para aplicaciones en producción

2. **Mailgun**
   - Plan gratuito: 5,000 emails/mes
   - API fácil de usar
   - Buena documentación

3. **AWS SES**
   - Muy económico
   - Requiere configuración de AWS
   - Ideal para alto volumen

---

## 📞 Soporte

Si después de seguir esta guía sigues teniendo problemas:

1. Revisa los logs completos de Render
2. Verifica que la cuenta de Gmail no esté bloqueada
3. Prueba generar una nueva App Password
4. Considera usar un servicio de email alternativo

---

**Última actualización:** Noviembre 2025

