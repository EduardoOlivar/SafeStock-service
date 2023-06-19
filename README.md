# SafeStock: Backend de proyecto de título
# José Olivar / Jean Rodríguez

## Requisitos

1. Tener python3 instalado
2. Tener MySQL versión 8.0.30 o superior
3. MySQL Workbench para correr localmente la base de datos
4. Tener VSC o Pycharm

### Clonar el repositorio

Primero clonar el repositorio

### Configuración del entorno virtual

Segundo abrir la terminal y escribir el siguiente comando:

```py -m venv venv```

Si usa VSC apretar f1 y escribir "interpreter, escoger la opción Python 3.10.x ('venv':venv), luego cerrar la consola y volver a abrir la terminal en command prompt (CMD)

Si ocupa PyCharm debe ver que su interprete sea seleccionado en su versión de Python3 y también utilizar command prompt (cmd).

Debe aparecer en paréntesis (venv) al costado izquierdo de la ruta en la terminal para seguir.

### Instalación de dependencias

Para instalar las dependencias desde el archivo requirements.txt escriba el siguiente comando:

```pip install -r requirements.txt```


### Configuración de la base de datos

Luego que se instalen las dependencias, es necesario tener MySQL Workbench  y MySQL Server en su versión 8.0.30 o superior, para poder crear el esquema de la base de datos.

Crear un usuario por defecto (root) con una contraseña de su elección.

Abre el archivo `settings.py` ubicado en la carpeta "backend".

Se debe encontrar con este apartado

```python
   DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'safe_stock',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '3306'
        }
    }
```

Aquí debe incluir la contraseña de su base de datos en la key 

```'PASSWORD': 'Aquí poner su contraseña'``` 

Cuando ya se tenga la contraseña, en MySQL Workbench debe crear un schema con este nombre "safe_stock".

### Migraciones y ejecución del servidor

Luego de la creación del esquema, en la terminal escribir el siguiente comando.

```py manage.py migrate```

Este comando creara la base de datos con sus tablas a través del ORM de Django.

Inicia el servidor ejecutando el siguiente comando en la terminal:

```py manage.py runserver```

