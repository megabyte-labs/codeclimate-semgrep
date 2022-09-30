# pylint: skip-file
# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = output_from_dict(json.loads(json_string))

from dataclasses import dataclass
from typing import Any, Optional, List, TypeVar, Type, cast, Callable
from enum import Enum


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
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


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


@dataclass
class Location:
    """Position in a file"""
    col: int
    line: int

    @staticmethod
    def from_dict(obj: Any) -> 'Location':
        assert isinstance(obj, dict)
        col = from_int(obj.get("col"))
        line = from_int(obj.get("line"))
        return Location(col, line)

    def to_dict(self) -> dict:
        result: dict = {}
        result["col"] = from_int(self.col)
        result["line"] = from_int(self.line)
        return result


@dataclass
class Span:
    end: Optional[Location] = None
    file: Optional[str] = None
    source_hash: Optional[str] = None
    start: Optional[Location] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Span':
        assert isinstance(obj, dict)
        end = from_union([Location.from_dict, from_none], obj.get("end"))
        file = from_union([from_str, from_none], obj.get("file"))
        source_hash = from_union([from_str, from_none], obj.get("source_hash"))
        start = from_union([Location.from_dict, from_none], obj.get("start"))
        return Span(end, file, source_hash, start)

    def to_dict(self) -> dict:
        result: dict = {}
        result["end"] = from_union([lambda x: to_class(Location, x), from_none], self.end)
        result["file"] = from_union([from_str, from_none], self.file)
        result["source_hash"] = from_union([from_str, from_none], self.source_hash)
        result["start"] = from_union([lambda x: to_class(Location, x), from_none], self.start)
        return result


@dataclass
class Error:
    """An error encountered while running a check"""
    code: Optional[int] = None
    help: Optional[str] = None
    level: Optional[str] = None
    long_msg: Optional[str] = None
    short_msg: Optional[str] = None
    spans: Optional[List[Span]] = None
    type: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Error':
        assert isinstance(obj, dict)
        code = from_union([from_int, from_none], obj.get("code"))
        help = from_union([from_str, from_none], obj.get("help"))
        level = from_union([from_str, from_none], obj.get("level"))
        long_msg = from_union([from_str, from_none], obj.get("long_msg"))
        short_msg = from_union([from_str, from_none], obj.get("short_msg"))
        spans = from_union([lambda x: from_list(Span.from_dict, x), from_none], obj.get("spans"))
        type = from_union([from_str, from_none], obj.get("type"))
        return Error(code, help, level, long_msg, short_msg, spans, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["code"] = from_union([from_int, from_none], self.code)
        result["help"] = from_union([from_str, from_none], self.help)
        result["level"] = from_union([from_str, from_none], self.level)
        result["long_msg"] = from_union([from_str, from_none], self.long_msg)
        result["short_msg"] = from_union([from_str, from_none], self.short_msg)
        result["spans"] = from_union([lambda x: from_list(lambda x: to_class(Span, x), x), from_none], self.spans)
        result["type"] = from_union([from_str, from_none], self.type)
        return result


class CcCategory(Enum):
    BUG_RISK = "Bug Risk"
    CLARITY = "Clarity"
    COMPATIBILITY = "Compatibility"
    COMPLEXITY = "Complexity"
    DUPLICATION = "Duplication"
    PERFORMANCE = "Performance"
    SECURITY = "Security"
    STYLE = "Style"


class CcSeverity(Enum):
    BLOCKER = "blocker"
    CRITICAL = "critical"
    INFO = "info"
    MAJOR = "major"
    MINOR = "minor"


@dataclass
class Metadata:
    cc_categories: Optional[List[CcCategory]] = None
    cc_severity: Optional[CcSeverity] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Metadata':
        assert isinstance(obj, dict)
        cc_categories = from_union([lambda x: from_list(CcCategory, x), from_none], obj.get("cc.categories"))
        cc_severity = from_union([CcSeverity, from_none], obj.get("cc.severity"))
        return Metadata(cc_categories, cc_severity)

    def to_dict(self) -> dict:
        result: dict = {}
        result["cc.categories"] = from_union([lambda x: from_list(lambda x: to_enum(CcCategory, x), x), from_none], self.cc_categories)
        result["cc.severity"] = from_union([lambda x: to_enum(CcSeverity, x), from_none], self.cc_severity)
        return result


class Severity(Enum):
    ERROR = "ERROR"
    INFO = "INFO"
    WARNING = "WARNING"


@dataclass
class Extra:
    """Extra result data"""
    message: str
    metadata: Metadata
    severity: Severity

    @staticmethod
    def from_dict(obj: Any) -> 'Extra':
        assert isinstance(obj, dict)
        message = from_str(obj.get("message"))
        metadata = Metadata.from_dict(obj.get("metadata"))
        severity = Severity(obj.get("severity"))
        return Extra(message, metadata, severity)

    def to_dict(self) -> dict:
        result: dict = {}
        result["message"] = from_str(self.message)
        result["metadata"] = to_class(Metadata, self.metadata)
        result["severity"] = to_enum(Severity, self.severity)
        return result


@dataclass
class Result:
    """A result matching a check"""
    """Identifier for the check that matched"""
    check_id: str
    end: Location
    extra: Extra
    """Location of the matching file"""
    path: str
    start: Location

    @staticmethod
    def from_dict(obj: Any) -> 'Result':
        assert isinstance(obj, dict)
        check_id = from_str(obj.get("check_id"))
        end = Location.from_dict(obj.get("end"))
        extra = Extra.from_dict(obj.get("extra"))
        path = from_str(obj.get("path"))
        start = Location.from_dict(obj.get("start"))
        return Result(check_id, end, extra, path, start)

    def to_dict(self) -> dict:
        result: dict = {}
        result["check_id"] = from_str(self.check_id)
        result["end"] = to_class(Location, self.end)
        result["extra"] = to_class(Extra, self.extra)
        result["path"] = from_str(self.path)
        result["start"] = to_class(Location, self.start)
        return result


@dataclass
class Output:
    """A JSON Schema describing the Semgrep output format. This isn't exhaustive, and only
    implements enough of the output to be useful for our purposes
    """
    """Results from the run"""
    errors: List[Error]
    """Results of the run"""
    results: List[Result]

    @staticmethod
    def from_dict(obj: Any) -> 'Output':
        assert isinstance(obj, dict)
        errors = from_list(Error.from_dict, obj.get("errors"))
        results = from_list(Result.from_dict, obj.get("results"))
        return Output(errors, results)

    def to_dict(self) -> dict:
        result: dict = {}
        result["errors"] = from_list(lambda x: to_class(Error, x), self.errors)
        result["results"] = from_list(lambda x: to_class(Result, x), self.results)
        return result


def output_from_dict(s: Any) -> Output:
    return Output.from_dict(s)


def output_to_dict(x: Output) -> Any:
    return to_class(Output, x)

SCHEMA = {'$schema': 'http://json-schema.org/draft-07/schema#',
 'definitions': {'error': {'$id': '#/definitions/error',
                           'description': 'An error encountered while running '
                                          'a check',
                           'properties': {'code': {'type': 'integer'},
                                          'help': {'type': 'string'},
                                          'level': {'type': 'string'},
                                          'long_msg': {'type': 'string'},
                                          'short_msg': {'type': 'string'},
                                          'spans': {'items': {'properties': {'end': {'$ref': '#/definitions/location'},
                                                                             'file': {'type': 'string'},
                                                                             'source_hash': {'type': 'string'},
                                                                             'start': {'$ref': '#/definitions/location'}},
                                                              'type': 'object'},
                                                    'type': 'array'},
                                          'type': {'type': 'string'}},
                           'type': 'object'},
                 'extra': {'$id': '#/definitions/extra',
                           'description': 'Extra result data',
                           'properties': {'message': {'type': 'string'},
                                          'metadata': {'additionalProperties': True,
                                                       'properties': {'cc.categories': {'items': {'enum': ['Bug '
                                                                                                           'Risk',
                                                                                                           'Clarity',
                                                                                                           'Compatibility',
                                                                                                           'Complexity',
                                                                                                           'Duplication',
                                                                                                           'Performance',
                                                                                                           'Security',
                                                                                                           'Style'],
                                                                                                  'type': 'string'},
                                                                                        'type': 'array'},
                                                                      'cc.severity': {'enum': ['info',
                                                                                               'minor',
                                                                                               'major',
                                                                                               'critical',
                                                                                               'blocker'],
                                                                                      'type': 'string'}},
                                                       'type': 'object'},
                                          'severity': {'enum': ['ERROR',
                                                                'WARNING',
                                                                'INFO'],
                                                       'type': 'string'}},
                           'required': ['message', 'severity', 'metadata'],
                           'type': 'object'},
                 'location': {'$id': '#/definitions/location',
                              'description': 'Position in a file',
                              'properties': {'col': {'type': 'integer'},
                                             'line': {'type': 'integer'}},
                              'required': ['line', 'col'],
                              'type': 'object'},
                 'result': {'$id': '#/definitions/result',
                            'description': 'A result matching a check',
                            'properties': {'check_id': {'description': 'Identifier '
                                                                       'for '
                                                                       'the '
                                                                       'check '
                                                                       'that '
                                                                       'matched',
                                                        'type': 'string'},
                                           'end': {'$ref': '#/definitions/location'},
                                           'extra': {'$ref': '#/definitions/extra'},
                                           'path': {'description': 'Location '
                                                                   'of the '
                                                                   'matching '
                                                                   'file',
                                                    'type': 'string'},
                                           'start': {'$ref': '#/definitions/location'}},
                            'required': ['check_id',
                                         'path',
                                         'start',
                                         'end',
                                         'extra'],
                            'type': 'object'}},
 'description': 'A JSON Schema describing the Semgrep output format. This '
                "isn't exhaustive, and only implements enough of the output to "
                'be useful for our purposes',
 'properties': {'errors': {'$id': '#/properties/errors',
                           'description': 'Results from the run',
                           'items': {'$ref': '#/definitions/error'},
                           'type': 'array'},
                'results': {'$id': '#/properties/results',
                            'description': 'Results of the run',
                            'items': {'$ref': '#/definitions/result'},
                            'type': 'array'}},
 'required': ['results', 'errors'],
 'title': 'Semgrep Output',
 'type': 'object'}
