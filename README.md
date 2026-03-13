# 🚢 NavRoute AI

Sistema de optimización de rutas navales con Inteligencia Artificial.

## 🚀 Deploy en Render.com (gratis)

1. Sube este repositorio a GitHub
2. Ve a [render.com](https://render.com) → New → Web Service
3. Conecta tu repo de GitHub
4. Render detecta el `render.yaml` automáticamente
5. Click **Deploy** — en 2-3 minutos estará en línea

## 🔑 Credenciales de acceso

| Usuario | Contraseña |
|---------|------------|
| admin   | admin123   |
| demo    | demo2024   |

## 🛠️ Ejecutar localmente

```bash
pip install -r requirements.txt
python app.py
```

Abre `http://localhost:5000`

## 📁 Estructura

```
NAVY/
├── app.py              # Backend Flask + motor IA
├── requirements.txt    # Dependencias Python
├── render.yaml         # Configuración Render.com
├── .gitignore
└── templates/
    ├── login.html      # Página de acceso
    └── dashboard.html  # Panel principal con mapa
```

## ⚙️ Tecnologías

- **Backend:** Flask (Python)
- **Frontend:** HTML5 + CSS3 + JavaScript vanilla
- **Mapa:** Leaflet.js con tiles CartoDB Dark
- **Deploy:** Render.com (gratis)
