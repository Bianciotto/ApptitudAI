import pytest
import joblib
import pandas as pd
from datetime import datetime
from app import app as appLocal, db, OfertaLaboral, Candidato, Educacion, Tecnologia, Habilidad

@pytest.fixture
def client():
    appLocal.config['TESTING'] = True
    appLocal.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/erp_rrhh.db'
    with appLocal.test_client() as cliente:
        yield cliente

def loadModel():
    modelo_path = "modelo_candidatos.pkl"

    try:
        modelo = joblib.load(modelo_path)
        return modelo
    except FileNotFoundError:
        pytest.fail(f"No se encontro el arhivo del modelo")

#Test que verifica que un candidato es apto
def test_model_prediction_apto():
    # Se carga el modelo
    modelo = loadModel()

    # Se crean los datos de prueba
    columnas = ["Experiencia", "Educacion", "Tecnologías", "Habilidades"] 
    datos_prueba = pd.DataFrame([[10, 2, 3, 1]], columns=columnas)

    # Se realiza la predicción
    try:
        prediccion = modelo.predict(datos_prueba)
    except Exception as e:
        pytest.fail(f"El modelo falló al realizar la predicción: {e}")

    assert prediccion[0] == 1

#Test que verifica que un candidato es no apto
def test_model_prediction_no_apto():
    # Se carga el modelo
    modelo = loadModel()

    # Se crean los datos de prueba
    columnas = ["Experiencia", "Educacion", "Tecnologías", "Habilidades"]  # Asegúrate de que coincidan con las esperadas
    datos_prueba = pd.DataFrame([[1, 0, 0, 0]], columns=columnas)

    # Se realiza la predicción
    try:
        prediccion = modelo.predict(datos_prueba)
    except Exception as e:
        pytest.fail(f"El modelo falló al realizar la predicción: {e}")

    assert prediccion[0] == 0

def test_model_aplicado_al_cerrar_oferta(client):
    with client.session_transaction() as sess:
        sess["username"] = "Fernando"
        sess["type"] = "Admin_RRHH"

    with client.application.app_context():
        oferta = OfertaLaboral(
            nombre="Oferta Test",
            fecha_cierre=datetime(2030, 1, 1),
            max_candidatos=10,
            remuneracion="1000",
            beneficio="Home Office",
            estado="Activa",
            usuario_responsable="Fernando"
        )
        db.session.add(oferta)
        db.session.flush()

        edu = Educacion.query.filter_by(nombre="Postgrado").first()
        tec = Tecnologia.query.filter_by(nombre="Java").first()
        hab = Habilidad.query.filter_by(nombre="Liderazgo").first()

        c_apto = Candidato(
            id=f"apto_test@gmail.com{oferta.idOfer}",
            nombre="Apto",
            apellido="ApellidoTest",
            mail="apto_test@gmail.com",
            telefono="1111111111",
            ubicacion="Buenos Aires",
            experiencia=10,
            idedu=edu.idedu,
            idtec=tec.idtec,
            idhab=hab.idhab,
            idOfer=oferta.idOfer
        )

        c_noapto = Candidato(
            id=f"noapto_test@gmail.com{oferta.idOfer}",
            nombre="NoApto",
            apellido="Apellidonoapto",
            mail="noapto_test@gmail.com",
            telefono="1122222222",
            ubicacion="Cordoba",
            experiencia=0,
            idedu=0,
            idtec=0,
            idhab=0,
            idOfer=oferta.idOfer
        )

        db.session.add_all([c_apto, c_noapto])
        db.session.commit()
        oferta_id = oferta.idOfer  # Guardar el ID para usarlo fuera del contexto


    response = client.post(f"/cerrar_oferta/{oferta_id}")
    assert response.status_code == 302

    with client.application.app_context():
        c1 = Candidato.query.get(f"apto_test@gmail.com{oferta_id}")
        c2 = Candidato.query.get(f"noapto_test@gmail.com{oferta_id}")

        assert c1.aptitud is True
        assert c2.aptitud is False

        Candidato.query.filter(Candidato.id.in_([ f"apto_test@gmail.com{oferta_id}", f"noapto_test@gmail.com{oferta_id}"])).delete()
        OfertaLaboral.query.filter_by(idOfer=oferta_id).delete()
        db.session.commit()