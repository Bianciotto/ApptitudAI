from flask import Flask, redirect, render_template, request, send_file, session
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

try:
    encoder_educacion_path = get_path("encoder_educacion.pkl")
    encoder_habilidades_path = get_path("encoder_habilidades.pkl")
    encoder_tecnologias_path = get_path("encoder_tecnologias.pkl")
    
except FileNotFoundError as e:
    print("Error: No se pudo cargar el archivo del encoder.", e)
    raise e
except Exception as e:
    print("Error al cargar los encoders:", e)
    raise e

# Página principal
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/", methods=["GET", "POST"])
def entrenar_inicio():
    if request.method == "POST":
        if "archivo_entrenamiento" not in request.files:
            return "Por favor, sube un archivo CSV."

        archivo = request.files["archivo_entrenamiento"]
        if archivo.filename == "":
            return "No seleccionaste ningún archivo."

        try:
            dataSet = pd.read_csv(archivo)
            dataSet2 = dataSet.copy()

            # Inicializar encoders
            encoder_educacion = LabelEncoder()
            encoder_habilidades = LabelEncoder()
            encoder_tecnologias = LabelEncoder()

            # Entrenamiento
            dataSet["Educacion"] = encoder_educacion.fit_transform(dataSet["Educacion"])
            dataSet["Habilidades"] = encoder_habilidades.fit_transform(dataSet["Habilidades"])
            dataSet["Tecnologías"] = encoder_tecnologias.fit_transform(dataSet["Tecnologías"])
            dataSet["Apto"] = dataSet["Apto"].map({"Apto": 1, "No Apto": 0})

            X = dataSet[["Experiencia", "Educacion", "Tecnologías", "Habilidades"]]
            y = dataSet["Apto"]

            modelo = DecisionTreeClassifier(max_depth=5)
            modelo.fit(X, y)

            # Guardar modelo y encoders
            joblib.dump(modelo, get_path("modelo_candidatos.pkl"))
            joblib.dump(encoder_educacion, get_path("encoder_educacion.pkl"))
            joblib.dump(encoder_habilidades, get_path("encoder_habilidades.pkl"))
            joblib.dump(encoder_tecnologias, get_path("encoder_tecnologias.pkl"))

            # Guardar dataset
            dataSet2.to_csv(get_path("entrenamientoActualizado.csv"), index=False)

            # Guardar en sesión para estadísticas
            session["clases_educacion"] = list(encoder_educacion.classes_)
            session["clases_habilidades"] = list(encoder_habilidades.classes_)
            session["clases_tecnologias"] = list(encoder_tecnologias.classes_)

            session["modelo_entrenado"] = True

            # Redirigir a la página de estadísticas
            return redirect("/estadisticas")

        except Exception as e:
            return f"❌ Ocurrió un error durante el entrenamiento: {e}"

    return render_template("index.html")


# Página de estadísticas
@app.route("/estadisticas", methods=["GET", "POST"])
def estadisticas():
    if request.method == "POST":
        return render_template("predecir.html")
    # Cargar modelo y encoders
    modelo = joblib.load(get_path("modelo_candidatos.pkl"))
    encoder_educacion = joblib.load(get_path("encoder_educacion.pkl"))
    encoder_habilidades = joblib.load(get_path("encoder_habilidades.pkl"))
    encoder_tecnologias = joblib.load(get_path("encoder_tecnologias.pkl"))

    # Leer el dataset de entrenamiento
    dataSet = pd.read_csv(get_path("entrenamientoActualizado.csv"))

    dataSet["Educacion"] = encoder_educacion.fit_transform(dataSet["Educacion"])
    dataSet["Habilidades"] = encoder_habilidades.fit_transform(dataSet["Habilidades"])
    dataSet["Tecnologías"] = encoder_tecnologias.fit_transform(dataSet["Tecnologías"])

    # Ya está codificado, así que sólo aseguramos que Apto esté como entero
    if dataSet["Apto"].dtype == object:
        dataSet["Apto"] = dataSet["Apto"].map({"Apto": 1, "No Apto": 0})

    X = dataSet[["Experiencia", "Educacion", "Tecnologías", "Habilidades"]]
    y = dataSet["Apto"]
    precision = round(modelo.score(X, y), 4)

    # Clases de encoders
    clases = {
        "Educacion": list(encoder_educacion.classes_),
        "Habilidades": list(encoder_habilidades.classes_),
        "Tecnologías": list(encoder_tecnologias.classes_),
    }

    # Graficar árbol y convertir a imagen en base64
    fig, ax = plt.subplots(figsize=(14, 8))
    plot_tree(modelo, feature_names=["Experiencia", "Educacion", "Tecnologías", "Habilidades"], 
              class_names=["No Apto", "Apto"], filled=True, rounded=True, fontsize=10, ax=ax)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent = True)
    plt.close(fig)
    buf.seek(0)
    imagen_base64 = base64.b64encode(buf.read()).decode("utf-8")

    return render_template(
    "estadisticas.html",
    clases_educacion=clases["Educacion"],
    clases_habilidades=clases["Habilidades"],
    clases_tecnologias=clases["Tecnologías"],
    precision=precision,
    imagen_arbol=imagen_base64
)


# Ruta para predecir con un archivo CSV
@app.route("/predecir", methods=["GET", "POST"])
def predecir():
    if request.method == "POST":

        # Verifica que el archivo esté en la solicitud
        if "archivo_csv" not in request.files:
            return "Por favor, sube un archivo CSV."

        file = request.files["archivo_csv"]
        if file.filename == "":
            return "No seleccionaste ningún archivo."

        try:
            # Leer el archivo CSV
            dataSet = pd.read_csv(file)
            encoder_educacion_path = get_path("encoder_educacion.pkl")
            encoder_habilidades_path = get_path("encoder_habilidades.pkl")
            encoder_tecnologias_path = get_path("encoder_tecnologias.pkl")
        
            encoder_educacion = joblib.load(encoder_educacion_path)
            session["opciones_educacion"] = list(encoder_educacion.classes_)
            encoder_habilidades = joblib.load(encoder_habilidades_path)
            session["opciones_habilidades"] = list(encoder_habilidades.classes_)
            encoder_tecnologias = joblib.load(encoder_tecnologias_path)
            session["opciones_tecnologias"] = list(encoder_tecnologias.classes_)
            modelo = joblib.load(modelo_path)

            # Verifica que las columnas necesarias existan en el archivo
            columnas_requeridas = ["Experiencia", "Educacion", "Tecnologías", "Habilidades"]
            for columna in columnas_requeridas:
                if columna not in dataSet.columns:
                    return f"El archivo no contiene la columna requerida: {columna}"

            dataSet2 = dataSet.copy()

            # Transformar las columnas categóricas utilizando los encoders cargados
            try:
                dataSet["Educacion"] = encoder_educacion.transform(dataSet["Educacion"])
                dataSet["Habilidades"] = encoder_habilidades.transform(dataSet["Habilidades"])
                dataSet["Tecnologías"] = encoder_tecnologias.transform(dataSet["Tecnologías"])
            except ValueError as e:
                return f"Error en las transformaciones: {e}. Asegúrate de que todas las categorías estén reconocidas por los encoders."

            # Verificar si hay valores no válidos después de las transformaciones
            if dataSet[["Educacion", "Habilidades", "Tecnologías"]].isnull().values.any():
                return "El archivo contiene categorías que no se pudieron transformar correctamente."

            # Realizar las predicciones con el modelo
            X = dataSet[["Experiencia", "Educacion", "Tecnologías", "Habilidades"]]
            predicciones = modelo.predict(X)

            # Añadir predicciones al DataFrame
            dataSet2["Apto"] = ["Apto" if pred == 1 else "No Apto" for pred in predicciones]

            # Reordenar las columnas para asegurar que "Apto" esté al final
            columnasOrdenadas = [col for col in dataSet2.columns if col != "Apto"] + ["Apto"]
            dataSet2 = dataSet2[columnasOrdenadas]

            # Convertir DataFrame a HTML
            tabla_html = dataSet2.to_html(classes="table table-striped", index=False)

            # Renderizar resultado con HTML
            return render_template("resultado.html", tabla=tabla_html)

        except Exception as e:
            return f"Ocurrió un error al procesar el archivo: {e}"
    
    return render_template("predecir.html")

    
# Ruta para crear un nuevo archivo CSV
@app.route("/actualizar_modelo", methods=["GET", "POST"])
def actualizar_modelo():
    if request.method == "POST":    
        if "nuevo_csv" not in request.files:
            return "Por favor, sube un archivo CSV para actualizar el modelo."

        file = request.files["nuevo_csv"]
        if file.filename == "":
            return "No seleccionaste ningún archivo."

        try:
            # Cargar modelo y encoders existentes
            print("Cargando modelo y encoders existentes...")
            modelo_path = get_path("modelo_candidatos.pkl")
            modelo = joblib.load(modelo_path)
            encoder_educacion_path = get_path("encoder_educacion.pkl")
            encoder_habilidades_path = get_path("encoder_habilidades.pkl")
            encoder_tecnologias_path = get_path("encoder_tecnologias.pkl")
            encoder_educacion = joblib.load(encoder_educacion_path)
            encoder_habilidades = joblib.load(encoder_habilidades_path)
            encoder_tecnologias = joblib.load(encoder_tecnologias_path)
            
            # Cargar datasets
            print("Cargando datasets...")
            entrenamientoActualizado_path = get_path("entrenamientoActualizado.csv")
            dataSet = pd.read_csv(entrenamientoActualizado_path)
            #nuevo_df = pd.read_csv(file_path)
            nuevo_df = pd.read_csv(file)

            # Combinar datasets
            print("Uniendo datasets...")
            unirDataSet = pd.concat([dataSet, nuevo_df], ignore_index=True)
            unirDataSet.drop_duplicates()
            unirDataSetNoMapeado = unirDataSet.copy()

            # Actualizar encoders dinámicamente
            print("Actualizando encoders dinámicamente...")
            nuevas_educaciones = set(unirDataSet["Educacion"]) - set(encoder_educacion.classes_)
            if nuevas_educaciones:
                encoder_educacion.classes_ = np.array(list(encoder_educacion.classes_) + list(nuevas_educaciones))
            nuevas_habilidades = set(unirDataSet["Habilidades"]) - set(encoder_habilidades.classes_)
            if nuevas_habilidades:
                encoder_habilidades.classes_ = np.array(list(encoder_habilidades.classes_) + list(nuevas_habilidades))
            nuevas_tecnologias = set(unirDataSet["Tecnologías"]) - set(encoder_tecnologias.classes_)
            if nuevas_tecnologias:
                encoder_tecnologias.classes_ = np.array(list(encoder_tecnologias.classes_) + list(nuevas_tecnologias))

            # Transformar columnas categóricas
            print("Transformando columnas categóricas...")
            unirDataSet["Educacion"] = encoder_educacion.transform(unirDataSet["Educacion"])
            unirDataSet["Habilidades"] = encoder_habilidades.transform(unirDataSet["Habilidades"])
            unirDataSet["Tecnologías"] = encoder_tecnologias.transform(unirDataSet["Tecnologías"])
            unirDataSet["Apto"] = unirDataSet["Apto"].map({"Apto": 1, "No Apto": 0})

            # Reentrenar el modelo
            print("Reentrenando el modelo...")
            X = unirDataSet[["Experiencia", "Educacion", "Tecnologías", "Habilidades"]]
            y = unirDataSet["Apto"]
            modelo.fit(X, y)

            # Guardar resultados actualizados
            print("Guardando datos actualizados...")
            unirDataSetNoMapeado.to_csv(entrenamientoActualizado_path, index=False)
            modelo_path = get_path("modelo_candidatos.pkl")
            encoder_educacion_path = get_path("encoder_educacion.pkl")
            encoder_habilidades_path = get_path("encoder_habilidades.pkl")
            encoder_tecnologias_path = get_path("encoder_tecnologias.pkl")
            joblib.dump(modelo, modelo_path)
            joblib.dump(encoder_educacion, encoder_educacion_path)
            joblib.dump(encoder_habilidades, encoder_habilidades_path)
            joblib.dump(encoder_tecnologias, encoder_tecnologias_path)

            # Redirigir a la página de estadísticas
            return redirect("/estadisticas")

        except Exception as e:
            print("Error:", e)
            return f"Ocurrió un error al procesar y actualizar el modelo: {e}"

    return render_template("actualizar_modelo.html")


@app.route("/crear", methods=["GET", "POST"])
def crear_csv():
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
        if nuevo_candidato not in session["candidatos"]:
            session["candidatos"].append(nuevo_candidato)
            session.modified = True  # Marcar la sesión como modificada
        else:
            session.modified = False
            return redirect("/crear")

    # Renderizar la página HTML con los candidatos actuales
    return render_template(
        "crear.html",
        candidatos=session["candidatos"],
        opciones_educacion=session["opciones_educacion"],
        opciones_habilidades=session["opciones_habilidades"],
        opciones_tecnologias=session["opciones_tecnologias"]
    )


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
    return redirect("/crear#tabla-container")


@app.route("/guardar_csv", methods=["POST"])
def guardar_csv():
    # Obtener los datos de la sesión
    candidatos = session.get("candidatos", [])

    if not candidatos:
        return redirect("/crear#tabla-container")

    # Crear un DataFrame con los datos de los candidatos
    dataSet = pd.DataFrame(candidatos)

    # Reordenar las columnas en el orden deseado
    columnasOrdenadas = ["Nombre", "Apellido", "Experiencia", "Educacion", "Tecnologías", "Habilidades", "Apto"]
    dataSet = dataSet[columnasOrdenadas]

    # Guardar el archivo CSV con el orden adecuado
    candidatosPagina_path = get_path("candidatosPagina.csv")
    dataSet.to_csv(candidatosPagina_path, index=False)

    # Limpiar la sesión después de guardar el archivo
    session.pop("candidatos", None)

    return send_file(candidatosPagina_path, as_attachment=True)

if __name__ == "__main__":
    threading.Timer(1.5, abrir_navegador).start() 
    app.run(debug=False, host="127.0.0.1", port=5000)
