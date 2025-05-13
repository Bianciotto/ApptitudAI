import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from FlaskLocal import db, Educacion, Tecnologia, Habilidad

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    db.init_app(app)
    return app

@pytest.fixture
def setup_db(app):
    with app.app_context():
        db.create_all()

        db.session.add(Educacion(nombre = 'Secundario', importancia = 1))
        db.session.add(Tecnologia(nombre = 'Java', importancia = 1))
        db.session.add(Habilidad(nombre = 'Liderazgo', importancia = 1))

        db.session.commit()
        yield db

        db.session.remove()
        db.drop_all()

def test_cambiar_peso_etiqueta_educacion(app, setup_db, importancia = 3):
    with app.app_context():
        edu = Educacion.query.filter_by(nombre = "Secundario").first()
        edu.importancia = importancia
        db.session.commit()
        edu_actualizada = Educacion.query.filter_by(nombre = "Secundario").first()
        assert edu_actualizada.importancia == 3


def test_cambiar_peso_etiqueta_tecnologia(app, setup_db, importancia = 3):
    with app.app_context():
        tec = Tecnologia.query.filter_by(nombre = "Java").first()
        tec.importancia = importancia
        db.session.commit()
        tec_actualizada = Tecnologia.query.filter_by(nombre = "Java").first()
        assert tec_actualizada.importancia == 3


def test_cambiar_peso_etiqueta_habilidad(app, setup_db, importancia = 3):
    with app.app_context():
        hab = Habilidad.query.filter_by(nombre = "Liderazgo").first()
        hab.importancia = importancia
        db.session.commit()
        hab_actualizada = Habilidad.query.filter_by(nombre = "Liderazgo").first()
        assert hab_actualizada.importancia == 3