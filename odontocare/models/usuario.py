"""Este archivo define la tabla "usuarios" usando SQLAlchemy.
SQLAlchemy permite trabajar con bases de datos usando clases Python en vez de usar SQL"""

# Importar funciones de Werkzeug para manejar contraseñas de manera segura
# Importar la instancia de SQLAlchemy desde extensions.py: db = SQLAlchemy() 
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

# Definir la clase Usuario, que será la tabla "usuarios" en la base de datos
class Usuario(db.Model):
    """
    Datos Usuario:
    - id_usuario (PK)
    - username
    - password
    - rol (admin, medico, secretaria, paciente)
    """
    # Nombre de la tabla en la base de datos
    __tablename__ = "usuarios"

    """Columnas de la tabla en la base de datos"""
    
    # ID único de cada usuario (primary_key=True)
    id_usuario = db.Column(db.Integer, primary_key=True)
    
    # Nombre de usuario único (unique=True)
    username = db.Column(db.String(80), unique=True, nullable=False) 
     
    # Contraseña hasheada
    password = db.Column(db.String(255), nullable=False)  
    
    # Rol del usuario
    rol = db.Column(db.String(20), nullable=False)  

    """Método para generar el hash de la contraseña antes de guardarla"""
    def set_password(self, password):
        self.password = generate_password_hash(password)  # Convertir la contraseña en un hash seguro

    """Método para comprobar si la contraseña ingresada coincide con el hash guardado"""
    def check_password(self, password):
        return check_password_hash(self.password, password)  # Devolver True si la contraseña es correcta
    
    """Método para devolver los datos del usuario en formato diccionario. La contraseña no se incluye
    Permite que en los endpoints se pueda utilizar jsonify para obtener los datos en JSON"""
    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "username": self.username,
            "rol": self.rol
        }