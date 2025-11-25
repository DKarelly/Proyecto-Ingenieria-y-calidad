# ✅ Verificación Rápida de Gmail - Pasos Inmediatos

## 🔍 Paso 1: Verificar en Render Dashboard

1. Ve a: https://dashboard.render.com
2. Selecciona tu servicio: **proyecto-ingenieria-y-calidad**
3. Ve a la pestaña **"Environment"**
4. Verifica estas variables:

```
SMTP_EMAIL=clinicaunion.cix.1@gmail.com
SMTP_PASSWORD=[debe ser una contraseña de 16 caracteres]
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## 🔐 Paso 2: Verificar/Generar App Password en Gmail

### Si NO tienes App Password:

1. **Activa Verificación en Dos Pasos:**
   - https://myaccount.google.com/security
   - Activa "Verificación en dos pasos" si no está activada

2. **Genera App Password:**
   - https://myaccount.google.com/apppasswords
   - App: **Correo**
   - Dispositivo: **Otro (nombre personalizado)** → `Render - Clínica Unión`
   - **Copia la contraseña de 16 caracteres**

3. **Actualiza en Render:**
   - Ve a Environment en Render
   - Actualiza `SMTP_PASSWORD` con la nueva contraseña
   - Guarda los cambios

4. **Reinicia el servicio:**
   - El servicio se reiniciará automáticamente
   - O haz "Manual Deploy" → "Clear build cache & deploy"

### Si YA tienes App Password:

1. Verifica que esté correctamente copiada en Render (sin espacios extra)
2. Si sigue fallando, **regenera** una nueva App Password

## 🧪 Paso 3: Verificar en Logs

Después de reiniciar, busca en los logs de Render:

✅ **CORRECTO:**
```
📧✅ EmailService inicializado: clinicaunion.cix.1@gmail.com en smtp.gmail.com:587
```

❌ **ERROR DE AUTENTICACIÓN:**
```
📧❌ Error de autenticación SMTP
```
→ **Solución:** Regenera la App Password

❌ **ERROR DE CONEXIÓN:**
```
📧❌ Error conectando al servidor SMTP smtp.gmail.com:587. Detalle: [Errno 101] La red es inalcanzable
```
→ **Solución:** Puede ser restricción de red en Render. Considera usar SendGrid o Mailgun.

## 📋 Checklist Rápido

- [ ] Verificación en dos pasos activada en Gmail
- [ ] App Password generada (16 caracteres)
- [ ] `SMTP_EMAIL` configurado en Render
- [ ] `SMTP_PASSWORD` configurado en Render (App Password, NO contraseña normal)
- [ ] `SMTP_SERVER=smtp.gmail.com` en Render
- [ ] `SMTP_PORT=587` en Render
- [ ] Servicio reiniciado
- [ ] Logs muestran inicialización correcta

## 🔗 Enlaces Útiles

- **Generar App Password:** https://myaccount.google.com/apppasswords
- **Verificación en dos pasos:** https://myaccount.google.com/security
- **Actividades recientes:** https://myaccount.google.com/security-activity

---

**Si después de esto sigue fallando, el problema puede ser restricciones de red en Render. Considera usar SendGrid o Mailgun como alternativa.**

