from app.suppliers.base import AbstractSupplier


class SupplierRegistry:
    def __init__(self) -> None:
        self._suppliers: dict[str, AbstractSupplier] = {}

    def register(self, supplier: AbstractSupplier) -> None:
        self._suppliers[supplier.name] = supplier

    def all(self) -> list[AbstractSupplier]:
        return list(self._suppliers.values())

    async def close_all(self) -> None:
        for supplier in self._suppliers.values():
            await supplier.close()
