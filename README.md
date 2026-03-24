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
