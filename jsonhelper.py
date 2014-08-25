import json
import re
from datetime import datetime


class JsonHelper:

    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

    @staticmethod
    def to_json(obj):
        return json.dumps(obj, default=JsonHelper.__date_serializer)

    @staticmethod
    def to_json_file(obj, filename):
        with open(filename, 'w') as f:
            json.dump(obj, f, sort_keys=True, indent=4, default=JsonHelper.__date_serializer)

    @staticmethod
    def from_json(json_str):
        return json.loads(json_str, object_hook=JsonHelper.__deserializer_helper)

    @staticmethod
    def from_json_file(filename):
        with open(filename, 'r') as f:
            return json.load(f, object_hook=JsonHelper.__deserializer_helper)

    @staticmethod
    def __date_serializer(obj):
        if isinstance(obj, datetime):
            serial = obj.isoformat()
            return serial

    @staticmethod
    def __deserializer_helper(dct):
        for k, v in dct.items():
            if isinstance(v, basestring) and len(v) == 19:
                try:
                    dct[k] = datetime.strptime(v, JsonHelper.DATE_FORMAT)
                except:
                    dct[k] = v
        return dct