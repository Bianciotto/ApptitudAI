import pytest
from FlaskLocal import app, db, Educacion, Tecnologia, Habilidad

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/erp_rrhh.db'
    with app.test_client() as cliente:
        with app.app_context():
            yield cliente

#Test que prueba que las etiquetas se actualizen con los datos permitidos
@pytest.mark.parametrize(
        "importancia",
        [
            (0),
            (1),
            (2),
            (3)
        ]
)
def test_actualizacion_importancia(client, importancia):
    with app.app_context():
        edu = db.session.execute(db.select(Educacion).filter_by(nombre="Secundario")).scalar_one()
        id_edu = edu.idedu
        valor_edu_original = edu.importancia

        tec = db.session.execute(db.select(Tecnologia).filter_by(nombre ="Java")).scalar_one()
        id_tec = tec.idtec
        valor_tec_original = tec.importancia

        hab = db.session.execute(db.select(Habilidad).filter_by(nombre ="Liderazgo")).scalar_one()
        id_hab = hab.idhab
        valor_hab_original = hab.importancia

    respuesta = client.post("/asignar_valores", data={
        "educacion_id": id_edu,
        "valor_educacion": importancia,
        "tecnologia_id": id_tec,
        "valor_tecnologia": importancia,
        "habilidad_id": id_hab,
        "valor_habilidad": importancia
    }, follow_redirects=True)

    assert respuesta.status_code == 200

    with app.app_context():
        edu_actualizada = db.session.get(Educacion, id_edu)
        assert edu_actualizada.importancia == importancia
        edu_actualizada.importancia = valor_edu_original

        tec_actualizada = db.session.get(Tecnologia, id_tec)
        assert tec_actualizada.importancia == importancia
        tec_actualizada.importancia = valor_tec_original

        hab_actualizada = db.session.get(Habilidad, id_hab)
        assert hab_actualizada.importancia == importancia
        hab_actualizada.importancia = valor_hab_original
        
        db.session.commit()

#Test que prueba que no se actualizen las etiquetas con datos no validos (❌Fallando❌)
@pytest.mark.parametrize(
        "importancia",
        [
            (-1),
            (4)
        ]
)
def test_actualizar_etiquetas_fuera_de_rango(client, importancia):
    with app.app_context():
        edu = db.session.execute(db.select(Educacion).filter_by(nombre="Secundario")).scalar_one()
        id_edu = edu.idedu
        
        tec = db.session.execute(db.select(Tecnologia).filter_by(nombre ="Java")).scalar_one()
        id_tec = tec.idtec
       
        hab = db.session.execute(db.select(Habilidad).filter_by(nombre ="Liderazgo")).scalar_one()
        id_hab = hab.idhab
       
    respuesta = client.post("/asignar_valores", data={
    "educacion_id": id_edu,
    "valor_educacion": importancia,
    "tecnologia_id": id_tec,
    "valor_tecnologia": importancia,
    "habilidad_id": id_hab,
    "valor_habilidad": importancia
    }, follow_redirects=True)

    assert respuesta.status_code == 400

