"""Este archivo define la tabla "centros" usando SQLAlchemy.
SQLAlchemy permite trabajar con bases de datos usando clases Python en vez de usar SQL"""

# Importar la instancia de SQLAlchemy desde extensions.py: db = SQLAlchemy() 
from extensions import db

class Centro(db.Model):
    """
    Datos Centro:
    - id_centro (PK)
    - nombre
    - direccion
    """

    # Definición nombre de la tabla en la base de datos
    __tablename__ = "centros"

    """Columnas de la tabla en la base de datos"""
    
    # Identificador único del centro (primary_key=True)
    id_centro = db.Column(db.Integer, primary_key=True)

    # Nombre del centro. Con unique=True se evitar que existan centros con el mismo nombre
    nombre = db.Column(db.String(120), nullable=False, unique=True)

    # Dirección del centro
    direccion = db.Column(db.String(200), nullable=False)

    """Método para devolver los datos del centro en formato diccionario.
    Permite que en los endpoints se pueda utilizar jsonify para obtener los datos en JSON"""
    def to_dict(self):
        return {
            "id_centro": self.id_centro,
            "nombre": self.nombre,
            "direccion": self.direccion,
        }