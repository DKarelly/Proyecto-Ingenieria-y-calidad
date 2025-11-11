# 🎨 Guía Rápida - Tailwind CSS CLI

## Inicio Rápido

### 1. Compilar CSS (una vez hola)
```bash
npm run build:css
```

### 2. Modo desarrollo (auto-recompilación)
```bash
npm run watch:css
```
Déjalo corriendo mientras desarrollas. Se actualizará automáticamente cuando cambies tus templates.

---

## Flujo de trabajo recomendado

### Terminal 1: Flask (servidor)
```bash
python app.py
```

### Terminal 2: Tailwind Watch (CSS)
```bash
npm run watch:css
```

---

## ¿Dónde añadir estilos?

### ✅ EN LOS TEMPLATES (HTML)
Usa las clases de Tailwind directamente:
```html
<div class="bg-blue-500 text-white p-4 rounded-lg">
    Mi contenido
</div>
```

### ✅ EN `static/css/input.css`
Para estilos personalizados globales:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

.mi-boton-especial {
    @apply bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold py-2 px-4 rounded;
}
```

### ❌ NO EDITAR `static/css/output.css`
Este archivo se genera automáticamente. Cualquier cambio se perderá.

---

## Personalizar Tailwind

Edita `tailwind.config.js` para:
- Añadir colores personalizados
- Modificar breakpoints
- Extender la configuración

Ejemplo:
```js
module.exports = {
  theme: {
    extend: {
      colors: {
        'clinica-blue': '#06B6D4',
        'clinica-green': '#10B981',
      },
    },
  },
}
```

---

## Resolución de problemas

### ❓ Los estilos no se aplican
1. Verifica que `npm run watch:css` esté corriendo
2. Recarga la página con Ctrl+F5 (forzar recarga)
3. Verifica que el template incluya: `<link rel="stylesheet" href="{{ url_for('static', filename='css/output.css') }}">`

### ❓ El archivo CSS es muy grande
Es normal en desarrollo. En producción usa:
```bash
npm run build:css
```
Esto minifica y optimiza el CSS.

---

## Antes de hacer commit

✅ Ejecuta: `npm run build:css`
✅ Incluye `static/css/output.css` en el commit
✅ NO incluyas `node_modules/`

---

## Recursos

- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Tailwind CSS Cheat Sheet](https://nerdcave.com/tailwind-cheat-sheet)
- [Tailwind Play (prueba en vivo)](https://play.tailwindcss.com/)
