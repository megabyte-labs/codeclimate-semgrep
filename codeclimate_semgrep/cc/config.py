# pylint: skip-file
# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = config_from_dict(json.loads(json_string))

from dataclasses import dataclass
from typing import Optional, List, Any, TypeVar, Callable, Type, cast


T = TypeVar("T")


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class Run:
    configs: Optional[List[str]] = None
    exclude: Optional[List[str]] = None
    include: Optional[List[str]] = None
    lang: Optional[str] = None
    pattern: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Run':
        assert isinstance(obj, dict)
        configs = from_union([lambda x: from_list(from_str, x), from_none], obj.get("configs"))
        exclude = from_union([lambda x: from_list(from_str, x), from_none], obj.get("exclude"))
        include = from_union([lambda x: from_list(from_str, x), from_none], obj.get("include"))
        lang = from_union([from_str, from_none], obj.get("lang"))
        pattern = from_union([from_str, from_none], obj.get("pattern"))
        return Run(configs, exclude, include, lang, pattern)

    def to_dict(self) -> dict:
        result: dict = {}
        result["configs"] = from_union([lambda x: from_list(from_str, x), from_none], self.configs)
        result["exclude"] = from_union([lambda x: from_list(from_str, x), from_none], self.exclude)
        result["include"] = from_union([lambda x: from_list(from_str, x), from_none], self.include)
        result["lang"] = from_union([from_str, from_none], self.lang)
        result["pattern"] = from_union([from_str, from_none], self.pattern)
        return result


@dataclass
class Config:
    """A JSON Schema describing the Code Climate Engine config format"""
    """Paths to run against"""
    include_paths: List[str]
    """Semgrep runs"""
    runs: List[Run]

    @staticmethod
    def from_dict(obj: Any) -> 'Config':
        assert isinstance(obj, dict)
        include_paths = from_list(from_str, obj.get("include_paths"))
        runs = from_list(Run.from_dict, obj.get("runs"))
        return Config(include_paths, runs)

    def to_dict(self) -> dict:
        result: dict = {}
        result["include_paths"] = from_list(from_str, self.include_paths)
        result["runs"] = from_list(lambda x: to_class(Run, x), self.runs)
        return result


def config_from_dict(s: Any) -> Config:
    return Config.from_dict(s)


def config_to_dict(x: Config) -> Any:
    return to_class(Config, x)

SCHEMA = {'$schema': 'http://json-schema.org/draft-07/schema#',
 'definitions': {'run': {'$id': '#/definitions/run',
                         'additionalProperties': False,
                         'oneOf': [{'required': ['configs']},
                                   {'required': ['pattern', 'lang']}],
                         'properties': {'configs': {'items': {'type': 'string'},
                                                    'minItems': 1,
                                                    'type': 'array'},
                                        'exclude': {'items': {'type': 'string'},
                                                    'type': 'array'},
                                        'include': {'items': {'type': 'string'},
                                                    'type': 'array'},
                                        'lang': {'type': 'string'},
                                        'pattern': {'type': 'string'}},
                         'type': 'object'}},
 'description': 'A JSON Schema describing the Code Climate Engine config '
                'format',
 'properties': {'include_paths': {'$id': '#/properties/include_paths',
                                  'description': 'Paths to run against',
                                  'items': {'type': 'string'},
                                  'type': 'array'},
                'runs': {'$id': '#/properties/runs',
                         'description': 'Semgrep runs',
                         'items': {'$ref': '#/definitions/run'},
                         'minItems': 1,
                         'type': 'array'}},
 'required': ['include_paths', 'runs'],
 'title': 'Config',
 'type': 'object'}
