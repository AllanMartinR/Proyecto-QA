"""
Archivo de configuración para PythonAnywhere
Este archivo contiene las configuraciones específicas para el despliegue en PythonAnywhere.
Copia estas configuraciones en la consola de PythonAnywhere o úsalas como referencia.
"""

# Configuraciones para PythonAnywhere
# Reemplaza 'tunombre' con tu nombre de usuario de PythonAnywhere

PYTHONANYWHERE_USERNAME = 'tunombre'  # CAMBIA ESTO

# Configuraciones de entorno para PythonAnywhere
ENV_VARS = {
    'SECRET_KEY': 'django-insecure-y*1ic_w3lzm(=+fwo-r2yhg6fjcq5_%ah4lk6j)$dk(mv4g=jf',  # Cambia esto por una clave segura
    'DEBUG': 'False',
    'ALLOWED_HOSTS': f'{PYTHONANYWHERE_USERNAME}.pythonanywhere.com',
    'STATIC_ROOT': f'/home/{PYTHONANYWHERE_USERNAME}/screwfx_project/staticfiles',
    'MEDIA_ROOT': f'/home/{PYTHONANYWHERE_USERNAME}/screwfx_project/media',
}

# Rutas en PythonAnywhere
PATHS = {
    'project_path': f'/home/{PYTHONANYWHERE_USERNAME}/screwfx_project',
    'virtualenv_path': f'/home/{PYTHONANYWHERE_USERNAME}/.virtualenvs/screwfx_env',
    'static_files_path': f'/home/{PYTHONANYWHERE_USERNAME}/screwfx_project/staticfiles',
    'media_files_path': f'/home/{PYTHONANYWHERE_USERNAME}/screwfx_project/media',
}

# Configuración WSGI
WSGI_CONFIG = f"""
# Archivo WSGI para PythonAnywhere
# Ubicación: /var/www/{PYTHONANYWHERE_USERNAME}_pythonanywhere_com_wsgi.py

import os
import sys

# Agrega la ruta del proyecto al path
path = '/home/{PYTHONANYWHERE_USERNAME}/screwfx_project'
if path not in sys.path:
    sys.path.append(path)

# Configura las variables de entorno
os.environ['DJANGO_SETTINGS_MODULE'] = 'screwfx_project.settings'
os.environ['SECRET_KEY'] = '{ENV_VARS["SECRET_KEY"]}'
os.environ['DEBUG'] = '{ENV_VARS["DEBUG"]}'
os.environ['ALLOWED_HOSTS'] = '{ENV_VARS["ALLOWED_HOSTS"]}'
os.environ['STATIC_ROOT'] = '{ENV_VARS["STATIC_ROOT"]}'
os.environ['MEDIA_ROOT'] = '{ENV_VARS["MEDIA_ROOT"]}'

# Activa el entorno virtual
activate_this = '/home/{PYTHONANYWHERE_USERNAME}/.virtualenvs/screwfx_env/bin/activate_this.py'
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {{'__file__': activate_this}})

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
"""

print("Configuración para PythonAnywhere generada.")
print(f"Usuario: {PYTHONANYWHERE_USERNAME}")
print("\nIMPORTANTE: Reemplaza 'tunombre' con tu nombre de usuario real de PythonAnywhere")



