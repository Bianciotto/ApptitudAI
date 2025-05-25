import pytest
from flask_sqlalchemy import SQLAlchemy
from app import app as appLocal, OfertaLaboral,OfertaEducacion,OfertaHabilidad,OfertaTecnologia, db

@pytest.fixture
def client():
    appLocal.config['TESTING'] = True
    appLocal.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/erp_rrhh.db'
    
    with appLocal.app_context():
        with appLocal.test_client() as cliente:
            yield cliente

#Test que verifica que se cree la oferta y que impacte en la base de datos
def test_crear_oferta_exitosa(client):
    with appLocal.app_context():        
        with client.session_transaction() as sess:
            sess["username"] = "Fernando"
            sess["type"] = "Admin_RRHH"

        response = client.post('/crear_oferta', data={
            'nombre': 'Desarrollador Frontend SR',
            'fecha_cierre': '2025-06-01',
            'max_candidatos': '20',
            'remuneracion': '100000',
            'beneficio': 'Home Office',
            'estado': 'Activa',
            'usuario_responsable': 'Fernando' 
        })

        assert response.status_code in [200,302]

        oferta_laboral = OfertaLaboral.query.filter_by(nombre= 'Desarrollador Frontend SR').first()
        assert oferta_laboral is not None

        OfertaEducacion.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        OfertaTecnologia.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        OfertaHabilidad.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        
        db.session.delete(oferta_laboral)
        db.session.commit()

#Test que verifica la asignacion exitosa de las etiquetas a la oferta laboral
def test_asignacion_de_etiquetas_exitosa(client):
    with appLocal.app_context():
        with client.session_transaction() as sess:
            sess["username"] = "Fernando"
            sess["type"] = "Admin_RRHH"
        
        response = client.post('/crear_oferta', data={
            'nombre': 'Desarrollador Backend SR',
            'fecha_cierre': '2025-06-01',
            'max_candidatos': '20',
            'remuneracion': '100000',
            'beneficio': 'Home Office',
            'estado': 'Activa',
            'usuario_responsable': 'Fernando' 
        })

        assert response.status_code in [200,302]

        oferta_laboral = OfertaLaboral.query.filter_by(nombre = 'Desarrollador Backend SR').first();

        id_oferta = oferta_laboral.idOfer

        assert OfertaEducacion.query.filter_by(idOfer=id_oferta).count() > 0
        assert OfertaTecnologia.query.filter_by(idOfer=id_oferta).count() > 0
        assert OfertaHabilidad.query.filter_by(idOfer=id_oferta).count() > 0

        OfertaEducacion.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        OfertaTecnologia.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        OfertaHabilidad.query.filter_by(idOfer=oferta_laboral.idOfer).delete()

        db.session.delete(oferta_laboral)
        db.session.commit()

def test_oferta_duplicada(client):
    with appLocal.app_context():        
        with client.session_transaction() as sess:
            sess["username"] = "Fernando"
            sess["type"] = "Admin_RRHH"

        response1 = client.post('/crear_oferta', data={
            'nombre': 'Desarrollador Java JR',
            'fecha_cierre': '2025-06-01',
            'max_candidatos': '20',
            'remuneracion': '100000',
            'beneficio': 'Home Office',
            'estado': 'Activa',
            'usuario_responsable': 'Fernando'  
        })

        assert response1.status_code in [200,302]

        response2 = client.post('/crear_oferta', data={
            'nombre': 'Desarrollador Java SR',
            'fecha_cierre': '2025-06-01',
            'max_candidatos': '20',
            'remuneracion': '100000',
            'beneficio': 'Home Office',
            'estado': 'Activa',
            'usuario_responsable': 'Fernando' 
        })

        assert response2.status_code in [400,409,500]

        oferta_laboral = OfertaLaboral.query.filter_by(nombre= 'Desarrollador Java JR').first()

        OfertaEducacion.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        OfertaTecnologia.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        OfertaHabilidad.query.filter_by(idOfer=oferta_laboral.idOfer).delete()
        
        db.session.delete(oferta_laboral)
        db.session.commit()


#test que verifica que no se cree la oferta con campos vacios ❌Fallando❌
def test_campos_vacios(client):
    with appLocal.app_context():
        with client.session_transaction() as sess:
            sess["username"] = "Fernando"
            sess["type"] = "Admin_RRHH"
        
        response = client.post('/crear_oferta', data={
            'nombre': '',
            'fecha_cierre': '',
            'max_candidatos': '',
            'remuneracion': '',
            'beneficio': '',
            'estado': '',
            'usuario_responsable': '' 
        })

        assert response.status_code in [400,422]

# def test_validacion_de_permisos(client):
#     with appLocal.app_context():
#         with client.session_transaction() as sess:
#             sess["username"] = "Diego"
#             sess["type"] = "Supervisor"

#         response = client.post('/crear_oferta', data = {
#             'nombre': 'Desarrollador Python SR',
#             'fecha_cierre': '2025-06-01',
#             'max_candidatos': '20',
#             'remuneracion': '100000',
#             'beneficio': 'Home Office',
#             'estado': 'Activa',
#             'usuario_responsable': 'Diego'
#         })

#         assert response.status_code == 200
#         assert b"Acceso no autorizado" in response.data