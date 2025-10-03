import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g, flash
import os
from datetime import datetime
import click
from flask.cli import with_appcontext

# Define la ruta de la base de datos SQLite
DATABASE = 'libro_de_contenidos.db'

# Crea la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) # Clave secreta segura para sesiones y mensajes flash

# --- Contenidos predefinidos de la materia ---
CONTENIDOS_MATERIA = {
    "Módulo Diseño de Algoritmos": [
        "Concepto de algoritmo",
        "Especificación de programas",
        "Predicados, precondiciones y postcondiciones"
    ],
    "Módulo Paradigmas de Programación": [
        "Conceptos básicos de programación funcional, conceptos de recursión y su implementación en el paradigma funcional",
        "El tipo de datos lista, funciones sobre listas",
        "Condiciones de terminación de programas funcionales",
        "Principios de la programación imperativa",
        "Conceptos básicos: acciones y comandos, valores y expresiones, tipos, estado",
        "Estructuras de control: secuencia, selección, iteración",
        "Variables, registros",
        "El tipo de dato arreglo",
        "Principios de la programación estructurada: Funciones y procedimientos, pasaje de parámetros",
        "Modularización de programas",
        "Conceptos del paradigma orientado a objetos",
        "Objetos y mensajes",
        "Métodos, clases herencia y polimorfismo"
    ]
}

# --- Configuración de la Base de Datos ---

def get_db():
    """Establece la conexión a la base de datos, reutilizando si ya está abierta."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # Configura el motor de filas para devolver diccionarios (acceso por nombre de columna)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Cierra la conexión a la base de datos al finalizar la solicitud."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Inicializa la base de datos ejecutando el script SQL."""
    with app.app_context():
        db = get_db()
        with app.open_resource('base_de_datos.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        
@click.command('init-db')
@with_appcontext
def init_db_command():
    """
    Comando para inicializar la base de datos.
    Ejecutar con: flask init-db
    """
    init_db()
    click.echo('Base de datos inicializada correctamente.')

app.cli.add_command(init_db_command)
# --- Rutas de la Aplicación ---

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Ruta principal. Maneja la visualización de registros y la inserción de nuevos registros.
    """
    db = get_db()
    
    if request.method == 'POST':
        # Obtiene los datos del formulario
        dia = request.form['dia']
        mes = request.form['mes']
        clase_nro = request.form['clase_nro']
        unidad_nro = request.form['unidad_nro']
        caracter_clase = request.form['caracter_clase']
        # Se obtienen los contenidos como una lista y se unen en un string
        contenidos_seleccionados = request.form.getlist('contenidos')
        contenidos = " | ".join(contenidos_seleccionados)
        actividades = request.form['actividades']
        observaciones = request.form['observaciones']

        # Validación simple de datos
        if not dia or not mes or not clase_nro or not unidad_nro:
            flash('Los campos de fecha, clase y unidad son obligatorios.', 'error')
            return redirect(url_for('index'))
        if not contenidos:
            flash('Debe seleccionar al menos un contenido.', 'error')
            return redirect(url_for('index'))

        try:
            # Inserción en la base de datos
            db.execute(
                "INSERT INTO registro_clase (dia, mes, clase_nro, unidad_nro, caracter_clase, contenidos, actividades, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (int(dia), int(mes), int(clase_nro), int(unidad_nro), caracter_clase, contenidos, actividades, observaciones)
            )
            db.commit()
            flash('Registro guardado con éxito.', 'success')
            
            # Redirecciona para evitar reenvío del formulario (patrón PRG)
            return redirect(url_for('index'))
            
        except ValueError:
            # Error si los campos numéricos no son números válidos
            flash('Error: Día, Mes, Clase Nro y Unidad Nro deben ser números.', 'error')
            print("Error de conversión: los campos de fecha/número no son válidos.")

        except Exception as e:
            # En caso de error, imprime el error en la consola
            flash(f'Error al guardar el registro: {e}', 'error')
            print(f"Error al guardar el registro: {e}")
            
    # Obtiene todos los registros ordenados por fecha de forma descendente
    registros = db.execute("SELECT * FROM registro_clase ORDER BY id DESC").fetchall()
    
    # Preparar datos iniciales para el formulario (autocompletar la fecha de hoy)
    hoy = datetime.now()
    # Para tu formato (Día, Mes, Clase Nro)
    datos_iniciales = {
        'dia': hoy.strftime('%d'), 
        'mes': hoy.strftime('%m'),
        'clase_nro': '' # Dejar en blanco para que el docente lo complete
    }

    return render_template('index.html', registros=registros, datos_iniciales=datos_iniciales, contenidos_materia=CONTENIDOS_MATERIA)

@app.route('/eliminar/<int:registro_id>', methods=['POST'])
def eliminar(registro_id):
    """Ruta para eliminar un registro por su ID."""
    try:
        db = get_db()
        db.execute("DELETE FROM registro_clase WHERE id = ?", (registro_id,))
        db.commit()
        flash('Registro eliminado correctamente.', 'success')
    except Exception as e:
        flash(f'Error al eliminar el registro {registro_id}.', 'error')
        print(f"Error al eliminar el registro {registro_id}: {e}")
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Nota: Para inicializar la base de datos por primera vez,
    # abre una terminal en esta carpeta y ejecuta:
    # > flask init-db
    app.run(debug=True)
