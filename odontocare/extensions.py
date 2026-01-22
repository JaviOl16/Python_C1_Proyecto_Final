from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Inicializar las extensiones, pero sin asociarlas a la app
db = SQLAlchemy()
jwt = JWTManager()