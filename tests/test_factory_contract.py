from app import create_app, crear_app

def test_fabrica_estandarizada_y_alias():
    assert callable(create_app)
    assert crear_app is create_app
