"""Archivo __init__ para definir carpeta como paquete de Python y 
para definir qué clases se tienen que importar al usar models

De esta forma se asegura que SQLAlchemy cree las tablas de los modelos que se han creado """

from .usuario import Usuario
from .paciente import Paciente
from .doctor import Doctor
from .centro import Centro
from .cita import Cita