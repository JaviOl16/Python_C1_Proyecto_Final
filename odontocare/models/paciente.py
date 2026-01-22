"""Este archivo define la tabla "pacientes" usando SQLAlchemy.
SQLAlchemy permite trabajar con bases de datos usando clases Python en vez de usar SQL"""

# Importar la instancia de SQLAlchemy desde extensions.py: db = SQLAlchemy() 
from extensions import db 

class Paciente(db.Model):
    """
    Datos Paciente:
    - id_paciente (PK)
    - id_usuario (FK opcional)
    - nombre
    - teléfono
    - estado (ACTIVO/INACTIVO)
    """

    # Definición nombre de la tabla en la base de datos
    __tablename__ = "pacientes"
    
    """Columnas de la tabla en la base de datos"""

    # Identificador único del paciente(primary_key=True)
    id_paciente = db.Column(db.Integer, primary_key=True)

    # ID de usuario:
    # Guardar el ID de usuario que pertenece al paciente
    # Es opcional porque puede que haya pacientes que no tengan usuario
    # Se utiliza ForeignKey para relacionar esta tabla con la tabla de usuarios
    # Se utiliza nullable=True para permitir que el valor sea nulo en caso de que el paciente no tenga usuario
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=True)

    # Nombre del paciente
    nombre = db.Column(db.String(120), nullable=False)

    # Teléfono del paciente
    telefono = db.Column(db.String(30), nullable=False)

    # Estado: ACTIVO o INACTIVO. Se define ACTIVO por defecto
    estado = db.Column(db.String(10), nullable=False, default="ACTIVO")

    """Método para devolver los datos del paciente en formato diccionario.
    Permite que en los endpoints se pueda utilizar jsonify para obtener los datos en JSON"""
    def to_dict(self):
        return {
            "id_paciente": self.id_paciente,
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "estado": self.estado,
        }