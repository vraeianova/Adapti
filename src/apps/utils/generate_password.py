import random
import string


def generate_password():
    # Elegir caracteres aleatorios de letras minúsculas, mayúsculas y dígitos
    password_characters = string.ascii_letters + string.digits
    # Generar una cadena de 5 caracteres al azar
    password = "".join(random.choice(password_characters) for i in range(5))
    return password
