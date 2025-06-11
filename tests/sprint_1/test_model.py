import pytest
import joblib
import pandas as pd
from datetime import datetime
from app import app as appLocal, db, OfertaLaboral, Candidato, Educacion, Tecnologia, Tecnologia2,Habilidad, Habilidad2,OfertaEducacion,OfertaHabilidad,OfertaHabilidad2,OfertaTecnologia,OfertaTecnologia2

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
    modelo = loadModel()

    columnas = ["Educacion", "Tecnologías", "Tecnologías2", "Habilidades", "Habilidades2"]
    datos_prueba = pd.DataFrame([[0, 0, 0, 0, 0]], columns=columnas)

    try:
        prediccion = modelo.predict(datos_prueba)
    except Exception as e:
        pytest.fail(f"El modelo falló al realizar la predicción: {e}")

    assert prediccion[0] == 1

#Test que verifica que un candidato es no apto
def test_model_prediction_no_apto():
    modelo = loadModel()

    columnas = ["Educacion", "Tecnologías", "Tecnologías2", "Habilidades", "Habilidades2"]
    datos_prueba = pd.DataFrame([[2, 3, 1, 1, 2]], columns=columnas)

    try:
        prediccion = modelo.predict(datos_prueba)
    except Exception as e:
        pytest.fail(f"El modelo falló al realizar la predicción: {e}")

    assert prediccion[0] == 0

#Test que verifica que se aplique el modelo al cerrar una oferta
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

        edu = Educacion.query.filter_by(nombre="postgrado").first()
        tec1 = Tecnologia.query.filter_by(nombre="aws").first()
        tec2 = Tecnologia2.query.filter_by(nombre ="azure").first()
        hab1 = Habilidad.query.filter_by(nombre="adaptabilidad").first()
        hab2 = Habilidad2.query.filter_by(nombre="autodidacta").first()

        oferta_edu = OfertaEducacion(idOfer=oferta.idOfer, idEdu=edu.idedu, importancia=3)
        oferta_tec = OfertaTecnologia(idOfer=oferta.idOfer, idTec=tec1.idtec, importancia=3)
        oferta_tec2 = OfertaTecnologia2(idOfer=oferta.idOfer, idTec2=tec2.idtec2, importancia=3)
        oferta_hab = OfertaHabilidad(idOfer=oferta.idOfer, idHab=hab1.idhab, importancia=3)
        oferta_hab2 = OfertaHabilidad2(idOfer=oferta.idOfer, idHab2=hab2.idhab2, importancia=3)

        db.session.add_all([oferta_edu, oferta_tec, oferta_tec2, oferta_hab, oferta_hab2])
        db.session.commit()

        c_apto = Candidato(
            id=f"apto_test@gmail.com{oferta.idOfer}",
            nombre="Apto",
            apellido="ApellidoTest",
            mail="apto_test@gmail.com",
            telefono="1111111111",
            ubicacion="Buenos Aires",
            experiencia=10,
            idedu=edu.idedu,
            idtec=tec1.idtec,
            idtec2=tec2.idtec2,
            idhab=hab1.idhab,
            idhab2=hab2.idhab2,
            idOfer=oferta.idOfer
        )

        c_noapto = Candidato(
            id=f"noapto_test@gmail.com{oferta.idOfer}",
            nombre="NoApto",
            apellido="Apellidonoapto",
            mail="noapto_test@gmail.com",
            telefono="1122222222",
            ubicacion="Cordoba",
            experiencia=2,
            idedu=2,
            idtec=3,
            idtec2=1,
            idhab=1,
            idhab2=2,
            idOfer=oferta.idOfer
        )

        db.session.add_all([c_apto, c_noapto])
        db.session.commit()
        oferta_id = oferta.idOfer 

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