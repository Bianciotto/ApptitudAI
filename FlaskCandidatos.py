import re
from flask import Flask, flash, redirect, render_template, request, send_file, session, url_for
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
import webbrowser
import numpy as np
import threading
import joblib
import os
import sys
import matplotlib.pyplot as plt
import io
import base64


app = Flask(__name__)
app.secret_key = "MiraQueSéQueMeVes"  # Necesario para sesiones

def abrir_navegador():
    webbrowser.open("http://127.0.0.1:5000/")  # URL de Flask

# 🔹 Obtener la ruta correcta dentro del ejecutable
def get_path(relative_path):
    """Obtiene la ruta absoluta, considerando si se ejecuta como .exe"""
    if getattr(sys, 'frozen', False):
        # Si se ejecuta como ejecutable de PyInstaller
        base_path = sys._MEIPASS
    else:
        # Si se ejecuta como script Python normal
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# 🔹 Cargar el modelo correctamente
modelo_path = get_path("modelo_candidatos.pkl")
modelo = joblib.load(modelo_path)


try:
    encoder_educacion = joblib.load("encoder_educacion.pkl")
    encoder_habilidades = joblib.load("encoder_habilidades.pkl")
    encoder_tecnologias = joblib.load("encoder_tecnologias.pkl")
    
except FileNotFoundError as e:
    print("Error: No se pudo cargar el archivo del encoder.", e)
    raise e
except Exception as e:
    print("Error al cargar los encoders:", e)
    raise e


# Página principal
@app.route("/")
def home():

    encoder_educacion_path = get_path("encoder_educacion.pkl")
    encoder_habilidades_path = get_path("encoder_habilidades.pkl")
    encoder_tecnologias_path = get_path("encoder_tecnologias.pkl")

    encoder_educacion = joblib.load(encoder_educacion_path)
    session["opciones_educacion"] = list(encoder_educacion.classes_)
    encoder_habilidades = joblib.load(encoder_habilidades_path)
    session["opciones_habilidades"] = list(encoder_habilidades.classes_)
    encoder_tecnologias = joblib.load(encoder_tecnologias_path)
    session["opciones_tecnologias"] = list(encoder_tecnologias.classes_)

    return render_template(
        "postulacion.html",
        opciones_educacion=session["opciones_educacion"],
        opciones_habilidades=session["opciones_habilidades"],
        opciones_tecnologias=session["opciones_tecnologias"]
    )

    
@app.route("/postulacion", methods=["GET", "POST"])
def postulacion():
    # Inicializar valores dinámicos para los inputs select
    encoder_educacion_path = get_path("encoder_educacion.pkl")
    encoder_habilidades_path = get_path("encoder_habilidades.pkl")
    encoder_tecnologias_path = get_path("encoder_tecnologias.pkl")
    encoder_educacion = joblib.load(encoder_educacion_path)
    session["opciones_educacion"] = list(encoder_educacion.classes_)
    encoder_habilidades = joblib.load(encoder_habilidades_path)
    session["opciones_habilidades"] = list(encoder_habilidades.classes_)
    encoder_tecnologias = joblib.load(encoder_tecnologias_path)
    session["opciones_tecnologias"] = list(encoder_tecnologias.classes_)
    
    candidatosLocales_path = get_path("candidatosLocales.csv")
    dataSet = pd.read_csv(candidatosLocales_path)
    
    if "candidatos" not in session:
        session["candidatos"] = []

    if request.method == "POST":
        # Obtener datos del formulario
        nombre = request.form["nombre"]

        apellido = request.form["apellido"]

        email = request.form["email"]
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            flash("Correo electrónico inválido. Por favor ingresa un email válido.")
            return redirect("/postulacion")
        
        telefono = request.form["telefono"]
        # Validación fuerte: solo números, y cantidad entre 8 y 10
        if not telefono.isdigit() or len(telefono) < 8 or len(telefono) > 10:
            flash("El teléfono debe contener solo números y tener entre 8 y 10 cifras.")
            return redirect("/postulacion")
        
        ubicacion = request.form["ubicacion"]
        PROVINCIAS_ARG = [
        "Buenos Aires", "CABA", "Catamarca", "Chaco", "Chubut", "Córdoba",
        "Corrientes", "Entre Ríos", "Formosa", "Jujuy", "La Pampa", "La Rioja",
        "Mendoza", "Misiones", "Neuquén", "Río Negro", "Salta", "San Juan",
        "San Luis", "Santa Cruz", "Santa Fe", "Santiago del Estero",
        "Tierra del Fuego", "Tucumán"]
        if ubicacion not in PROVINCIAS_ARG:
            flash("Ubicación no válida. Selecciona una provincia de Argentina.")
            return redirect("/postulacion")
        
        experiencia = int(request.form["experiencia"])
        
        educacion = request.form["educacion"]
        
        tecnologias = request.form["tecnologias"]
        
        habilidades = request.form["habilidades"]

        # Crear un nuevo candidato como un diccionario
        nuevo_candidato = {
            "Nombre": nombre,
            "Apellido": apellido,
            "Correo electrónico": email,
            "Teléfono": telefono,
            "Ubicación": ubicacion,
            "Experiencia": experiencia,
            "Educacion": educacion,
            "Tecnologías": tecnologias,
            "Habilidades": habilidades,
            "Apto": ""  # La columna Apto se evaluará después
        }

        # Convertir el diccionario a un DataFrame de una sola fila
        nuevo_df = pd.DataFrame([nuevo_candidato])

        # Agregar al dataset existente
        dataSet = pd.concat([dataSet, nuevo_df], ignore_index=True)

        # Guardar cambios en el archivo CSV
        dataSet.to_csv(candidatosLocales_path, index=False)

        #redirect a una pagina que muestre mi cv cargado o solo un cartelito que diga cargado exitosamente

    # Renderizar la página HTML con los candidatos actuales
    return render_template(
        "postulacion.html",
        candidatos=session["candidatos"],
        opciones_educacion=session["opciones_educacion"],
        opciones_habilidades=session["opciones_habilidades"],
        opciones_tecnologias=session["opciones_tecnologias"]
    )

if __name__ == "__main__":
    threading.Timer(1.5, abrir_navegador).start() 
    app.run(debug=False, host="127.0.0.1", port=5000)
