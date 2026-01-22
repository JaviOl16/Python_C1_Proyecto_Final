from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import citas_bp
from extensions import db
from models.usuario import Usuario
from models.paciente import Paciente
from models.doctor import Doctor
from models.centro import Centro
from models.cita import Cita


"""Endpoint agendar citas: POST /citas 
        Roles permitidos: Admin y Paciente (se interpreta del enunciado, donde figura Admin y Cliente)
        Validaciones obligatorias:
            - El doctor existe
            - El centro existe
            - El paciente existe y está ACTIVO
            - No se puede agendar si el doctor ya tiene otra cita en la misma fecha y hora
"""

@citas_bp.route("/citas", methods=["POST"])
@jwt_required() # Decorador de la librería flask_jwt_extended. Se coloca en el Endpoint para protegerlo pidiendo a los usuarios que quieran acceder un token JWT válido
def agendar_cita():
    
    # Obtener la identidad del usuario desde el JWT (para verificar si es admin o paciente en la base de datos), si no existe o no tiene ese rol, devolver error 403
    current_user_id = get_jwt_identity()
    current_user = Usuario.query.get(current_user_id)

    if not current_user or current_user.rol not in ["admin", "paciente"]:
        return jsonify({"error": "No tienes permisos para agendar citas"}), 403

    # Leer el JSON del body de la petición HTTP que hace el cliente. request.get_json() convierte ese JSON en un diccionario de Python.
    data = request.get_json()
    
    # Si la petición no viene en formato JSON (necesario para este proyecto), data = None y entonces se devuelve un error
    if not data:
        return jsonify({"error": "No se han enviado datos"}), 400

    # Extraer los campos esperados. Con estos campos se pueden deducir las validaciones obligatorias
    fecha = data.get("fecha")
    motivo = data.get("motivo")
    id_doctor = data.get("id_doctor")
    id_centro = data.get("id_centro")
    id_paciente = data.get("id_paciente")    # Para admin será obligatorio, para paciente no

    if not fecha or not motivo or id_doctor is None or id_centro is None:
        return jsonify({"error": "Faltan datos", "required": ["fecha", "motivo", "id_doctor", "id_centro"], "conditional_required": ["id_paciente (si rol = admin)"]}), 400

    # Convertir IDs a int (por si vienen como string)
    try:
        id_doctor = int(id_doctor)
        id_centro = int(id_centro)
    except ValueError:
        return jsonify({"error": "id_doctor e id_centro deben ser numericos"}), 400

    # Validación obligatoria: paciente existe:
        # - Si pide la cita el paciente: se deduce por id_usuario
        # - Si pide la cita un admin: debe venir id_paciente en el JSON de la petición
    if current_user.rol == "paciente":
        paciente = Paciente.query.filter_by(id_usuario=current_user.id_usuario).first()
        if not paciente:
            return jsonify({"error": "No existe un Paciente asociado a este usuario"}), 400
    else: # caso de admin
        if id_paciente is None:
            return jsonify({"error": "Un admin debe indicar id_paciente"}), 400
        try:
            id_paciente = int(id_paciente)
        except ValueError:
            return jsonify({"error": "id_paciente debe ser numérico"}), 400

        paciente = Paciente.query.get(id_paciente)
        if not paciente:
            return jsonify({"error": "El paciente no existe"}), 404

    # Validación obligatoria: paciente ACTIVO
    if str(paciente.estado).upper() != "ACTIVO":
        return jsonify({"error": "Paciente inactivo. No se puede agendar cita"}), 409

    # Validación obligatoria: doctor existe
    doctor = Doctor.query.get(id_doctor)
    if not doctor:
        return jsonify({"error": "El doctor no existe"}), 404

    # Validación obligatoria: centro existe
    centro = Centro.query.get(id_centro)
    if not centro:
        return jsonify({"error": "El centro medico no existe"}), 404

    # Validación obligatoria: evitar doble reserva para un doctor en misma fecha/hora
        # Si hay una cita del doctor en esa fecha/hora y NO está cancelada, hay conflicto.
    conflicto = (Cita.query
                 .filter(Cita.id_doctor == id_doctor)
                 .filter(Cita.fecha == fecha)
                 .filter(Cita.estado != "Cancelada")
                 .first())

    if conflicto:
        return jsonify({"error": "Conflicto: el doctor ya tiene una cita en esa fecha/hora"}), 409

    # Crear cita. Se usa estado Activa por defecto
    cita = Cita(fecha=fecha, motivo=motivo, estado="Activa", id_paciente=paciente.id_paciente, id_doctor=id_doctor, id_centro=id_centro, id_usuario_registra=current_user.id_usuario)

    # Guardar en base de datos
    db.session.add(cita)
    db.session.commit()

    # Devolver mensaje en JSON para confirmar cita creada
    return jsonify({"msg": "Cita creada correctamente", "Cita": cita.to_dict()}), 201

"""Endpoint listar citas: GET /citas 
        Roles permitidos: Medico, Secretaria y Admin
        Validaciones obligatorias:
            - Doctor: solo ve sus propias citas.
            - Secretaria: puede consultar citas filtrando por fecha.
            - Admin: puede filtrar por doctor, centro, fecha, estado o paciente.
            - Paciente: no puede obtener información de citas
            - Utilizar query params para aplicar los filtros.
"""
@citas_bp.route('/citas', methods=['GET'])
@jwt_required()
def listar_citas():
    
    # Obtener la identidad del usuario desde el JWT para comprobar si figura en la base de datos, si no, devolver error 404
    id_usuario = get_jwt_identity()
    usuario = Usuario.query.get(id_usuario)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Obtener el rol del usuario (admin, medico, secretaria, paciente) para poder establecer los casos
    rol = usuario.rol

    """Caso 1: Rol Medico"""
    
    if rol == "medico":
        # Buscar el doctor asociado a este usuario filtrando en la base de datos. Si no existe, devolver error 404
        doctor = Doctor.query.filter_by(id_usuario=usuario.id_usuario).first()

        if not doctor:
            return jsonify({"error": "Doctor no encontrado"}), 404

        # Regla obligatoria: El doctor SOLO puede ver sus propias citas. Filtrar en la base de datos de Citas por el id del Doctor
        citas = Cita.query.filter_by(id_doctor=doctor.id_doctor).all()


        """Caso 2: Rol Secretaria"""
        
    elif rol == "secretaria":
        # Regla obligatoria: Secretaria puede filtrar por fecha. Como en la petición se usan query params para aplicar el filtro, para obtener la fecha se utiliza la función request.args
        fecha = request.args.get("fecha")

        # Si existe fecha, devolver las citas filtradas en la base de datos
        if fecha:
            citas = Cita.query.filter_by(fecha=fecha).all()
        # Si no existe fecha en la petición, devolver todas las citas existentes (se interpreta que la secretaria puede filtrar por fecha o no filtrar)
        else:
            citas = Cita.query.all()
        

        """Caso 3: Rol Admin"""
        
    elif rol == "admin":
        # Se inicia la consulta en la base de datos de citas, pero no se listan aún las citas hasta filtrarla
        citas_query = Cita.query

        # Regla obligatoria: El admin puede aplicar diferentes filtros (doctor, centro, paciente, fecha, estado)
        
        # Se obtienen los posibles filtros de la petición. Como la petición se realiza con query params, se utiliza la función request.args
        id_doctor = request.args.get("id_doctor")
        id_centro = request.args.get("id_centro")
        id_paciente = request.args.get("id_paciente")
        fecha = request.args.get("fecha")
        estado = request.args.get("estado")

        # Si viene id_doctor, filtrar citas_query por doctor
        # Tener en cuenta que id_doctor puede venir como string al cogerlo del filtro query params. Es necesario transformarlo a int para trabajar con la base de datos. Se usa try, except para capturar posible error
        if id_doctor:
            try:
                id_doctor = int(id_doctor)
            except ValueError:
                return jsonify({"error": "id_doctor debe ser numérico"}), 400
            citas_query = citas_query.filter_by(id_doctor=id_doctor)

        # Si viene id_centro, filtrar citas_query por centro
        # Tener en cuenta que id_centro puede venir como string al cogerlo del filtro query params. Es necesario transformarlo a int para trabajar con la base de datos. Se usa try, except para capturar posible error
        if id_centro:
            try:
                id_centro = int(id_centro)
            except ValueError:
                return jsonify({"error": "id_centro debe ser numérico"}), 400
            citas_query = citas_query.filter_by(id_centro=id_centro)

        # Si viene id_paciente, filtrar citas_query por paciente
        # Tener en cuenta que id_paciente puede venir como string al cogerlo del filtro query params. Es necesario transformarlo a int para trabajar con la base de datos. Se usa try, except para capturar posible error
        if id_paciente:
            try:
                id_paciente = int(id_paciente)
            except ValueError:
                return jsonify({"error": "id_paciente debe ser numérico"}), 400
            citas_query = citas_query.filter_by(id_paciente=id_paciente)

        # Si viene fecha, filtrar citas_query por fecha
        if fecha:
            citas_query = citas_query.filter_by(fecha=fecha)

        # Si viene estado, filtrar citas_query por estado
        if estado:
            citas_query = citas_query.filter_by(estado=estado)

        # Ejecutar la consulta final con todos los filtros que se hayan aplicado
        citas = citas_query.all()


        """Caso 4: Rol Paciente o ningún Rol"""

    else:
        # Devolver error porque no está permitido consultar citas
        return jsonify({"error": "No tiene permiso para ver citas"}), 403

    # Convertir las citas a diccionario y devolver JSON
    return jsonify([cita.to_dict() for cita in citas]), 200


"""Endpoint cancelar citas: PUT /citas 
        Roles permitidos: Secretaria y Admin
        Validaciones obligatorias:
            - La cita existe.
            - La cita no está cancelada.
            - Se cambia el estado a "Cancelada" y se devuelve un mensaje JSON confirmando la acción.
"""
@citas_bp.route('/citas/<int:id_cita>', methods=['PUT'])
@jwt_required()
def cancelar_cita(id_cita):

    # Obtener la identidad del usuario desde el JWT (para verificar si es admin o secretaria en la base de datos), si no existe o no tiene ese rol devolver error 403
    id_usuario = get_jwt_identity()
    usuario = Usuario.query.get(id_usuario)

    if not usuario or usuario.rol not in ["admin", "secretaria"]:
        return jsonify({"error": "No tienes permisos para cancelar citas"}), 403

    # Buscar la cita por ID de cita filtrando en la base de datos
    cita = Cita.query.get(id_cita)

    # Validaciones obligatorias: Existencia de cita
    if not cita:
        return jsonify({"error": "Cita no encontrada"}), 404

    # Validaciones obligatorias: Estado cancelado
    if cita.estado == "Cancelada":
        return jsonify({"error": "La cita ya está cancelada"}), 400

    # Cambiar estado a "Cancelada"
    cita.estado = "Cancelada"
    
    # Guardar la edición en la base de datos
    db.session.commit()

    # Devolver mensaje en JSON para confirmar cita cancelada
    return jsonify({"msg": "Cita cancelada correctamente"}), 200
    

