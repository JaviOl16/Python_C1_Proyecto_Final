from flask import Flask
from extensions import db, jwt
from auth_bp import auth_bp  # Importa el Blueprint auth_bp
from admin_bp import admin_bp  # Importa el Blueprint admin_bp
from citas_bp import citas_bp # Importa el Blueprint citas_bp

"""Crear y configurar instancia de Flask"""
def create_app():
    app = Flask(__name__)

    # Configuración de la base de datos
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///odontocare.db" # Configurar la base de datos llamada odontocare.db en SQLite
    app.config["SECRET_KEY"] = "secret"  # Clave secreta de Flask para firmar sesiones
    app.config["JWT_SECRET_KEY"] = "jwtsecretkey"  # Clave secreta de Flask para firmar tokens JWT

    # Inicializar la base de datos y JWT con la app Flask
    db.init_app(app)
    jwt.init_app(app)

    # Registrar los Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(citas_bp, url_prefix='/citas')

    # Devolver aplicación lista para usarse
    return app


