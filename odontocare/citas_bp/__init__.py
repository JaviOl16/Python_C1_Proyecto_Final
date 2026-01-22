from flask import Blueprint

# Crear el Blueprint
citas_bp = Blueprint('citas_bp', __name__)

# Importar el archivo routes de esta carpeta
from . import routes