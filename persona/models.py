from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractUser, Group

class Rol(models.Model):

    class Meta:
        abstract = True

class Profesional(Rol):
    CATEGORIAS = [

        (1, 'Categoria 1'),
        (2, 'Categoria 2'),
        (3, 'Categoria 3'),
    ]
    matricula = models.CharField(max_length=10)
    profesion = models.CharField(max_length=10)  # ["Maestro Mayor de Obra", "Ingeniero Civil", "Arquitecto"]
    categoria = models.IntegerField(choices=CATEGORIAS)
    certificado = models.ImageField(upload_to='certificado/', null= True)

class Propietario(Rol):
    pass

class Usuario(Rol, AbstractUser):
    PROFESIONAL = "profesional"
    PROPIETARIO = "propietario"
    ADMINISTRATIVO = "administrativo"
    VISADOR = "visador"
    INSPECTOR = "inspector"
    DIRECTOR = "director"

    def get_view_name(self):
        return self.groups.first().name

class Persona(models.Model):
    SEXOS = [ {'F', 'Femenino'}, {'M', 'Masculino'} ]
    dni =  models.CharField(max_length = 8, unique = True)
    apellido  = models.CharField(max_length = 50)
    nombre = models.CharField(max_length = 50)
    mail = models.CharField(max_length = 40)
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
            # Hacer una funcion que genere claves aleatorias
            password = "123456"
            aux_usuario = Usuario.objects.create_user( username=self.mail,
                                                        email=self.mail,
                                                        password=password)
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
