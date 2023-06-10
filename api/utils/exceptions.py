class StocksException(Exception):
    def __init__(self, product_name: str) -> None:
        self.message = (
            f"No hay suficiente cantidad disponible de {product_name} en inventario."
        )
        super().__init__(self.message)
