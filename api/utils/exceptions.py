class StocksException(Exception):
    def __init__(self, product_name: str) -> None:
        self.message = (
            f"No hay suficiente cantidad disponible de {product_name} en inventario."
        )
        super().__init__(self.message)


class InventoryNotFoundException(Exception):
    def __init__(self, product_id, admin_id) -> None:
        self.message = f"No existe ningún inventario para el productoID {product_id} bajo el adminID {admin_id}"
        self.product_id = product_id
        self.admin_id = admin_id
        super().__init__(self.message)
