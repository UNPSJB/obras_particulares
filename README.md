OBRAS PARTICULARES
==================

Instalación y Uso
---

**Nota de uso:** Debemos tener instalado Git en el sistema.

##### Paso 1: Clonar el repositorio a nuestro sistema
    git clone https://github.com/UNPSJB/obras_particulares.git
    cd obras_particulares

##### Paso 2: Crear ambiente virtual
    pip install virtualenv
    python -m virtualenv myvirtualenv
    Linux: source myvirtualenv/bin/activate
    Windows: myvirtualenv/Scripts/activate.bat


##### Paso 3: Instalar lista de dependencias
    pip install -r requirements.txt
    
##### Paso 4: Realizar migraciones de aplicaciones
    python manage.py makemigrations
    
##### Paso 5: Correr el código
    python manage.py runserver
    
##### Paso 6: Acceso al sistema
    Ir a http://localhost:8000

Catedra e Integrantes
-----
Trabajo practico para la catedra Desarrollo de Software de la UNPSJB sede Trelew.

###### Integrantes de la Cátedra
- Lic. Gloria Bianchi
- Lic. Diego Van Haaster

###### Integrantes del Grupo
- Garibaldi Anele
- Monjelat David
- Garcia Julian
- Abitu Victor
- Perdomo Luciano
