from app import create_app
from extensions import db
import models

"""Creación de la API y la base de datos"""
app = create_app()
    
if __name__ == "__main__":
    
    import models # Se importan las clases definidas en models para que SQLAlchemy cree las tablas a partir de ellas
    with app.app_context():
        print("Creando tablas...")
        db.create_all()  # Crear las tablas
        print("Tablas creadas")
    app.run(debug=True)