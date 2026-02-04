# GymBase

Aplicación de escritorio para gestión de gimnasios (Control de Acceso y Membresías).

## Características
- **Control de Acceso**: Verificación rápida por ID. Indica si la membresía está activa, vencida o congelada.
- **Registro de Miembros**: Formulario sencillo para nuevos usuarios.
- **Gestión de Miembros**: Lista de todos los miembros con búsqueda.
- **Edición**: Actualizar datos, renovar membresía (días/meses/años), congelar/descongelar tiempo.
- **Base de Datos**: SQLite local (sin configuración compleja).
- **Interfaz**: Moderna y limpia (Modo Oscuro/Claro).

## Requisitos
- Python 3.7+
- Dependencias listadas en `requirements.txt`

## Instalación

1. **Crear un entorno virtual** (Recomendado para evitar errores de conflictos en Linux):
   ```bash
   # Si no tienes venv instalado:
   # sudo apt install python3-venv python3-tk

   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
   *Nota: Si no usas entorno virtual y tienes errores, intenta `pip install -r requirements.txt --break-system-packages` bajo tu propio riesgo.*

## Ejecución

Para iniciar la aplicación:

```bash
# Asegúrate de tener el entorno activado si lo creaste
# source venv/bin/activate
python3 main.py
```

## Estructura del Proyecto

- `main.py`: Punto de entrada y configuración de la ventana principal.
- `views.py`: Definición de las pantallas (Inicio, Registro, Lista).
- `database.py`: Lógica de conexión y consultas a SQLite.
- `gym.db`: Archivo de base de datos (se crea automáticamente).
