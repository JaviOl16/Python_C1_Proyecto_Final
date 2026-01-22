from flask import request, jsonify
from werkzeug.security import check_password_hash
from extensions import db, jwt
from models.usuario import Usuario
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# Importar el Blueprint definido en __init__.py
from . import auth_bp

"""Endpoint de Login"""

@auth_bp.route("/login", methods=["POST"])
def login():
    # Obtener los datos del usuario en formato JSON
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    # Validar que el usuario haya pasado todos los datos, si no, responder con error 400
    if not username or not password:
        return jsonify({"error": "Datos incompletos"}), 400

    # Buscar el usuario por username en la base de datos
    usuario = Usuario.query.filter_by(username=username).first()

    # Verificar que el usuario exista y que la contraseña sea correcta, si no, responder con error 401
    if not usuario or not usuario.check_password(password): #check_password compara el hash almacenado al crear usuario (en admin_bp) con la contraseña ingresada
        return jsonify({"error": "Credenciales incorrectas"}), 401

    # Si todo es correcto, generar un JWT
    access_token = create_access_token(identity=str(usuario.id_usuario))

    # Devolver el token al usuario en formato json y con mensaje 200
    return jsonify({"access_token": access_token}), 200