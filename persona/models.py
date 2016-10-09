from __future__ import unicode_literals

from django.db import models


class Rol(models.Model):

    class Meta:
        abstract = True

class Profesional(Rol):

    CATEGORIAS = [

        (1, 'Categoria 1'),
        (2, 'Categoria 2'),
        (3, 'Categoria 3'),
    ]
    matricula = models.CharField(max_length = 10)
    profesion = ["Maestro Mayor de Obra", "Ingeniero Civil", "Arquitecto"]
    categoria = models.IntegerField()


class Propietario(Rol):
    pass

class Usuario(Rol):
    nombre_de_usuario = models.CharField(max_length = 15)
    contrasenia = models.CharField(max_length = 15)

    def login(self):
        print("Iniciando secion")

class Persona(models.Model):
    SEXOS = [ {'F', 'Femenino'}, {'M', 'Masculino'} ]
    dni =  models.CharField(max_length = 8, unique = True)
    apellido  = models.CharField(max_length = 50)
    nombre = models.CharField(max_length = 50)
    mail = models.CharField(max_length = 20)
    cuil = models.CharField(max_length = 14)    #el ultimo numero va a ser 00..09
    domicilio = models.CharField(max_length = 50)
    telefono = models.CharField(max_length = 15)
    profesional = models.OneToOneField(Profesional, blank=True)
    propietario = models.OneToOneField(Propietario, blank=True)
    Usuario = models.OneToOneField(Usuario, blank=True)


    def __str__(self):
        return "{}, {}" .format(self.apellido, self.nombre)

