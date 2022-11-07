from django.http import JsonResponse

def handler404(request, exception):
    message = ('Ruta no existe')
    response = JsonResponse(data = {'error': message})
    response.status_code = 404
    return response


def handler500(request):
    message = ('Error interno del servidor')
    response = JsonResponse(data = {'error': message})
    response.status_code = 500
    return response


