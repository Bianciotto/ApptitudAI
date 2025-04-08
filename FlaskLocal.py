from flask import Flask, redirect, render_template, request, send_file, session
import pandas as pd
import webbrowser
import threading
import joblib
import os
import sys

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
# Página principal
@app.route("/")
def home():
    return render_template("index.html")

# Ruta para predecir con un archivo CSV
@app.route("/predecir", methods=["POST"])
def predecir():
    # Verifica que el archivo esté en la solicitud
    if "archivo_csv" not in request.files:
        return "Por favor, sube un archivo CSV."

    file = request.files["archivo_csv"]
    if file.filename == "":
        return "No seleccionaste ningún archivo."

    try:
        # Leer el archivo CSV
        dataSet = pd.read_csv(file)

        # Preprocesar (realiza mapeos necesarios según tu IA)
        educacion_map = {"Secundario": 0, "Universitario": 1, "Postgrado": 2}
        habilidades_map = {
            "Trabajo en equipo": 0, "Comunicación efectiva": 1, "Adaptabilidad": 2,
            "Liderazgo": 3, "Resolución de problemas": 4, "Empatía": 5
        }
        tecnologias_map = {"Python": 0, "Java": 1, "SQL": 2, "C++": 3}

        dataSet["Educacion"] = dataSet["Educacion"].map(educacion_map)
        dataSet["Habilidades"] = dataSet["Habilidades"].map(habilidades_map)
        dataSet["Tecnologías"] = dataSet["Tecnologías"].map(tecnologias_map)

        # Verificar si hay valores no válidos
        if dataSet[["Educacion", "Habilidades", "Tecnologías"]].isnull().values.any():
            return "El archivo contiene categorías no válidas."

        # Realiza las predicciones con el modelo
        X = dataSet[["Experiencia", "Educacion", "Tecnologías", "Habilidades"]]
        predicciones = modelo.predict(X)

        # Añadir predicciones al DataFrame
        dataSet["Apto"] = ["Apto" if pred == 1 else "No Apto" for pred in predicciones]

        # Reordenar las columnas para asegurar que "Apto" esté al final
        columnasOrdenadas = [col for col in dataSet.columns if col != "Apto"] + ["Apto"]
        dataSet = dataSet[columnasOrdenadas]

        # Guardar el archivo actualizado en un CSV
        #output_path = "resultado_prediccion.csv"
        #dataSet.to_csv(output_path, index=False)

        # Convertir DataFrame a HTML
        tabla_html = dataSet.to_html(classes="table table-striped", index=False)

        # Renderizar resultado con HTML
        return render_template("resultado.html", tabla=tabla_html)

    except Exception as e:
        return f"Ocurrió un error al procesar el archivo: {e}"
    
# Ruta para crear un nuevo archivo CSV
@app.route("/crear", methods=["GET", "POST"])
def crear_csv():
    # Inicializar la lista de candidatos si no existe
    if "candidatos" not in session:
        session["candidatos"] = []

    if request.method == "POST":
        # Obtener datos del formulario
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        experiencia = int(request.form["experiencia"])
        educacion = request.form["educacion"]
        tecnologias = request.form["tecnologias"]
        habilidades = request.form["habilidades"]

        # Crear un nuevo candidato como un diccionario
        nuevo_candidato = {
            "Nombre": nombre,
            "Apellido": apellido,
            "Experiencia": experiencia,
            "Educacion": educacion,
            "Tecnologías": tecnologias,
            "Habilidades": habilidades,
            "Apto": ""  # La columna Apto se evaluará después
        }

        # Agregar el nuevo candidato a la lista de candidatos
        if nuevo_candidato not in session:
            session["candidatos"].append(nuevo_candidato)
            session.modified = True  # Marcar la sesión como modificada
        else:
            session.modified = False
            return redirect("/crear")

    # Renderizar la página HTML con los candidatos actuales
    return render_template("crear.html", candidatos=session["candidatos"])


@app.route("/eliminar_candidato/<int:indice>", methods=["POST"])
def eliminar_candidato(indice):
    if "candidatos" in session:
        try:
            # Eliminar el candidato en el índice especificado
            session["candidatos"].pop(indice)
            session.modified = True  # Marcar la sesión como modificada
            return redirect("/crear#tabla-container")  # Redirigir nuevamente a la página de creación
        except IndexError:
            return "Índice fuera de rango.", 400
    return "No hay candidatos en la sesión.", 400



@app.route("/guardar_csv", methods=["POST"])
def guardar_csv():
    # Obtener los datos de la sesión
    candidatos = session.get("candidatos", [])

    if not candidatos:
        return redirect("/crear")

    # Crear un DataFrame con los datos de los candidatos
    dataSet = pd.DataFrame(candidatos)

    # Reordenar las columnas en el orden deseado
    columnasOrdenadas = ["Nombre", "Apellido", "Experiencia", "Educacion", "Tecnologías", "Habilidades", "Apto"]
    dataSet = dataSet[columnasOrdenadas]

    # Guardar el archivo CSV con el orden adecuado
    output_path = "candidatosPagina.csv"
    dataSet.to_csv(output_path, index=False)

    # Limpiar la sesión después de guardar el archivo
    session.pop("candidatos", None)


    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    threading.Timer(1.5, abrir_navegador).start() 
    app.run(debug=False, host="127.0.0.1", port=5000)
