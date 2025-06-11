from typing import Literal
from flask.testing import FlaskClient
import pytest
from app import app as app_candidatos,Candidato,OfertaLaboral,db

# Fixture para eliminar candidatos específicos antes de ejecutar los tests
@pytest.fixture(scope="function", autouse=True)
def eliminar_candidatos():
    ids_a_eliminar = [
        'correoDePueba123@gmail.com',
        'correoDePueba4123@gmail.com',
        'tincho462@gmail.com',
        'agusmartinez@hotmail.com'
    ]
    with app_candidatos.app_context():
        for id_candidato in ids_a_eliminar:
            candidato = Candidato.query.filter_by(id=id_candidato).first()
            if candidato:
                db.session.delete(candidato)
        db.session.commit()

@pytest.fixture
def client_Candidatos():
    app_candidatos.config['TESTING'] = True  # Activa el modo TESTING de Flask
    app_candidatos.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/erp_rrhh.db'  # Configura la base de datos para usar SQLite local
    with app_candidatos.test_client() as client_Candidatos:  # Crea un cliente de prueba de Flask
        yield client_Candidatos  # Devuelve el cliente para que sea usado dentro de los tests

#🟡A revisar🟡
# Test parametrizado que verifica intentos de agregar postulantes validos
# Envía una solicitud POST con datos válidos y espera una respuesta 200 o 302
# Luego verifica que el postulante fue correctamente guardado en la base de datos
@pytest.mark.parametrize(
    "nombre, apellido, email, telefono, ubicacion, experiencia, educacion, tecnologia1,tecnologia2, habilidad1, habilidad2",
    [
        ('Lucas', 'Abalos', 'correoDePueba123@gmail.com', '1135356456', 'Buenos Aires', '2', 'secundario', 'python','html' ,'trabajo en equipo','adaptabilidad'),
        ('Jose', 'Perez', 'correoDePueba4123@gmail.com', '1343567856', 'Buenos Aires', '2', 'secundario', 'python','html' ,'trabajo en equipo','adaptabilidad'),
    ]
)
def test_valid_agregar_postulacion(client_Candidatos: FlaskClient,nombre,apellido,email,telefono,ubicacion,experiencia,educacion,tecnologia1,tecnologia2,habilidad1,habilidad2):    
    client_Candidatos.get('/postulacionIT')
    
    oferta_id = OfertaLaboral.query.filter_by(estado = 'Activa').first().idOfer

    response = client_Candidatos.post('/postulacion', data={
        'nombre': nombre,
        'apellido': apellido,
        'email': email,
        'telefono': telefono,
        'ubicacion': ubicacion,
        'experiencia': experiencia,
        'educacion': educacion,
        'tecnologias': tecnologia1,      
        'tecnologias2': tecnologia2,     
        'habilidades': habilidad1,       
        'habilidades2': habilidad2,      
        'idOfer': str(oferta_id),
        'puntaje': 0
    })
    assert response.status_code in [200, 302]

    # Verificar que el postulante fue ingresado en la base de datos
    with app_candidatos.app_context():
        candidato = Candidato.query.filter_by(id=email + str(oferta_id)).first()
        assert candidato is not None
        #Se puede explayar mas

#🟡A revisar🟡
# Test parametrizado que verifica el intento de agregar postulantes duplicados
# Envía una solicitud POST con datos válidos dos veces seguidas
# Espera que la primera solicitud se procese correctamente (200 o 302)
# La segunda debería fallar con un código de error (500) por ser duplicado
# Luego verifica que el postulante no fue duplicado en la base de datos
@pytest.mark.parametrize(
    "nombre, apellido, email, telefono, ubicacion, experiencia, educacion, tecnologia1,tecnologia2, habilidad1, habilidad2",
     [
         ('Martin', 'Gonzales', 'tincho462@gmail.com','1125432354', 'Buenos Aires', '6','universitario', 'java','css', 'trabajo en equipo','autodidacta'),
         ('Agustin', 'Martinez', 'agusmartinez@hotmail.com','1123432345', 'Formosa', '3' ,'postgrado', 'sql','css', 'liderazgo','autodidacta')
     ]
)
def test_postulantes_duplicados(client_Candidatos: FlaskClient,nombre,apellido,email,telefono,ubicacion,experiencia,educacion,tecnologia1,tecnologia2,habilidad1,habilidad2):
    client_Candidatos.get('/postulacionIT')

    oferta_id = OfertaLaboral.query.filter_by(estado = 'Activa').first().idOfer

    data = {
        'nombre': nombre,
        'apellido': apellido,
        'email': email,
        'telefono': telefono,
        'ubicacion': ubicacion,
        'experiencia': experiencia,
        'educacion': educacion,
        'tecnologias': tecnologia1,      
        'tecnologias2': tecnologia2,     
        'habilidades': habilidad1,       
        'habilidades2': habilidad2,      
        'idOfer': str(oferta_id),
        'puntaje': 0
    }

    response1 = client_Candidatos.post('/postulacion', data=data)
    assert response1.status_code in [200,302]

    response2 = client_Candidatos.post('/postulacion', data=data)
    assert response2.status_code == 500

    with client_Candidatos.application.app_context():
       candidatos = Candidato.query.filter_by(id=email + str(oferta_id)).all()
       assert len(candidatos) == 1

#Test que verifica que no se pueda agregar un candidato a una oferta cerrada ❌Fallando❌
# def test_cargar_candidatos_con_oferta_cerrada(client_Candidatos):
#     client_Candidatos.get('/postulacionIT')
    
#     id_oferta_cerrada = OfertaLaboral.query.filter_by(estado = 'Cerrada').first()
    
#     response = client_Candidatos.post('/postulacion', data = {
#         'nombre': 'Carlos',
#         'apellido': 'Rodriguez',
#         'email': 'Carlitos@gmail.com', 
#         'telefono': '1134123423',
#         'ubicacion': 'Buenos Aires',
#         'experiencia': 5, 
#         'educacion': 'Universitario',  
#         'tecnologias': 'Java',        
#         'habilidades': 'Liderazgo',
#         'idOfer': str(id_oferta_cerrada.idOfer),
#         'puntaje': 0
#     })

#     assert response.status_code in [400,409, 500]
#     candidato = Candidato.query.filter_by(id='Carlitos@gmail.com' + str(id_oferta_cerrada.idOfer)).first()
#     assert candidato is None