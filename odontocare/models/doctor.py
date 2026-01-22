"""Este archivo define la tabla "doctores" usando SQLAlchemy.
SQLAlchemy permite trabajar con bases de datos usando clases Python en vez de usar SQL"""

# Importar la instancia de SQLAlchemy desde extensions.py: db = SQLAlchemy() 
from extensions import db

class Doctor(db.Model):
    """
    Datos Doctor:
    - id_doctor (PK)
    - id_usuario (FK opcional)
    - nombre
    - especialidad
    """

    # Definición nombre de la tabla en la base de datos
    __tablename__ = "doctores"

    """Columnas de la tabla en la base de datos"""
    
    # Identificador único del doctor en la base de datos (primary_key=True)
    id_doctor = db.Column(db.Integer, primary_key=True)

    # ID de usuario:
    # Guardar el ID de usuario que pertenece al doctor
    # Es opcional porque puede que haya doctores que no tengan usuario
    # Se utiliza ForeignKey para relacionar esta tabla con la tabla de usuarios
    # Se utiliza nullable=True para permitir que el valor sea nulo en caso de que el paciente no tenga usuario
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=True)

    # Nombre del doctor
    nombre = db.Column(db.String(120), nullable=False)

    # Especialidad del doctor
    especialidad = db.Column(db.String(120), nullable=False)

    """Método para devolver los datos del doctor en formato diccionario.
    Permite que en los endpoints se pueda utilizar jsonify para obtener los datos en JSON"""
    def to_dict(self):
        return {
            "id_doctor": self.id_doctor,
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "especialidad": self.especialidad,
        }