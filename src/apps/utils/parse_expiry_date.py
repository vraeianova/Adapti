def parse_expiry_date(expiry_string):
    try:
        # Dividir la cadena en mes y año
        month_str, year_str = expiry_string.split("/")

        # Convertir a enteros
        expire_month = int(month_str)
        expire_year = (
            int(year_str) + 2000
        )  # Convertir el año a formato de cuatro dígitos (ejemplo: 23 -> 2023)

        # Crear y devolver el diccionario
        result = {"expire_month": expire_month, "expire_year": expire_year}
        return result
    except ValueError:
        # En caso de error, retornar None o un valor indicativo de error
        return None
