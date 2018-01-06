from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from random import choice

class Rol(models.Model):
    '''
    Correspondiente a un rol dentro del sistema
    '''
    class Meta:
        abstract = True

class Profesional(Rol):
    '''
    Correspondiente a un rol profesional dentro del sistema
    '''
    CATEGORIAS = [

        (1, 'Categoria 1'),
        (2, 'Categoria 2'),
        (3, 'Categoria 3'),
    ]
    matricula = models.CharField(max_length=10)
    profesion = models.CharField(max_length=10)  # ["Maestro Mayor de Obra", "Ingeniero Civil", "Arquitecto"]
    categoria = models.IntegerField(choices=CATEGORIAS)
    certificado = models.ImageField(upload_to='certificado/', null=True)

    def __str__(self):
        if hasattr(self, "persona"):
            return "{}".format(self.persona)
        return "Matricula: {}, Profesion: {}".format(self.matricula, self.profesion)


class Propietario(Rol):
    '''
    Correspondiente a un rol propietario dentro del sistema
    '''
    def __str__(self):
        try:
            return str(self.persona)
        except:
            return "PONEME UNA PERSONA.... ANIMAL"

    def obtener_persona(self):
        return Persona.get_self().nombre


class Usuario(Rol, AbstractUser):
    '''
    Correspondiente a un rol usuario dentro del sistema
    '''
    PROFESIONAL = "profesional"
    PROPIETARIO = "propietario"
    ADMINISTRATIVO = "administrativo"
    VISADOR = "visador"
    INSPECTOR = "inspector"
    DIRECTOR = "director"

    def get_view_name(self):
        return self.groups.first().name

    def get_view_groups(self):
        return self.groups.all()

class Persona(models.Model):
    '''
    Correspondiente al modelo de persona dentro del sistema
    '''
    SEXOS = [{'F', 'Femenino'}, {'M', 'Masculino'}]
    dni = models.IntegerField(unique = True)
    apellido = models.CharField(max_length = 50)
    nombre = models.CharField(max_length = 50)
    mail = models.EmailField(max_length = 40)
    cuil = models.CharField(max_length = 14)    #el ultimo numero va a ser 00..09
    domicilio = models.CharField(max_length = 50)
    telefono = models.CharField(max_length = 15)
    profesional = models.OneToOneField(Profesional, blank=True, null=True)
    propietario = models.OneToOneField(Propietario, blank=True, null=True)
    usuario = models.OneToOneField(Usuario, blank=True, null=True)

    def __str__(self):
        return "{}, {}" .format(self.apellido, self.nombre)

    def crear_usuario(self, *extra_grupos):
        grupos = list(extra_grupos)
        created = False
        password = ""
        aux_usuario = None
        if self.usuario is None:
            password = generar_password()
            aux_usuario = Usuario.objects.create_user(username=self.mail, email=self.mail, password=password)
            created = True
        self.usuario = aux_usuario
        if self.profesional is not None:
            grupos.append(Usuario.PROFESIONAL)
        if self.propietario is not None:
            grupos.append(Usuario.PROPIETARIO)
        for nombre in grupos:
            g = Group.objects.get(name=nombre)
            self.usuario.groups.add(g)
        self.save()
        return created, password, self.usuario

    def get_profesional(self):
        return self.profesional

    def get_propietario(self):
        return self.propietario

def generar_password():
    '''
    Funcion generar_password.
    Funcion que genera una contraseña con valores aleatorios.
    :return password: contraseña generada.
    '''
    longitud = 6
    valores = "123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    password = ""
    password = password.join([choice(valores) for i in range(longitud)])
    return password
