import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from FlaskLocal import db, Educacion, Habilidad, Tecnologia, Candidato, calcular_puntaje, asignar_puntajes

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

        edu = Educacion(nombre="Universitario", importancia = 3)
        edu2 = Educacion(nombre = "Secundario", importancia = 1)
        tec = Tecnologia(nombre="Java", importancia = 2)
        tec2 = Tecnologia(nombre = "SQL", importancia = 1)
        hab = Habilidad(nombre="Liderazgo", importancia=2)
        hab2 = Habilidad(nombre = "Adaptabilidad", importancia = 3)

        db.session.add_all([edu, tec, hab, edu2, hab2, tec2])
        db.session.commit()

        candidato = Candidato(
        id="JosePerez@gmail.com",
        nombre="Jose",
        apellido="Abalos",
        mail="JosePerez@gmail.com",
        telefono="1122334455",
        ubicacion="Buenos Aires",
        experiencia=5,
        idedu=edu.idedu,
        idtec=tec.idtec,
        idhab=hab.idhab,
        aptitud=True,
        puntaje=0
        )

        db.session.add(candidato)
        db.session.commit()

        app.test_ids = {
            "Universitario": edu.idedu,
            "Secundario": edu2.idedu,
            "Java": tec.idtec,
            "SQL": tec2.idtec,
            "Liderazgo": hab.idhab,
            "Adaptabilidad": hab2.idhab,
        }

        yield db

        db.session.remove()
        db.drop_all()

# Testea que el puntaje asignado a un candidato sea correcto según sus datos
def test_agregar_puntaje(app, setup_db):
    with app.app_context():
        asignar_puntajes()  # ahora esto calcula y guarda el puntaje automáticamente

        postulante = Candidato.query.filter_by(id="JosePerez@gmail.com").first()
        assert postulante is not None
        assert postulante.puntaje == 33

# Verifica que el cálculo de puntaje funcione correctamente para varios candidatos parametrizados
@pytest.mark.parametrize(
    "nombre, apellido, email, telefono, ubicacion, experiencia, educacion, tecnologias, habilidades",
    [
        ('Lucas', 'Abalos', 'correoDePueba123@gmail.com', '1135356456', 'Buenos Aires', 3, "Universitario", "Java", "Adaptabilidad"),
        ('Hernesto', 'Gonzalez', 'correoDePueba4123@gmail.com', '1343567856', 'Buenos Aires', 6, "Secundario", "SQL", "Liderazgo"),
    ]
)
def test_calcular_puntaje_params(app, setup_db,nombre, apellido, email, telefono, ubicacion, experiencia, educacion, tecnologias, habilidades):
    with app.app_context():
        
        postulante = Candidato(
        id=email,
        nombre=nombre,
        apellido=apellido,
        mail=email,
        telefono=telefono,
        ubicacion=ubicacion,
        experiencia=experiencia,
        idedu = app.test_ids[educacion],
        idtec = app.test_ids[tecnologias],
        idhab = app.test_ids[habilidades],
        aptitud=True,
        puntaje=0)

        db.session.add(postulante)
        db.session.commit()

        edu = db.session.get(Educacion, postulante.idedu)
        tec = db.session.get(Tecnologia, postulante.idtec)
        hab = db.session.get(Habilidad, postulante.idhab)

        puntaje_esperado = postulante.experiencia * 2  +  edu.importancia * 3 + tec.importancia * 5 + hab.importancia * 2

        puntaje_calculado = calcular_puntaje(postulante)

        assert puntaje_esperado == puntaje_calculado

# Verifica que el ranking creado esté ordenado correctamente por puntaje descendente
def test_ranking(app, setup_db):
    with app.app_context():
        ids = app.test_ids

        candidato1 = Candidato(
            id="lucas@mail.com",
            nombre="Lucas",
            apellido="Abalos",
            mail="lucas@mail.com",
            telefono="1111111111",
            ubicacion="Buenos Aires",
            experiencia=3,
            idedu=ids["Universitario"],
            idtec=ids["Java"],
            idhab=ids["Adaptabilidad"],
            aptitud=True,
            puntaje=0
        )

        candidato2 = Candidato(
            id="hernesto@mail.com",
            nombre="Hernesto",
            apellido="Gonzalez",
            mail="hernesto@mail.com",
            telefono="2222222222",
            ubicacion="Buenos Aires",
            experiencia=6,
            idedu=ids["Secundario"],
            idtec=ids["SQL"],
            idhab=ids["Liderazgo"],
            aptitud=True,
            puntaje=0
        )
        
        db.session.add_all([candidato1, candidato2])
        db.session.commit()
        
        candidatos = Candidato.query.all()

        for c in candidatos:
            c.puntaje = calcular_puntaje(c)
            db.session.add(c)
        db.session.commit()

        candidatos_ordenados = Candidato.query.order_by(Candidato.puntaje.desc()).all()
        puntajes = [c.puntaje for c in candidatos_ordenados]

        assert puntajes == sorted(puntajes, reverse=True)

# Verifica que dos candidatos con los mismos datos tengan el mismo puntaje y aparezcan empatados en el ranking
def test_ranking_con_empate(app, setup_db):
    with app.app_context():
        ids = app.test_ids
        
        Candidato.query.delete()
        db.session.commit()

        c1 = Candidato(
            id="empate1@mail.com",
            nombre="Ana",
            apellido="Lopez",
            mail="empate1@mail.com",
            telefono="1111111111",
            ubicacion="Buenos Aires",
            experiencia=4,
            idedu=ids["Universitario"],
            idtec=ids["SQL"],
            idhab=ids["Liderazgo"],
            aptitud=True,
            puntaje=0
        )
        c2 = Candidato(
            id="empate2@mail.com",
            nombre="Bruno",
            apellido="Martinez",
            mail="empate2@mail.com",
            telefono="2222222222",
            ubicacion="CABA",
            experiencia=4,
            idedu=ids["Universitario"],
            idtec=ids["SQL"],
            idhab=ids["Liderazgo"],
            aptitud=True,
            puntaje=0
        )

        db.session.add_all([c1, c2])
        db.session.commit()

        asignar_puntajes()

        ordenados = Candidato.query.order_by(Candidato.puntaje.desc()).all()
        puntajes = [c.puntaje for c in ordenados]

        assert puntajes == sorted(puntajes, reverse=True)
        assert puntajes.count(puntajes[0]) >= 2 

def test_calcular_puntaje_a_no_apto(app, setup_db):
     with app.app_context():
        ids = app.test_ids
        
        Candidato.query.delete()
        db.session.commit()

        postulante = Candidato(
            id="anaLopez@gmail.com",
            nombre="Ana",
            apellido="Lopez",
            mail="anaLopez@gmail.com",
            telefono="1111111111",
            ubicacion="Buenos Aires",
            experiencia=4,
            idedu=ids["Universitario"],
            idtec=ids["SQL"],
            idhab=ids["Liderazgo"],
            aptitud=False,
            puntaje=0
        )

        db.session.add(postulante)
        db.session.commit()

        asignar_puntajes()

        postulante_actualizado = db.session.get(Candidato,postulante.id)
        puntaje_esperado = 0
        puntaje_calculado = postulante_actualizado.puntaje
        

        assert puntaje_esperado == puntaje_calculado        