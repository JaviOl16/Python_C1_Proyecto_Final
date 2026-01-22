from flask import Blueprint

# Crear el Blueprint
admin_bp = Blueprint('admin_bp', __name__)

# Importar el archivo routes de esta carpeta
from . import routes