# pylint: skip-file
# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = output_from_dict(json.loads(json_string))

from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional, List, TypeVar, Type, cast, Callable


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


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


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


class Category(Enum):
    BUG_RISK = "Bug Risk"
    CLARITY = "Clarity"
    COMPATIBILITY = "Compatibility"
    COMPLEXITY = "Complexity"
    DUPLICATION = "Duplication"
    PERFORMANCE = "Performance"
    SECURITY = "Security"
    STYLE = "Style"


@dataclass
class Content:
    """More information about the issue's check, including a description of the issue, how to
    fix it, and relevant links
    """
    """A Markdown document"""
    body: str

    @staticmethod
    def from_dict(obj: Any) -> 'Content':
        assert isinstance(obj, dict)
        body = from_str(obj.get("body"))
        return Content(body)

    def to_dict(self) -> dict:
        result: dict = {}
        result["body"] = from_str(self.body)
        return result


@dataclass
class Lines:
    begin: int
    end: int

    @staticmethod
    def from_dict(obj: Any) -> 'Lines':
        assert isinstance(obj, dict)
        begin = from_int(obj.get("begin"))
        end = from_int(obj.get("end"))
        return Lines(begin, end)

    def to_dict(self) -> dict:
        result: dict = {}
        result["begin"] = from_int(self.begin)
        result["end"] = from_int(self.end)
        return result


@dataclass
class Position:
    column: int
    line: int

    @staticmethod
    def from_dict(obj: Any) -> 'Position':
        assert isinstance(obj, dict)
        column = from_int(obj.get("column"))
        line = from_int(obj.get("line"))
        return Position(column, line)

    def to_dict(self) -> dict:
        result: dict = {}
        result["column"] = from_int(self.column)
        result["line"] = from_int(self.line)
        return result


@dataclass
class Positions:
    begin: Position
    end: Position

    @staticmethod
    def from_dict(obj: Any) -> 'Positions':
        assert isinstance(obj, dict)
        begin = Position.from_dict(obj.get("begin"))
        end = Position.from_dict(obj.get("end"))
        return Positions(begin, end)

    def to_dict(self) -> dict:
        result: dict = {}
        result["begin"] = to_class(Position, self.begin)
        result["end"] = to_class(Position, self.end)
        return result


@dataclass
class Location:
    """A range of a source code file"""
    """The file path relative to /code"""
    path: str
    lines: Optional[Lines] = None
    positions: Optional[Positions] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Location':
        assert isinstance(obj, dict)
        path = from_str(obj.get("path"))
        lines = from_union([Lines.from_dict, from_none], obj.get("lines"))
        positions = from_union([Positions.from_dict, from_none], obj.get("positions"))
        return Location(path, lines, positions)

    def to_dict(self) -> dict:
        result: dict = {}
        result["path"] = from_str(self.path)
        result["lines"] = from_union([lambda x: to_class(Lines, x), from_none], self.lines)
        result["positions"] = from_union([lambda x: to_class(Positions, x), from_none], self.positions)
        return result


class Severity(Enum):
    """A string describing the potential impact of the issue found"""
    BLOCKER = "blocker"
    CRITICAL = "critical"
    INFO = "info"
    MAJOR = "major"
    MINOR = "minor"


@dataclass
class Trace:
    """A data structure meant to represent ordered or unordered lists of source code locations"""
    locations: List[Location]
    """When true, this Trace object will be treated like an ordered stacktrace by the CLI and
    the Code Climate UI
    """
    stacktrace: Optional[bool] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Trace':
        assert isinstance(obj, dict)
        locations = from_list(Location.from_dict, obj.get("locations"))
        stacktrace = from_union([from_bool, from_none], obj.get("stacktrace"))
        return Trace(locations, stacktrace)

    def to_dict(self) -> dict:
        result: dict = {}
        result["locations"] = from_list(lambda x: to_class(Location, x), self.locations)
        result["stacktrace"] = from_union([from_bool, from_none], self.stacktrace)
        return result


class TypeEnum(Enum):
    """Must always be 'issue'"""
    ISSUE = "issue"


@dataclass
class Output:
    """A JSON Schema describing the Code Climate Engine output format"""
    location: Location
    """At least one category indicating the nature of the issue being reported"""
    categories: List[Category]
    """A unique name representing the static analysis check that emitted this issue"""
    check_name: str
    """A string explaining the issue that was detected"""
    description: str
    """Must always be 'issue'"""
    type: TypeEnum
    """A unique, deterministic identifier for the specific issue being reported to allow a user
    to exclude it from future analyses
    """
    fingerprint: Optional[str] = None
    content: Optional[Content] = None
    """An optional array of Location objects"""
    other_locations: Optional[List[Location]] = None
    """An integer indicating a rough estimate of how long it would take to resolve the reported
    issue
    """
    remediation_points: Optional[int] = None
    """A string describing the potential impact of the issue found"""
    severity: Optional[Severity] = None
    trace: Optional[Trace] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Output':
        assert isinstance(obj, dict)
        location = Location.from_dict(obj.get("location"))
        categories = from_list(Category, obj.get("categories"))
        check_name = from_str(obj.get("check_name"))
        description = from_str(obj.get("description"))
        type = TypeEnum(obj.get("type"))
        fingerprint = from_union([from_str, from_none], obj.get("fingerprint"))
        content = from_union([Content.from_dict, from_none], obj.get("content"))
        other_locations = from_union([lambda x: from_list(Location.from_dict, x), from_none], obj.get("other_locations"))
        remediation_points = from_union([from_int, from_none], obj.get("remediation_points"))
        severity = from_union([Severity, from_none], obj.get("severity"))
        trace = from_union([Trace.from_dict, from_none], obj.get("trace"))
        return Output(location, categories, check_name, description, type, fingerprint, content, other_locations, remediation_points, severity, trace)

    def to_dict(self) -> dict:
        result: dict = {}
        result["location"] = to_class(Location, self.location)
        result["categories"] = from_list(lambda x: to_enum(Category, x), self.categories)
        result["check_name"] = from_str(self.check_name)
        result["description"] = from_str(self.description)
        result["type"] = to_enum(TypeEnum, self.type)
        result["fingerprint"] = from_union([from_str, from_none], self.fingerprint)
        result["content"] = from_union([lambda x: to_class(Content, x), from_none], self.content)
        result["other_locations"] = from_union([lambda x: from_list(lambda x: to_class(Location, x), x), from_none], self.other_locations)
        result["remediation_points"] = from_union([from_int, from_none], self.remediation_points)
        result["severity"] = from_union([lambda x: to_enum(Severity, x), from_none], self.severity)
        result["trace"] = from_union([lambda x: to_class(Trace, x), from_none], self.trace)
        return result


def output_from_dict(s: Any) -> Output:
    return Output.from_dict(s)


def output_to_dict(x: Output) -> Any:
    return to_class(Output, x)

SCHEMA = {'$schema': 'http://json-schema.org/draft-07/schema#',
 'definitions': {'content': {'$id': '#/definitions/content',
                             'description': 'More information about the '
                                            "issue's check, including a "
                                            'description of the issue, how to '
                                            'fix it, and relevant links',
                             'properties': {'body': {'description': 'A '
                                                                    'Markdown '
                                                                    'document',
                                                     'type': 'string'}},
                             'required': ['body'],
                             'type': 'object'},
                 'location': {'$id': '#/definitions/location',
                              'description': 'A range of a source code file',
                              'oneOf': [{'required': ['lines']},
                                        {'required': ['positions']}],
                              'properties': {'lines': {'properties': {'begin': {'type': 'integer'},
                                                                      'end': {'type': 'integer'}},
                                                       'required': ['begin',
                                                                    'end'],
                                                       'type': 'object'},
                                             'path': {'description': 'The file '
                                                                     'path '
                                                                     'relative '
                                                                     'to /code',
                                                      'type': 'string'},
                                             'positions': {'properties': {'begin': {'$ref': '#/definitions/position'},
                                                                          'end': {'$ref': '#/definitions/position'}},
                                                           'required': ['begin',
                                                                        'end'],
                                                           'type': 'object'}},
                              'required': ['path'],
                              'type': 'object'},
                 'position': {'$id': '#/definitions/position',
                              'properties': {'column': {'type': 'integer'},
                                             'line': {'type': 'integer'}},
                              'required': ['line', 'column'],
                              'type': 'object'},
                 'trace': {'$id': '#/definitions/trace',
                           'description': 'A data structure meant to represent '
                                          'ordered or unordered lists of '
                                          'source code locations',
                           'properties': {'locations': {'items': {'$ref': '#/definitions/location'},
                                                        'type': 'array'},
                                          'stacktrace': {'description': 'When '
                                                                        'true, '
                                                                        'this '
                                                                        'Trace '
                                                                        'object '
                                                                        'will '
                                                                        'be '
                                                                        'treated '
                                                                        'like '
                                                                        'an '
                                                                        'ordered '
                                                                        'stacktrace '
                                                                        'by '
                                                                        'the '
                                                                        'CLI '
                                                                        'and '
                                                                        'the '
                                                                        'Code '
                                                                        'Climate '
                                                                        'UI',
                                                         'type': 'boolean'}},
                           'required': ['locations'],
                           'type': 'object'}},
 'description': 'A JSON Schema describing the Code Climate Engine output '
                'format',
 'properties': {'categories': {'$id': '#/properties/categories',
                               'description': 'At least one category '
                                              'indicating the nature of the '
                                              'issue being reported',
                               'examples': [['Complexity']],
                               'items': {'enum': ['Bug Risk',
                                                  'Clarity',
                                                  'Compatibility',
                                                  'Complexity',
                                                  'Duplication',
                                                  'Performance',
                                                  'Security',
                                                  'Style'],
                                         'type': 'string'},
                               'minItems': 1,
                               'type': 'array'},
                'check_name': {'$id': '#/properties/check_name',
                               'description': 'A unique name representing the '
                                              'static analysis check that '
                                              'emitted this issue',
                               'examples': ['Bug Risk/Unused Variable'],
                               'type': 'string'},
                'content': {'$ref': '#/definitions/content'},
                'description': {'$id': '#/properties/description',
                                'description': 'A string explaining the issue '
                                               'that was detected',
                                'examples': ['Unused local variable `foo`'],
                                'type': 'string'},
                'fingerprint': {'$id': '#/properties/fingerprint',
                                'description': 'A unique, deterministic '
                                               'identifier for the specific '
                                               'issue being reported to allow '
                                               'a user to exclude it from '
                                               'future analyses',
                                'examples': ['abcd1234'],
                                'type': 'string'},
                'location': {'$ref': '#/definitions/location'},
                'other_locations': {'$id': '#/properties/other_locations',
                                    'description': 'An optional array of '
                                                   'Location objects',
                                    'items': {'$ref': '#/definitions/location'},
                                    'type': 'array'},
                'remediation_points': {'$id': '#/properties/remediation_points',
                                       'description': 'An integer indicating a '
                                                      'rough estimate of how '
                                                      'long it would take to '
                                                      'resolve the reported '
                                                      'issue',
                                       'examples': [50000],
                                       'type': 'integer'},
                'severity': {'$id': '#/properties/severity',
                             'description': 'A string describing the potential '
                                            'impact of the issue found',
                             'enum': ['info',
                                      'minor',
                                      'major',
                                      'critical',
                                      'blocker'],
                             'examples': ['info'],
                             'type': 'string'},
                'trace': {'$ref': '#/definitions/trace'},
                'type': {'$id': '#/properties/type',
                         'description': "Must always be 'issue'",
                         'enum': ['issue'],
                         'examples': ['issue'],
                         'type': 'string'}},
 'required': ['type', 'check_name', 'description', 'categories', 'location'],
 'title': 'Result',
 'type': 'object'}
