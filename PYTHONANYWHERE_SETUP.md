# 🐍 Guía de Despliegue en PythonAnywhere

## ✅ Compatibilidad

Tu aplicación **SÍ es 100% compatible** con PythonAnywhere. Funcionará sin problemas:
- ✅ Flask
- ✅ Tailwind CSS (CDN)
- ✅ Swiper JS (CDN)
- ✅ Google Fonts
- ✅ Archivos estáticos (CSS/JS propios)

**Nota**: Se eliminó el chatbot con Gemini AI para simplificar la aplicación y evitar problemas de seguridad.

---

## 📦 Paso 1: Preparar el Proyecto

### 1.1 Verificar estructura de archivos
```
Proyecto-Ingenieria-y-calidad/
├── app.py                 # ✅ Listo
├── requirements.txt       # ✅ Listo
├── templates/
│   └── home.html         # ✅ Listo
└── static/
    ├── css/
    │   └── home.css      # ✅ Listo
    └── js/
        └── home.js       # ✅ Listo
```

### 1.2 Verificar requirements.txt
Asegúrate de que incluya:
```
Flask==3.1.2
```

---

## 🚀 Paso 2: Subir a PythonAnywhere

### 2.1 Crear cuenta en PythonAnywhere
1. Ve a https://www.pythonanywhere.com/
2. Crea una cuenta gratuita (o de pago según necesites)

### 2.2 Subir archivos

**Opción A: Usando Git (Recomendado)**
```bash
# En tu terminal local
git add .
git commit -m "Preparar para despliegue en PythonAnywhere"
git push origin jose

# En PythonAnywhere > Consoles > Bash
git clone https://github.com/DKarelly/Proyecto-Ingenieria-y-calidad.git
cd Proyecto-Ingenieria-y-calidad
git checkout jose
```

**Opción B: Subir manualmente**
1. Ve a la pestaña "Files"
2. Sube cada archivo a su respectiva carpeta

### 2.3 Instalar dependencias
En PythonAnywhere > Consoles > Bash:
```bash
cd ~/Proyecto-Ingenieria-y-calidad
pip3 install --user -r requirements.txt
```

---

## ⚙️ Paso 3: Configurar Web App

### 3.1 Crear Web App
1. Ve a la pestaña "Web"
2. Click en "Add a new web app"
3. Selecciona "Manual configuration"
4. Elige Python 3.10 (o la versión más reciente)

### 3.2 Configurar WSGI
1. En la sección "Code", click en el archivo WSGI
2. Reemplaza todo el contenido con:

```python
import sys
import os

# Agregar el directorio del proyecto al path
project_home = '/home/TU_USUARIO/Proyecto-Ingenieria-y-calidad'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Importar la aplicación Flask
from app import app as application
```

**⚠️ IMPORTANTE**: Reemplaza `TU_USUARIO` con tu nombre de usuario de PythonAnywhere

### 3.3 Configurar directorio estático
En la pestaña "Web", en la sección "Static files":

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/TU_USUARIO/Proyecto-Ingenieria-y-calidad/static/` |

### 3.4 Recargar la aplicación
Click en el botón verde "Reload" en la parte superior

---

## 🌐 Paso 4: Probar la Aplicación

Tu aplicación estará disponible en:
```
http://TU_USUARIO.pythonanywhere.com
```

---

##  Monitoreo y Logs

### Ver logs de error
PythonAnywhere > Web > Log files:
- Error log: Ver errores de la aplicación
- Server log: Ver acceso a la aplicación
- Access log: Ver todas las peticiones

---

## 🔧 Solución de Problemas

### 1. Error 404 - Static files no cargan
- Verifica la configuración de archivos estáticos
- Asegúrate de que las rutas sean absolutas
- Recarga la aplicación

### 2. Error 500 - Internal Server Error
- Revisa el Error log
- Verifica que todas las dependencias estén instaladas
- Asegúrate de que `app.py` no tenga errores

### 3. Cambios no se reflejan
- Siempre haz "Reload" después de cambios
- Limpia la caché del navegador (Ctrl + F5)

---

## 📝 Checklist de Despliegue

- [ ] Estructura de archivos correcta
- [ ] `requirements.txt` actualizado
- [ ] Archivos subidos a PythonAnywhere
- [ ] Dependencias instaladas
- [ ] Web App creada
- [ ] Archivo WSGI configurado
- [ ] Archivos estáticos configurados
- [ ] Aplicación recargada
- [ ] Prueba la URL pública

---

## 🆓 Limitaciones de la Cuenta Gratuita

PythonAnywhere Free Tier:
- ✅ 1 aplicación web
- ✅ Dominio: `tuusuario.pythonanywhere.com`
- ⚠️ Solo HTTPS para dominios propios (cuenta paga)
- ⚠️ Acceso limitado a APIs externas (whitelist)
- ⚠️ 512 MB de espacio en disco
- ⚠️ CPU limitado

**Whitelist de APIs**: PythonAnywhere tiene una lista blanca de dominios permitidos.
- ✅ Google Fonts: Permitido
- ✅ CDNs comunes: Permitidos
- ✅ API de Gemini: Permitido
- ✅ unpkg.com: Permitido

---

## 🎯 Conclusión

Tu aplicación **funcionará perfectamente** en PythonAnywhere sin ningún problema.

**Características de la aplicación**:
- ✅ Landing page responsiva
- ✅ Carousels interactivos (Hero, Especialidades, Testimonios)
- ✅ Diseño moderno con Tailwind CSS
- ✅ Animaciones suaves
- ✅ Modales de login/registro
- ✅ Menú móvil responsive

**Tiempo estimado de despliegue**: 15-20 minutos

¡Buena suerte con tu despliegue! 🚀
