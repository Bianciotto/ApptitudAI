import joblib
import pandas as pd

# Cargar el modelo entrenado
modelo = joblib.load("modelo_candidatos.pkl")

# Cargar los datos desde el CSV
df = pd.read_csv("candidatosAPredecir.csv")

# Mapeo de valores categóricos a números
educacion_map = {"Secundario": 0, "Universitario": 1, "Postgrado": 2}
habilidades_map = {"Trabajo en equipo": 0, "Comunicación efectiva": 1, "Adaptabilidad": 2,
                   "Liderazgo": 3, "Resolución de problemas": 4, "Empatía": 5}
tecnologias_map = {"Python": 0, "Java": 1, "SQL": 2, "C++": 3}

# Aplicar los mapeos
df["Educacion"] = df["Educacion"].map(educacion_map)
df["Habilidades"] = df["Habilidades"].map(habilidades_map)
df["Tecnologías"] = df["Tecnologías"].map(tecnologias_map)

# Verificar si hay valores nulos (errores en el mapeo)
if df[["Educacion", "Habilidades", "Tecnologías"]].isnull().values.any():
    raise ValueError("Error en la conversión de datos. Revisa que todas las categorías sean correctas.")

# Seleccionar las características relevantes para predecir
X = df[["Experiencia", "Educacion", "Tecnologías", "Habilidades"]]

# Hacer las predicciones
predicciones = modelo.predict(X)

# Agregar las predicciones al DataFrame
df["Apto"] = ["Apto" if pred == 1 else "No Apto" for pred in predicciones]

# Guardar las predicciones en un nuevo CSV
df.to_csv("predicciones.csv", index=False)

print("✅ Predicciones realizadas y guardadas en 'predicciones.csv'")
