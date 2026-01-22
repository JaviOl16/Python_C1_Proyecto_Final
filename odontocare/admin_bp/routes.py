from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db
from models.centro import Centro
from models.usuario import Usuario
from models.doctor import Doctor
from models.paciente import Paciente

# Importar el Blueprint definido en __init__.py
from . import admin_bp

"""Endpoint para crear Usuarios: : POST /admin/usuario (solo para rol Admin)"""
@admin_bp.route("/usuario", methods=["POST"])
@jwt_required()  # Decorador de la librería flask_jwt_extended. Se coloca en el Endpoint para protegerlo pidiendo a los usuarios que quieran acceder un token JWT válido
def register_user():
    
    # Obtener la identidad del usuario desde el JWT (para verificar si es admin), si no, devolver error 403
    current_user_id = get_jwt_identity() # Esta función de la librería flask_jwt_extended permite obtener el ID de usuario desde el token JWT
    current_user = Usuario.query.get(current_user_id) # Buscar filtrando en la base de datos mediante función query

    if not current_user or current_user.rol != "admin":
        return jsonify({"error": "No tienes permisos para registrar usuarios"}), 403

    # Leer el JSON del body de la petición HTTP que hace el cliente para crear un usuario. Si falta alguno de ellos, devolver error 400
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    rol = request.json.get("rol", None)

    if not username or not password or not rol:
        return jsonify({"error": "Faltan datos"}), 400
    
    # Verificar que el rol creado es de "admin" o "secretaria"
    if rol not in ["admin", "secretaria"]:
        return jsonify({"error": "rol invalido","roles_validos": ["admin", "secretaria"]}), 400

    # Verificar si el usuario ya existe y devolver error 409 en ese caso
    existing_user = Usuario.query.filter_by(username=username).first() # Buscar usuario filtrando por nombre en la base de datos
    if existing_user:
        return jsonify({"error": "El nombre de usuario ya esta en uso"}), 409

    # Crear el nuevo usuario
    # La función set_password cifra la contraseña (hash). Se utiliza para no guardar la contraseña directamente en la base de datos (seguridad)
    new_user = Usuario(username=username, rol=rol)
    new_user.set_password(password)

    # Guardar el nuevo usuario en la base de datos
    db.session.add(new_user)
    db.session.commit()

    # Devolver mensaje para confirmar registro OK
    return jsonify({"msg": "Usuario registrado exitosamente"}), 201


"""Endpoint para crear Centro Médico: POST /admin/centros (solo para rol Admin)"""

@admin_bp.route("/centros", methods=["POST"])
@jwt_required()     # Obliga a estar autenticado con token. Se usa el decorador de la librería flask_jwt_extended y solicita a los usuarios que quieran acceder un token JWT válido
def crear_centro():
    
    # Obtener datos de usuario autenticado y buscar en la base de datos
    current_user_id = get_jwt_identity()
    current_user = Usuario.query.get(current_user_id)

    # Verificar que el usuario exista y que sea admin, si no, devolver error 403
    if not current_user or current_user.rol != "admin":
        return jsonify({"error": "No tienes permisos para crear centros medicos"}), 403
    
    # Leer el JSON del body de la petición HTTP que hace el cliente. request.get_json() convierte ese JSON en un diccionario de Python.
    data = request.get_json()

    # Si la petición no viene en formato JSON (necesario para este proyecto), data = None y entonces se devuelve un error
    if not data:
        return jsonify({"error": "No se han enviado datos"}), 400

    # Extraer los campos esperados de la petición
    nombre = data.get("nombre")
    direccion = data.get("direccion")

    # Validación: ambos campos son obligatorios
    if not nombre or not direccion:
        return jsonify({"error": "Faltan campos obligatorios", "required": ["nombre", "direccion"]}), 400

    # Verificar si el centro ya existe y devolver error 409 en ese caso
    existe = Centro.query.filter_by(nombre=nombre).first() # Buscar centro filtrando por nombre en la base de datos
    if existe:
        return jsonify({"error": "Ya existe un centro con ese nombre", "centro_existente": existe.to_dict()}), 409

    # Crear el centro y guardar en la base de datos
    centro = Centro(nombre=nombre, direccion=direccion)
    db.session.add(centro)
    db.session.commit()

    # Devolver mensaje en JSON para confirmar el centro creado
    return jsonify({"msg": "Centro creado correctamente", "centro": centro.to_dict()}), 201

"""Endpoint para crear Doctor: POST /admin/doctores (solo para rol Admin)"""

@admin_bp.route("/doctores", methods=["POST"])
@jwt_required()     # Obliga a estar autenticado con token. Se usa el decorador de la librería flask_jwt_extended y solicita a los usuarios que quieran acceder un token JWT válido
def crear_doctor():

    # Obtener datos de usuario autenticado y buscar en la base de datos
    current_user_id = get_jwt_identity()
    current_user = Usuario.query.get(current_user_id)

    # Verificar que el usuario exista y que sea admin, si no, devolver error 403
    if not current_user or current_user.rol != "admin":
        return jsonify({"error": "No tienes permisos para crear doctores"}), 403

    # Leer el JSON del body de la petición HTTP que hace el cliente. request.get_json() convierte ese JSON en un diccionario de Python.
    data = request.get_json()
    
    # Si la petición no viene en formato JSON (necesario para este proyecto), data = None y entonces se devuelve un error
    if not data:
        return jsonify({"error": "No se han enviado datos"}), 400

    # Extraer los campos esperados. Se debe definir el nombre y la especialidad, pero también se debe crear un usuario asociado con nombre y contraseña.
    nombre = data.get("nombre")
    especialidad = data.get("especialidad")
    username = data.get("username")
    password = data.get("password")

    # Validación: todos los campos son obligatorios
    if not nombre or not especialidad or not username or not password:
        return jsonify({"error": "Faltan datos", "required": ["nombre", "especialidad", "username", "password"]}), 400

    # Verificar si el usuario ya existe y devolver error 409 en ese caso
    existe = Usuario.query.filter_by(username=username).first() # Buscar usuario filtrando por nombre en la base de datos
    if existe:
        return jsonify({"error": "El nombre de usuario ya esta en uso"}), 409

    # Crear el usuario del doctor forzando el rol a "medico"
    user_medico = Usuario(username=username, rol="medico")
    user_medico.set_password(password)
    
    # Guardar usuario en la base de datos para obtener de antemano el ID de usuario
    db.session.add(user_medico)
    db.session.commit()

    # Crear el doctor asociado al usuario recién creado
    doctor = Doctor(nombre=nombre, especialidad=especialidad, id_usuario=user_medico.id_usuario)
    # Guardar todo en la base de datos
    db.session.add(doctor)
    db.session.commit()

    # Devolver mensaje en JSON para confirmar el doctor creado
    return jsonify({"msg": "Doctor creado correctamente", "doctor": doctor.to_dict(), "usuario": user_medico.to_dict()}), 201

"""Endpoint para crear Pacientes: POST /admin/pacientes (solo para rol Admin)"""

@admin_bp.route("/pacientes", methods=["POST"])
@jwt_required()
def crear_paciente():

    # Obtener datos de usuario autenticado y buscar en la base de datos
    current_user_id = get_jwt_identity()
    current_user = Usuario.query.get(current_user_id)

    # Verificar que el usuario exista y que sea admin, si no, devolver error 403
    if not current_user or current_user.rol != "admin":
        return jsonify({"error": "No tienes permisos para crear pacientes"}), 403

    # Leer el JSON del body de la petición HTTP que hace el cliente. request.get_json() convierte ese JSON en un diccionario de Python.
    data = request.get_json()
    
    # Si la petición no viene en formato JSON (necesario para este proyecto), data = None y entonces se devuelve un error
    if not data:
        return jsonify({"error": "No se han enviado datos"}), 400

    # Extraer los campos esperados. Se debe definir el nombre, el teléfono, el estado (no obligatorio porque el modelo lo pone Activo por defecto), pero también se debe crear un usuario asociado con nombre y contraseña.
    nombre = data.get("nombre")
    telefono = data.get("telefono")
    estado = data.get("estado")
    username = data.get("username")
    password = data.get("password")

    # Validar datos obligatorios
    if not nombre or not telefono or not username or not password:
        return jsonify({"error": "Faltan datos", "required": ["nombre", "telefono", "username", "password"], "optional": ["estado"]}), 400

    # Validar estado (ACTIVO o INACTIVO). Pasar a mayúsculas para evitar problemas.
    estado = str(estado).upper()
    if estado and estado not in ["ACTIVO", "INACTIVO"]:
        return jsonify({"error": "Estado invalido", "estados_validos": ["ACTIVO", "INACTIVO"]}), 400

    # Verificar si el usuario ya existe y devolver error 409 en ese caso
    existe = Usuario.query.filter_by(username=username).first()
    if existe:
        return jsonify({"error": "El nombre de usuario ya esta en uso"}), 409

    # Crear el usuario del paciente forzando el rol a "paciente"
    user_paciente = Usuario(username=username, rol="paciente")
    user_paciente.set_password(password)

    # Guardar usuario en la base de datos para obtener de antemano el ID de usuario
    db.session.add(user_paciente)
    db.session.commit() 

    # Crear el paciente asociado al usuario recién creado
    paciente = Paciente(nombre=nombre, telefono=telefono, estado=estado, id_usuario=user_paciente.id_usuario)

    # Guardar todo en la base de datos
    db.session.add(paciente)
    db.session.commit()

    # Devolver mensaje en JSON para confirmar el paciente creado
    return jsonify({"msg": "Paciente creado correctamente", "paciente": paciente.to_dict(), "usuario": user_paciente.to_dict()}), 201