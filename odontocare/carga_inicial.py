import pandas as pd
import requests
import os
from extensions import db
from models.usuario import Usuario
from app import create_app

"""Definición URL de la API"""

BASE_URL = "http://127.0.0.1:5000"


"""Función para hacer login como admin
    Esta función se encarga de:
     - Enviar el username y password al endpoint /auth/login
     - Recibir un token JWT si las credenciales son correctas
"""

def login_admin(username, password):
    
    # Construir la URL completa para hacer login
    url = f"{BASE_URL}/auth/login"

    # Construir diccionario con datos que se envían en la petición (username y password del admin)
    data = {"username": username, "password": password}

    # Hacer la petición POST (enviar datos al servidor) usando la librería requests. Los parámetro son la url del servidor y el diccionario de datos en formato json
    response = requests.post(url, json=data)

    # Si la respuesta fue exitosa (200), se obtiene el token y se devuelve para usarlo más adelante
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        # Si algo falla, se muestra error
        return print("Error al hacer login:", response.json())


"""Función principal del Script
    Esta función se encarga de:
     - Leer el archivo CSV con los datos iniciales (centros, doctores, pacientes).
     - Buscar dentro del CSV un usuario con tipo "admin".
     - Hacer login con ese admin para obtener un token JWT.
     - Usar ese token para enviar al servidor cada registro del CSV
     - Crear una cita
     - Imprimir en consola el resultado de la cita creada
"""
def main():
   
   # Crear app y contexto
        # create_app(): crea la aplicación Flask con DB, JWT y Blueprints
        # app.app_context().push(): activa el contexto de Flask para poder usar db y Usuario fuera de una petición HTTP
    app = create_app()
    app.app_context().push()
    
    # Leer el CSV usando pandas
        # Función pd.read_csv() lee el archivo CSV y lo guarda como un DataFrame. Se usa sep=";" porque el CSV usa ; como separador
        # Con os, obtener la ruta completa del directorio y construir la ruta hasta datos.csv para poder leerlo
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "..", "data", "datos.csv")

    df = pd.read_csv(csv_path, sep=";")


    # Buscar en el CSV el usuario admin
        # En el CSV se añade la columna tipo para facilitar la búsqueda del tipo de usuario del aplicativo (admin, paciente, doctor...)
        # Filtrar solo las filas donde el tipo sea "admin"
    admin_rows = df[df["tipo"] == "admin"]

    # Si no existe ninguna fila admin, se sale de la función enviando mensaje de error
    if admin_rows.empty:
        print("No se encontró usuario admin en el CSV")
        return

    # Coger la primera fila de admin (si hubiera varias)
    admin_user = admin_rows.iloc[0]

    # Hacer login con ese admin y la función definida anteriormente
    token = login_admin(admin_user["username"], admin_user["password"])

    # Si falla el login, creamos el admin directamente en la base de datos (para cuando la base de datos está vacía)
    if not token:
        print("El admin no existe en la base de datos. Intentando crearlo...")

        # Asegurar que el admin no esté creado ya en la base de datos
        existing = Usuario.query.filter_by(username=admin_user["username"]).first()

        if not existing:

            new_admin = Usuario(username=admin_user["username"], rol="admin")
            new_admin.set_password(admin_user["password"])

            db.session.add(new_admin)
            db.session.commit()

        print("Admin creado en BD. Reintentando login...")
        token = login_admin(admin_user["username"], admin_user["password"])

    # Si sigue sin token, y por tanto falla el login, salir
    if not token:
        print("No se pudo iniciar sesión. Revisa el usuario o contraseña del admin")
        return

    # Headers para usar el token en todas las peticiones
        # Como la API está protegida con JWT, todas las peticiones a endpoints deben incluir un token válido.
        # Este header, que incluye el token, se enviará en todas las peticiones posteriores para que el servidor sepa quién está haciendo la solicitud.
        # La construcción del header es un estándar de python
    headers = {"Authorization": f"Bearer {token}"}

    # Enviar registros del CSV uno a uno al servidor
    created_doctors = []
    created_patients = []
    created_centers = []
        # Se itera cada fila del DataFrame
    for _, row in df.iterrows():
        tipo = row["tipo"]

        # Caso Centro
        
        if tipo == "centro":
            # Diccionario con parámetros del centro
            data = {"nombre": row["nombre"], "direccion": row["direccion"]} 
            # Hacer petición POST a admin/centros para crear el centro. Los datos se envían en JSON y se envía el headers con el token para permitir la acción. 
            response = requests.post(f"{BASE_URL}/admin/centros", json=data, headers=headers)
            
            # Verificar si la petición fue exitosa
                # Si el código de la respuesta es exitoso, añadir centro creado y su ID a la lista e imprimir confirmación
            if response.status_code in [200, 201]:
                created_centers.append(response.json()["centro"]["id_centro"])
                print("Centro creado:", row["nombre"])
                # Si el código de la respuesta no es exitoso, devolver mensaje de error
            else:
                print("Error al crear centro:", response.json())

        # Caso Doctor
        
        elif tipo == "doctor":
            # Diccionario con parámetros del doctor
            data = {"nombre": row["nombre"], "especialidad": row["especialidad"], "username": row["username"], "password": row["password"]}
            # Hacer petición POST a admin/doctores para crear el centro. Los datos se envían en JSON y se envía el headers con el token para permitir la acción.             
            response = requests.post(f"{BASE_URL}/admin/doctores", json=data, headers=headers)
            
            # Verificar si la petición fue exitosa
                # Si el código de la respuesta es exitoso, añadir doctor creado y su ID a la lista e imprimir confirmación
            if response.status_code in [200, 201]:
                created_doctors.append(response.json()["doctor"]["id_doctor"])
                print("Doctor creado:", row["nombre"])
                # Si el código de la respuesta no es exitoso, devolver mensaje de error
            else:
                print("Error al crear doctor:", response.json())

        # Caso Paciente
        
        elif tipo == "paciente":
            # Diccionario con parámetros del paciente. Si el estado no está definido (se comprueba con función notna), se define por defecto Activo
            data = {"nombre": row["nombre"], "telefono": row["telefono"], "username": row["username"], "password": row["password"], "estado": row["estado"] if pd.notna(row["estado"]) else "ACTIVO"}
             # Hacer petición POST a admin/pacientes para crear el centro. Los datos se envían en JSON y se envía el headers con el token para permitir la acción.                        
            response = requests.post(f"{BASE_URL}/admin/pacientes", json=data, headers=headers)

            # Verificar si la petición fue exitosa
                # Si el código de la respuesta es exitoso, añadir paciente creado y su ID a la lista e imprimir confirmación
            if response.status_code in [200, 201]:
                created_patients.append(response.json()["paciente"]["id_paciente"])
                print("Paciente creado:", row["nombre"])
                # Si el código de la respuesta no es exitoso, devolver mensaje de error
            else:
                print("Error al crear paciente:", response.json())
                
        # Caso Admin
            # No hacer nada, se usa para el login
        elif tipo == "admin":
            continue

        # Si el tipo no es conocido, devolver error y seguir con el bucle
        else:
            print("Tipo no reconocido:", tipo)
            continue

    # Crear una cita
        # Asegurar que las listas de doctores, pacientes y centros contienen datos
    if not created_doctors or not created_patients or not created_centers:
        print("No se pudo crear la cita porque faltan datos.")
        return
        
        # Rellenar la información de la cita con la primera fila de cada lista (cita de ejemplo)
    cita_data = {"fecha": "2025-09-10 10:00", "motivo": "Revisión dental", "id_doctor": created_doctors[0], "id_centro": created_centers[0], "id_paciente": created_patients[0]}
        
        # Hacer petición POST a admin/pacientes para crear la cita. Los datos se envían en JSON y se envía el headers con el token para permitir la acción.                        
    response = requests.post(f"{BASE_URL}/citas/citas", json=cita_data, headers=headers)

    # Imprimir el JSON de la cita creada
        # Si la respuesta del servidor es exitosa, devolver mensaje json con la cita creada
    if response.status_code == 201:
        print("Cita creada:")
        print(response.json())
        # Si no ha sido exitoso, devolver error
    else:
        print("Error al crear cita:", response.status_code, response.json())


# Ejecutar script
if __name__ == "__main__":
    main()
