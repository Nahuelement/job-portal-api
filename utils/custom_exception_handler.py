
from rest_framework.views import exception_handler



def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    exception_class = exc.__class__.__name__

    print(exception_class)

    if exception_class == 'AuthenticationFailed':
        response.data = {
            "error": " mail o password invalido"
        }
    if exception_class == 'NotAuthenticated':
        response.data = {
            "error": " no se encunentra autenticado"
        }
    if exception_class == 'InvalidToken':
        response.data = {
            "error": " el valor del token de autentificacion se encuntra expirado, inicie sesion nuevamente "
        }





    return response