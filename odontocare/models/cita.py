"""Este archivo define la tabla "citas" usando SQLAlchemy.
SQLAlchemy permite trabajar con bases de datos usando clases Python en vez de usar SQL"""

# Importar la instancia de SQLAlchemy desde extensions.py: db = SQLAlchemy() 
from extensions import db 

class Cita(db.Model):
    """
    Datos Cita Médica:
    - id_cita (PK)
    - fecha
    - motivo
    - estado
    - id_paciente (FK)
    - id_doctor (FK)
    - id_centro (FK)
    - id_usuario_registra (FK)
    """

    # Definición nombre de la tabla en la base de datos
    __tablename__ = "citas"

    """Columnas de la tabla en la base de datos"""
    
    # Identificador único de la cita (primary_key=True)
    id_cita = db.Column(db.Integer, primary_key=True)

    # Fecha y hora de la cita
    fecha = db.Column(db.String(25), nullable=False)

    # Motivo de la cita
    motivo = db.Column(db.String(200), nullable=False)

    # Estado de la cita
    estado = db.Column(db.String(20), nullable=False, default="Activa")

    """Relaciones con otras tablas mediante ForeignKey"""

    # Paciente al que pertenece la cita
    id_paciente = db.Column(db.Integer, db.ForeignKey("pacientes.id_paciente"), nullable=False)

    # Doctor que atiende la cita
    id_doctor = db.Column(db.Integer, db.ForeignKey("doctores.id_doctor"), nullable=False)

    # Centro médico donde se atiende la cita
    id_centro = db.Column(db.Integer, db.ForeignKey("centros.id_centro"), nullable=False)

    # Usuario que registró la cita (quién la creó en el sistema)
    id_usuario_registra = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False)


    """Método para devolver los datos de la cita en formato diccionario
    Permite que en los endpoints se pueda utilizar jsonify para obtener los datos en JSON"""
    def to_dict(self):
        return {
            "id_cita": self.id_cita,
            "fecha": self.fecha,
            "motivo": self.motivo,
            "estado": self.estado,
            "id_paciente": self.id_paciente,
            "id_doctor": self.id_doctor,
            "id_centro": self.id_centro,
            "id_usuario_registra": self.id_usuario_registra,
        }