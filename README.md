# OdontoCare — Proyecto Final Python C1

## Descripción General

**OdontoCare** es una aplicación backend desarrollada como proyecto final del curso **Python C1**, cuyo objetivo es integrar y aplicar los conocimientos adquiridos en el diseño e implementación de una **API RESTful profesional**, segura y modular.

El sistema permite gestionar de manera eficiente las operaciones de una red de clínicas dentales, incluyendo la administración de pacientes, doctores, centros médicos y citas, reemplazando procesos manuales propensos a errores.

---

## Objetivos del Proyecto

- Diseñar una API RESTful organizada y mantenible.
- Implementar operaciones **CRUD** para:
  - Pacientes
  - Doctores
  - Centros médicos
  - Citas médicas
- Garantizar la persistencia de datos mediante una base de datos.
- Incorporar autenticación segura basada en **tokens (JWT)**.
- Asegurar que todas las respuestas se entreguen en formato **JSON**.
- Aplicar buenas prácticas de desarrollo backend.
- Implementar una arquitectura distribuida usando **Docker**.
- Demostrar la interacción cliente-servidor mediante un script externo en Python.

---

## Arquitectura de la Solución

El proyecto está desarrollado utilizando **Flask** como framework backend, organizado mediante **Blueprints** para garantizar modularidad, escalabilidad y claridad en el código.

### Estructura General del Proyecto

```bash
odonto-care/
│
├── auth/                # Autenticación y usuarios
├── admin/               # Gestión administrativa
├── citas/               # Gestión de citas médicas
├── models/              # Modelos SQLAlchemy
├── database/            # Configuración de la base de datos
├── client/              # Cliente externo (requests)
├── docker/              # Configuración Docker
├── app.py               # Inicialización de la aplicación
├── requirements.txt     # Dependencias del proyecto
└── README.md

