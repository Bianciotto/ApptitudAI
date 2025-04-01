import joblib
import pandas as pd

# Cargar el modelo entrenado y los encoders
modelo = joblib.load("modelo_candidatos.pkl")
encoder_educacion = joblib.load("encoder_educacion.pkl")
encoder_habilidades = joblib.load("encoder_habilidades.pkl")
encoder_tecnologias = joblib.load("encoder_tecnologias.pkl")

# Cargar los datos desde el CSV
df = pd.read_csv("candidatosAPredecir.csv")

# Transformar los datos utilizando los encoders guardados
df["Educacion"] = encoder_educacion.transform(df["Educacion"])
df["Habilidades"] = encoder_habilidades.transform(df["Habilidades"])
df["Tecnologías"] = encoder_tecnologias.transform(df["Tecnologías"])

# Verificar si hay valores nulos (errores en la transformación)
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
