import uuid


def generate_order_id():
    # Generar un UUID version 4, que es aleatorio y seguro para la mayoría de los casos
    order_id = uuid.uuid4()
    return str(order_id)
