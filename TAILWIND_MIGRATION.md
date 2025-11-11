# Migración de Tailwind CSS de CDN a CLI

## ✅ Cambios realizados

Se ha migrado exitosamente de Tailwind CSS CDN a Tailwind CSS CLI para mejor rendimiento y control.

### Archivos creados:
- `tailwind.config.js` - Configuración de Tailwind CSS
- `static/css/input.css` - Archivo de entrada con directivas de Tailwind
- `static/css/output.css` - Archivo CSS compilado (generado automáticamente)

### Plugins instalados:
- `@tailwindcss/forms` - Estilos mejorados para formularios
- `@tailwindcss/typography` - Estilos para contenido tipográfico

### Templates actualizados:
✅ **52 archivos HTML** actualizados para usar el CSS compilado en lugar del CDN

## 🚀 Comandos disponibles

### Compilar CSS para producción (minificado):
```bash
npm run build:css
```

### Modo desarrollo (watch mode - recompila automáticamente):
```bash
npm run watch:css
```

## 📝 Workflow de desarrollo

1. **Durante el desarrollo**, ejecuta el watch mode en una terminal:
   ```bash
   npm run watch:css
   ```
   Esto detectará automáticamente cambios en tus templates y recompilará el CSS.

2. **Antes de hacer commit**, asegúrate de compilar para producción:
   ```bash
   npm run build:css
   ```

3. **El archivo `static/css/output.css`** debe incluirse en el repositorio para producción.

## 🎯 Ventajas de esta migración

✅ **Mejor rendimiento**: El CSS se descarga más rápido (minificado y optimizado)
✅ **Sin dependencia de CDN**: Funciona offline y sin conexión a internet
✅ **CSS purgeado**: Solo incluye las clases que realmente usas
✅ **Mayor control**: Puedes personalizar completamente la configuración
✅ **Plugins disponibles**: Forms y Typography para mejor UX

## 📂 Estructura de archivos CSS

```
static/css/
├── input.css    → Archivo fuente (editar este)
└── output.css   → Archivo compilado (generado automáticamente, no editar)
```

## ⚠️ Importante

- **NO edites** `static/css/output.css` manualmente
- Todos los estilos personalizados deben ir en `static/css/input.css`
- Para personalizar Tailwind, edita `tailwind.config.js`
- El archivo `output.css` debe estar en el repositorio para producción

## 🔧 Personalización

Para añadir estilos personalizados, edita `static/css/input.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Tus estilos personalizados aquí */
.mi-clase-custom {
  /* ... */
}
```

Para extender la configuración de Tailwind, edita `tailwind.config.js`.
