# Gestor de Reservas de Hoteles

Aplicación web desarrollada con **Django 4.2** que permite gestionar hoteles, habitaciones y reservas. Los usuarios pueden explorar hoteles, consultar disponibilidad por fechas y realizar reservas con soporte de recurrencia.

## Funcionalidades

- Listado público de hoteles activos
- Detalle de hotel con filtro de disponibilidad por rango de fechas
- Sistema de reservas con validación de solapamiento
- Reservas recurrentes (diaria, semanal, mensual…)
- Registro, inicio y cierre de sesión de usuarios
- **Panel de administración** (Django Admin + Jazzmin) con gestión completa de hoteles, habitaciones, reservas y usuarios
- 32 tests automatizados

## Requisitos del proyecto cubiertos

| Requisito | Estado |
|---|---|
| Evitar solapamiento de reservas | ✅ |
| Reservas recurrentes | ✅ |
| Calendario de disponibilidad por fechas | ✅ |
| Panel de gestión para admins *(extra opcional)* | ✅ |

## Tecnologías

- Python 3.8 / Django 4.2.29
- SQLite (desarrollo) 
- Bootstrap 5
- django-jazzmin · django-recurrence · django-scheduler · django-notifications-hq

## Instalación local

```bash
git clone https://github.com/tu-usuario/gestorReservas.git
cd gestorReservas/gestor

python -m venv env
source env/bin/activate

pip install -r requirements.txt

DEBUG=True python manage.py migrate
DEBUG=True python manage.py cargar_demo
DEBUG=True python manage.py runserver
```

Abre `http://127.0.0.1:8000/` en el navegador.

## Datos de demo

El comando `cargar_demo` crea automáticamente:

- 2 hoteles con 3 habitaciones cada uno
- Usuario **demo** con una reserva activa
- Superusuario para el panel de admin

| | |
|---|---|
| **Admin** | `/admin/` |
| **Usuario** | `admin` |
| **Contraseña** | `Admin1234!` |

## Despliegue en PythonAnywhere

1. Clona el repo en la consola Bash de PythonAnywhere
2. Crea un virtualenv e instala `requirements.txt`
3. Configura las variables de entorno en la pestaña **Web**:

   | Variable | Valor |
   |---|---|
   | `SECRET_KEY` | clave secreta larga |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `tuusuario.pythonanywhere.com` |

4. Apunta el fichero WSGI a `gestor.settings`
5. Añade las rutas de estáticos y media en la pestaña **Web**
6. Ejecuta las migraciones y carga los datos de demo:

   ```bash
   python manage.py migrate
   python manage.py collectstatic --no-input
   python manage.py cargar_demo
   ```

## Tests

```bash
DEBUG=True python manage.py test core bookings
```

Resultado esperado: **32 tests OK**

## Estructura del proyecto

```
gestor/
├── bookings/        # App de habitaciones y reservas
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── available_logic.py   # Lógica de disponibilidad
│   ├── createService.py     # Servicio de creación de reservas
│   └── management/commands/cargar_demo.py
├── core/            # App de hoteles y usuarios
│   ├── models.py
│   ├── views.py
│   ├── admin.py     # Panel de admin personalizado
│   └── templates/
├── gestor/          # Configuración del proyecto
│   └── settings.py
└── requirements.txt
```
