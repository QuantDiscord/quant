from typing import Any, Dict, Mapping, TypeVar, Iterator

__all__ = (
    'JSONObject'
)

KT = TypeVar("KT")
VT = TypeVar("VT")


class JSONObjectBuilder(Mapping[KT, VT]):
    _json_data: Dict[str, Any] = {}

    def __getitem__(self, item) -> Any:
        # print(self._json_data, type(item))
        return self._json_data.get(item)

    def __delitem__(self, key):
        del self._json_data[key]

    def __contains__(self, item):
        return item in self._json_data

    def __len__(self) -> int:
        return len(self._json_data)

    def __iter__(self) -> Iterator:
        return self._json_data

    def get_first_element(self) -> tuple[Any, Any]:
        return [(key, value) for key, value in self._json_data.items()][0]

    def get_last_element(self) -> tuple[Any, Any]:
        return [(key, value) for key, value in self._json_data.items()][-1]

    def put(self, key: Any, element: Any) -> None:
        self._json_data.update({key: element})

    def get_values(self):
        return self._json_data.values()
