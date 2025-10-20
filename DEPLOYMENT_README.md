# Clínica Unión - Aplicación Flask

## 🎯 Cambios Realizados

Se ha convertido el archivo `home.html` para que funcione con Flask, separando el CSS y JavaScript en archivos independientes para mejorar el rendimiento y la mantenibilidad.

### Archivos Modificados/Creados:

1. **`templates/home.html`** - Archivo HTML principal optimizado para Flask
   - Usa `url_for()` para referenciar archivos estáticos
   - Eliminado CSS y JS inline
   - Optimizado para carga rápida con `defer` en scripts

2. **`static/css/home.css`** - Estilos CSS separados
   - Todas las animaciones y estilos personalizados
   - Estilos del chatbot
   - Estilos de Swiper carousels

3. **`static/js/home.js`** - JavaScript separado
   - Inicialización de Swiper carousels
   - Menú móvil y modales de autenticación
   - Animaciones de scroll

4. **`app.py`** - Actualizado para renderizar el template

## 🚀 Optimizaciones Implementadas

### Rendimiento:
- ✅ **Preconnect** a dominios externos (Google Fonts, unpkg)
- ✅ Scripts con atributo `defer` para carga asíncrona
- ✅ Versión específica de Swiper (v8) en lugar de "latest"
- ✅ Importmap para Gemini AI SDK
- ✅ CSS y JS externos en lugar de inline

### Estructura:
- ✅ Separación de responsabilidades (HTML/CSS/JS)
- ✅ Código modular y mantenible
- ✅ Fácil de actualizar y debuguear

## 📦 Configuración

### 1. Instalar dependencias Python:
```bash
pip install flask
```

### 2. Ejecutar la aplicación:
```bash
python app.py
```

La aplicación estará disponible en: `http://127.0.0.1:5000`

## 🔧 Estructura del Proyecto

```
Proyecto-Ingenieria-y-calidad/
├── app.py                          # Aplicación Flask principal
├── templates/
│   └── home.html                   # Template HTML
├── static/
│   ├── css/
│   │   ├── estilos.css            # CSS existente
│   │   └── home.css               # CSS nuevo para home.html
│   └── js/
│       ├── scripts.js             # JS existente
│       └── home.js                # JS nuevo para home.html
├── models/                         # Modelos de datos
├── routes/                         # Rutas adicionales
└── requirements.txt
```

## ⚡ Características

### Funcionalidades Implementadas:
- 🏥 Landing page de clínica médica
- 🎠 Carousels con Swiper (Hero, Especialidades, Testimonios)
- 📱 Diseño responsive (móvil, tablet, desktop)
- 🔐 Modales de login y registro
- ✨ Animaciones suaves con Intersection Observer
- 📍 Mapa de ubicación

### Enlaces Externos Utilizados:
- **Tailwind CSS**: Framework CSS (CDN)
- **Google Fonts**: Fuente Inter
- **Swiper JS**: Biblioteca de carousels (v8)

## 📱 Compatibilidad

- ✅ Chrome/Edge (Últimas versiones)
- ✅ Firefox (Últimas versiones)
- ✅ Safari (Últimas versiones)
- ✅ Móviles (iOS/Android)

## 🛠️ Desarrollo

### Para agregar nuevas páginas:
1. Crea un nuevo template en `templates/`
2. Crea archivos CSS/JS específicos en `static/`
3. Agrega la ruta en `app.py` o en `routes/`

### Para modificar estilos:
- Edita `static/css/home.css`
- Los cambios se reflejarán automáticamente (con debug=True)

### Para modificar funcionalidad:
- Edita `static/js/home.js`
- Recarga la página para ver los cambios

## 📝 Notas Adicionales

- Los archivos `static/css/estilos.css` y `static/js/scripts.js` originales se mantienen sin cambios
- El template usa Tailwind CSS desde CDN (considera usar la versión compilada en producción)
- Las imágenes usan placeholders de placehold.co (reemplazar con imágenes reales)

## 🐛 Solución de Problemas

### Los estilos no se cargan:
- Verifica que la carpeta `static/` exista
- Asegúrate de que Flask está corriendo con `debug=True`
- Limpia la caché del navegador (Ctrl + F5)

### Los carousels no funcionan:
- Verifica que Swiper JS se haya cargado correctamente
- Revisa la consola del navegador

## 📞 Soporte

Para problemas o preguntas, revisa:
- Documentación de Flask: https://flask.palletsprojects.com/
- Documentación de Swiper: https://swiperjs.com/
- Documentación de Gemini AI: https://ai.google.dev/
