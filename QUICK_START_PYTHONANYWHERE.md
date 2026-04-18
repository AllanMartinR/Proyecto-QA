# Guía Rápida: Despliegue en PythonAnywhere

## 🚀 Pasos Rápidos

### 1. Subir Proyecto
```bash
# Opción A: Git
cd ~
git clone https://github.com/tu-usuario/tu-repo.git screwfx_project

# Opción B: Panel de Archivos de PythonAnywhere
# Sube la carpeta screwfx_project completa
```

### 2. Configurar Entorno Virtual
```bash
cd ~/screwfx_project
mkvirtualenv --python=/usr/bin/python3.10 screwfx_env
workon screwfx_env
pip install -r requirements.txt
```

### 3. Configurar Base de Datos
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 4. Configurar WSGI
Edita `/var/www/tunombre_pythonanywhere_com_wsgi.py`:

```python
import os
import sys

path = '/home/tunombre/screwfx_project'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'screwfx_project.settings'
os.environ['SECRET_KEY'] = 'tu-secret-key-aqui'
os.environ['DEBUG'] = 'False'
os.environ['ALLOWED_HOSTS'] = 'tunombre.pythonanywhere.com'
os.environ['STATIC_ROOT'] = '/home/tunombre/screwfx_project/staticfiles'
os.environ['MEDIA_ROOT'] = '/home/tunombre/screwfx_project/media'

activate_this = '/home/tunombre/.virtualenvs/screwfx_env/bin/activate_this.py'
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {'__file__': activate_this})

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 5. Configurar Archivos Estáticos (Panel Web)
- Ve a **Web** → **Static files**
- Agrega:
  - URL: `/static/` → Directorio: `/home/tunombre/screwfx_project/staticfiles`
  - URL: `/media/` → Directorio: `/home/tunombre/screwfx_project/media`

### 6. Recargar
- Haz clic en **Reload** en el Panel Web

## ⚠️ Recordatorios

- Reemplaza `tunombre` con tu usuario de PythonAnywhere
- Cambia `SECRET_KEY` por una clave segura
- Verifica que `DEBUG = False` en producción

## 📖 Tutorial Completo

Para más detalles, consulta `TUTORIAL_PYTHONANYWHERE.md`



