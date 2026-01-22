from flask import Blueprint

# Crear el Blueprint
auth_bp = Blueprint("auth_bp", __name__)

# Importar el archivo routes de esta carpeta
from . import routes