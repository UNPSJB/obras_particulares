from django.shortcuts import render

def mostrar_inicio(request):
    return render(request, 'inicio/index.html', {})

def mostrar_inspector(request):
    return render(request, 'inspector/inspector.html', {})

def mostrar_profesional(request):
    return render(request, 'profesional/profesional.html')

def mostrar_jefe_inspector(request):
    return render(request, 'jefe_inspector/jefe_inspector.html')
