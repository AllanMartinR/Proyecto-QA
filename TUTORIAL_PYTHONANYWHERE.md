# Tutorial: Desplegar Django ScrewFX en PythonAnywhere

Este tutorial te guiará paso a paso para desplegar tu aplicación Django ScrewFX en PythonAnywhere.

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Crear Cuenta en PythonAnywhere](#crear-cuenta-en-pythonanywhere)
3. [Preparar el Proyecto Localmente](#preparar-el-proyecto-localmente)
4. [Subir el Proyecto a PythonAnywhere](#subir-el-proyecto-a-pythonanywhere)
5. [Configurar el Entorno Virtual](#configurar-el-entorno-virtual)
6. [Configurar la Base de Datos](#configurar-la-base-de-datos)
7. [Configurar Archivos Estáticos y Media](#configurar-archivos-estáticos-y-media)
8. [Configurar WSGI](#configurar-wsgi)
9. [Configurar Archivos Estáticos en el Panel Web](#configurar-archivos-estáticos-en-el-panel-web)
10. [Configurar Tareas Programadas (Opcional)](#configurar-tareas-programadas-opcional)
11. [Solución de Problemas](#solución-de-problemas)

---

## 1. Requisitos Previos

- ✅ Cuenta en PythonAnywhere (gratuita o de pago)
- ✅ Proyecto Django funcionando localmente
- ✅ Git instalado (opcional, pero recomendado)
- ✅ Acceso a la consola de PythonAnywhere

---

## 2. Crear Cuenta en PythonAnywhere

1. Ve a [https://www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Haz clic en **"Sign up for free"** o **"Sign in"** si ya tienes cuenta
3. Completa el registro (puedes usar cuenta gratuita para empezar)
4. Anota tu **nombre de usuario** (lo necesitarás más adelante)

---

## 3. Preparar el Proyecto Localmente

### 3.1. Verificar requirements.txt

Asegúrate de que tu `requirements.txt` contenga todas las dependencias:

```txt
Django==5.2.7
psycopg2-binary==2.9.9
Pillow==10.4.0
whitenoise==6.6.0
gunicorn==21.2.0
```

### 3.2. Recopilar archivos estáticos (opcional, se hará en PythonAnywhere)

```bash
python manage.py collectstatic --noinput
```

### 3.3. Crear un archivo .gitignore (si usas Git)

```gitignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
db.sqlite3
*.log
.DS_Store
media/
staticfiles/
```

---

## 4. Subir el Proyecto a PythonAnywhere

### Opción A: Usando Git (Recomendado)

1. **Sube tu proyecto a GitHub/GitLab/Bitbucket** (si aún no lo has hecho):
   ```bash
   git init
   git add .
   git commit -m "Preparado para PythonAnywhere"
   git remote add origin https://github.com/tu-usuario/tu-repositorio.git
   git push -u origin main
   ```

2. **En PythonAnywhere, clona el repositorio**:
   - Abre una consola Bash en PythonAnywhere
   - Navega a tu directorio home:
     ```bash
     cd ~
     ```
   - Clona el repositorio:
     ```bash
     git clone https://github.com/tu-usuario/tu-repositorio.git screwfx_project
     ```

### Opción B: Usando el Panel de Archivos de PythonAnywhere

1. Ve al **Panel de Archivos** en PythonAnywhere
2. Navega a `/home/tunombre/` (reemplaza `tunombre` con tu usuario)
3. Crea una carpeta llamada `screwfx_project`
4. Sube todos los archivos de tu proyecto usando el **upload** del panel
   - **IMPORTANTE**: Sube la carpeta `screwfx_project` completa, manteniendo la estructura

### Opción C: Usando SCP o SFTP

```bash
# Desde tu máquina local
scp -r screwfx_project/ tunombre@ssh.pythonanywhere.com:/home/tunombre/
```

---

## 5. Configurar el Entorno Virtual

1. **Abre una consola Bash** en PythonAnywhere

2. **Navega a tu proyecto**:
   ```bash
   cd ~/screwfx_project
   ```

3. **Crea un entorno virtual**:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 screwfx_env
   ```
   O si ya existe:
   ```bash
   workon screwfx_env
   ```

4. **Instala las dependencias**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Verifica la instalación**:
   ```bash
   python --version
   django-admin --version
   ```

---

## 6. Configurar la Base de Datos

1. **En la consola Bash, navega a tu proyecto**:
   ```bash
   cd ~/screwfx_project
   workon screwfx_env
   ```

2. **Ejecuta las migraciones**:
   ```bash
   python manage.py migrate
   ```

3. **Crea un superusuario** (si no lo tienes):
   ```bash
   python manage.py createsuperuser
   ```

4. **Si tienes datos locales que quieres importar**:
   - Sube tu `db.sqlite3` al servidor
   - O exporta/importa datos usando fixtures:
     ```bash
     # En local
     python manage.py dumpdata > datos.json
     
     # En PythonAnywhere
     python manage.py loaddata datos.json
     ```

---

## 7. Configurar Archivos Estáticos y Media

### 7.1. Recopilar archivos estáticos

En la consola Bash de PythonAnywhere:

```bash
cd ~/screwfx_project
workon screwfx_env
python manage.py collectstatic --noinput
```

Esto creará la carpeta `staticfiles` con todos los archivos estáticos.

### 7.2. Verificar rutas

Asegúrate de que en `settings.py` las rutas estén configuradas correctamente:

```python
STATIC_ROOT = '/home/tunombre/screwfx_project/staticfiles'
MEDIA_ROOT = '/home/tunombre/screwfx_project/media'
```

---

## 8. Configurar WSGI

1. **Ve al Panel Web** en PythonAnywhere
2. Haz clic en **"Add a new web app"** o edita la existente
3. Selecciona **"Manual configuration"** y luego **"Python 3.10"** (o la versión que uses)
4. Haz clic en **"Next"**

5. **Edita el archivo WSGI** (haz clic en el enlace del archivo WSGI):
   - El archivo estará en: `/var/www/tunombre_pythonanywhere_com_wsgi.py`
   - Reemplaza todo el contenido con:

```python
import os
import sys

# Agrega la ruta del proyecto al path
path = '/home/tunombre/screwfx_project'
if path not in sys.path:
    sys.path.append(path)

# Configura las variables de entorno
os.environ['DJANGO_SETTINGS_MODULE'] = 'screwfx_project.settings'
os.environ['SECRET_KEY'] = 'django-insecure-y*1ic_w3lzm(=+fwo-r2yhg6fjcq5_%ah4lk6j)$dk(mv4g=jf'  # CAMBIA ESTO
os.environ['DEBUG'] = 'False'
os.environ['ALLOWED_HOSTS'] = 'tunombre.pythonanywhere.com'  # CAMBIA tunombre
os.environ['STATIC_ROOT'] = '/home/tunombre/screwfx_project/staticfiles'
os.environ['MEDIA_ROOT'] = '/home/tunombre/screwfx_project/media'

# Activa el entorno virtual
activate_this = '/home/tunombre/.virtualenvs/screwfx_env/bin/activate_this.py'
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {'__file__': activate_this})

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**⚠️ IMPORTANTE**: Reemplaza `tunombre` con tu nombre de usuario real de PythonAnywhere en todas las rutas.

6. **Guarda el archivo** y haz clic en **"Reload"** en el Panel Web

---

## 9. Configurar Archivos Estáticos en el Panel Web

1. **Ve al Panel Web** en PythonAnywhere
2. Haz clic en **"Static files"**
3. **Agrega las siguientes rutas**:

   | URL | Directorio |
   |-----|------------|
   | `/static/` | `/home/tunombre/screwfx_project/staticfiles` |
   | `/media/` | `/home/tunombre/screwfx_project/media` |

4. **Guarda los cambios**

---

## 10. Configurar Tareas Programadas (Opcional)

Si necesitas ejecutar tareas periódicas (como limpieza de sesiones):

1. Ve al **Panel de Tareas** (Tasks)
2. Haz clic en **"Create a new scheduled task"**
3. Configura el comando:
   ```bash
   cd /home/tunombre/screwfx_project && /home/tunombre/.virtualenvs/screwfx_env/bin/python manage.py clearsessions
   ```
4. Configura la frecuencia (diaria, semanal, etc.)

---

## 11. Solución de Problemas

### Error: "ModuleNotFoundError"

**Solución**: Asegúrate de que el entorno virtual esté activado en el archivo WSGI y que todas las dependencias estén instaladas.

```bash
workon screwfx_env
pip install -r requirements.txt
```

### Error: "DisallowedHost"

**Solución**: Agrega tu dominio a `ALLOWED_HOSTS` en el archivo WSGI:

```python
os.environ['ALLOWED_HOSTS'] = 'tunombre.pythonanywhere.com'
```

### Error: "You're using the staticfiles app without having set the STATIC_ROOT setting to a filesystem path"

**Solución**: Este error ocurre cuando `STATIC_ROOT` no está configurado como una cadena de texto. Asegúrate de que en `settings.py` esté así:

```python
STATIC_ROOT = os.environ.get('STATIC_ROOT', str(BASE_DIR / 'staticfiles'))
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', str(BASE_DIR / "media"))
```

**Nota**: El `str()` es importante para convertir el objeto `Path` a una cadena de texto que Django pueda usar.

Si el error persiste, puedes configurarlo directamente:

```python
STATIC_ROOT = '/home/Allanmartin/server/screwfx_project/staticfiles'
MEDIA_ROOT = '/home/Allanmartin/server/screwfx_project/media'
```

### Los archivos estáticos no se cargan

**Solución**:
1. Verifica que hayas ejecutado `collectstatic`
2. Verifica las rutas en el Panel Web → Static files
3. Asegúrate de que `STATIC_ROOT` esté correctamente configurado como una cadena de texto

### Error: "No such file or directory"

**Solución**: Verifica que todas las rutas en el archivo WSGI usen tu nombre de usuario correcto.

### La base de datos no funciona

**Solución**:
1. Verifica que las migraciones se hayan ejecutado:
   ```bash
   python manage.py migrate
   ```
2. Verifica los permisos del archivo `db.sqlite3`:
   ```bash
   chmod 664 db.sqlite3
   ```

### Error 500 Internal Server Error

**Solución**:
1. Revisa los logs de error en el Panel Web → **Error log**
2. Verifica que todas las variables de entorno estén configuradas correctamente
3. Asegúrate de que `DEBUG = False` en producción

### Los archivos de media no se muestran

**Solución**:
1. Verifica que la ruta `/media/` esté configurada en el Panel Web → Static files
2. Verifica que `MEDIA_ROOT` esté correctamente configurado
3. Asegúrate de que los archivos estén en la carpeta correcta

---

## 📝 Checklist Final

Antes de considerar el despliegue completo, verifica:

- [ ] Proyecto subido a PythonAnywhere
- [ ] Entorno virtual creado y dependencias instaladas
- [ ] Base de datos migrada
- [ ] Archivos estáticos recopilados (`collectstatic`)
- [ ] Archivo WSGI configurado correctamente
- [ ] Rutas de archivos estáticos y media configuradas en el Panel Web
- [ ] `ALLOWED_HOSTS` configurado con tu dominio
- [ ] `DEBUG = False` en producción
- [ ] Superusuario creado
- [ ] Sitio web accesible en `https://tunombre.pythonanywhere.com`

---

## 🔒 Seguridad Adicional

1. **Cambia la SECRET_KEY**: Genera una nueva clave secreta:
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

2. **Configura HTTPS**: PythonAnywhere proporciona HTTPS automáticamente para dominios `.pythonanywhere.com`

3. **Revisa ALLOWED_HOSTS**: Solo incluye dominios que realmente uses

---

## 📞 Soporte

- **Documentación de PythonAnywhere**: [https://help.pythonanywhere.com](https://help.pythonanywhere.com)
- **Foros de PythonAnywhere**: [https://www.pythonanywhere.com/forums](https://www.pythonanywhere.com/forums)
- **Documentación de Django**: [https://docs.djangoproject.com](https://docs.djangoproject.com)

---

## 🎉 ¡Listo!

Tu aplicación Django ScrewFX debería estar funcionando en PythonAnywhere. Accede a tu sitio en:

**https://tunombre.pythonanywhere.com**

¡Feliz despliegue! 🚀

