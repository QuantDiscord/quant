from typing import Any, Dict, Mapping, TypeVar, Iterator

__all__ = (
    'JSONObject'
)

KT = TypeVar("KT")
VT = TypeVar("VT")


class MutableJsonBuilder(Mapping[KT, VT]):
    def __iter__(self) -> Iterator:
        ...

    def __init__(self, dict_object: Dict[str, Any] = None) -> None:
        self._json_data: Dict[str, Any] = {}

        if dict_object is not None:
            self._json_data = dict_object

    def asdict(self) -> Dict:
        return self._json_data

    def __getitem__(self, item) -> Any:
        return self._json_data.get(item)

    def __delitem__(self, key):
        del self._json_data[key]

    def __contains__(self, item):
        return item in self._json_data

    def __len__(self) -> int:
        return len(self._json_data)

    def __repr__(self) -> str:
        return f"<MutableJsonBuilder {self._json_data}>"

    def get_first_element(self) -> tuple[Any, Any]:
        return [(key, value) for key, value in self._json_data.items()][0]

    def get_last_element(self) -> tuple[Any, Any]:
        return [(key, value) for key, value in self._json_data.items()][-1]

    def put(self, key: Any, element: Any) -> None:
        if isinstance(self._json_data, MutableJsonBuilder):
            self._json_data = self._json_data.asdict()

        self._json_data.update({key: element})

    def get_values(self):
        return self._json_data.values()
