"""Normaliza la fabrica Flask de la copia y recupera el refactor parcial conocido.

Se ejecuta por RUTA DE ARCHIVO para conservar comillas en Windows PowerShell 5.1.
No modifica el ZIP original ni servicios externos.
"""
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime
import shutil
import ast

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT.parent / 'fuentes' / 'api.zip'
EVIDENCIAS = ROOT.parent / 'evidencias'

REGLAS = {
    'app/__init__.py': [('def crear_app():', 'def create_app():')],
    'app.py': [
        ('from app import crear_app', 'from app import create_app'),
        ('app = crear_app()', 'app = create_app()'),
        ('app.run(debug=True, port=5000)',
         'app.run(host="127.0.0.1", port=5000, debug=False)'),
    ],
    'tests/conftest.py': [
        ('from app import crear_app', 'from app import create_app'),
        ('app = crear_app()', 'app = create_app()'),
    ],
    'scripts/promover_admin.py': [
        ('from app import crear_app', 'from app import create_app'),
        ('app = crear_app()', 'app = create_app()'),
    ],
    'README.md': [('Factory: crear_app()', 'Factory: create_app()')],
}
ALIAS = '\n\n# Alias temporal para consumidores externos antiguos.\ncrear_app = create_app\n'

if not ORIGINAL.is_file():
    raise RuntimeError('Falta la fuente original: ' + str(ORIGINAL))

pendientes = {}
with ZipFile(ORIGINAL) as fuente:
    for nombre, reglas in REGLAS.items():
        # La fuente se utiliza solo para construir y verificar el cambio esperado.
        base = fuente.read(nombre).decode('utf-8-sig').replace('\r\n', '\n')
        objetivo = base
        for viejo, nuevo in reglas:
            if objetivo.count(viejo) != 1:
                raise RuntimeError(f'La fuente no tiene el contrato esperado: {nombre}')
            objetivo = objetivo.replace(viejo, nuevo, 1)
        if nombre == 'app/__init__.py':
            objetivo += ALIAS

        ruta = ROOT / nombre
        actual = ruta.read_text(encoding='utf-8-sig').replace('\r\n', '\n')
        aceptados = {base, objetivo}
        if nombre == 'app.py':
            # Estado parcial concreto producido por Python -c en PowerShell 5.1.
            aceptados.add(objetivo.replace('host="127.0.0.1"', 'host=127.0.0.1'))
        if actual not in aceptados:
            raise RuntimeError(
                f'{nombre}: hay cambios no reconocidos; detenerse y revisarlos, '
                'sin sobrescribir trabajo ajeno.'
            )
        if nombre.endswith('.py'):
            ast.parse(objetivo, filename=nombre)
        if actual != objetivo:
            pendientes[ruta] = objetivo

# Validar TODO antes de realizar la primera escritura.
if pendientes:
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    sello = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    resguardo = EVIDENCIAS / ('fabrica_previa_' + sello)
    for ruta in pendientes:
        destino = resguardo / ruta.relative_to(ROOT)
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ruta, destino)
    try:
        for ruta, objetivo in pendientes.items():
            ruta.write_text(objetivo, encoding='utf-8', newline='\n')
        for ruta in pendientes:
            if ruta.suffix == '.py':
                ast.parse(ruta.read_text(encoding='utf-8'), filename=str(ruta))
    except Exception:
        for ruta in pendientes:
            copia = resguardo / ruta.relative_to(ROOT)
            shutil.copy2(copia, ruta)
        raise
    print('RESGUARDO_REFRACTOR', resguardo)

print('ARCHIVOS_MODIFICADOS', len(pendientes))
print('FABRICA_PRODUCTO_CORREGIDA_OK')
