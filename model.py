import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import joblib  

# Cargar el conjunto de datos
df = pd.read_csv("candidatos.csv")

# Estandarizado de datos
encoder_educacion = LabelEncoder()
encoder_habilidades = LabelEncoder()
encoder_tecnologias = LabelEncoder()

df["Educacion"] = encoder_educacion.fit_transform(df["Educacion"])
df["Habilidades"] = encoder_habilidades.fit_transform(df["Habilidades"])
df["Tecnologías"] = encoder_tecnologias.fit_transform(df["Tecnologías"])
df["Apto"] = df["Apto"].map({"Apto": 1, "No Apto": 0})

# Separar variables independientes (X) y dependiente (y)
X = df[["Experiencia", "Educacion", "Tecnologías", "Habilidades"]]
y = df["Apto"]

# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenar el modelo de árbol de decisión
modelo = DecisionTreeClassifier()
modelo.fit(X_train, y_train)

# Evaluar el modelo
predicciones = modelo.predict(X_test)
precision = accuracy_score(y_test, predicciones)
print(f"✅ Modelo entrenado con precisión: {precision:.2f}")

# Guardar el modelo entrenado
joblib.dump(modelo, "modelo_candidatos.pkl")  # Guardar el modelo

print("✅ Modelo y encoders guardados exitosamente.")