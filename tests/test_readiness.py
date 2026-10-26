from unittest.mock import patch
from app import db


def test_ready_con_base_disponible(client):
    response = client.get('/ready')
    assert response.status_code == 200
    assert response.get_json() == {
        'status': 'ready', 'database': 'available'
    }


def test_ready_con_base_no_disponible(client):
    # Se simula la excepción en la operación DB; no se detiene MySQL real.
    with patch.object(db.session, 'execute', side_effect=RuntimeError('corte simulado')):
        response = client.get('/ready')
    assert response.status_code == 503
    assert response.get_json() == {
        'status': 'not_ready', 'database': 'unavailable'
    }
