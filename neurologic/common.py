import json
import os
import re
import struct
import subprocess
import typing
from collections import OrderedDict
from glob import glob

import holoviews as hv


def extract_parameters(filename):
    match = re.search(r"<(.+?)> \((.+?)\) \[(.+?)\]", filename)
    dataset_parameters = OrderedDict((key, json.loads(value)) for key, value in map(lambda keyval: keyval.split(": "),
                                                                                    match.group(1).split(
                                                                                        ", ") if match else []))
    learning_parameters = OrderedDict((key, json.loads(value)) for key, value in map(lambda keyval: keyval.split(": "),
                                                                                     match.group(2).split(
                                                                                         ", ") if match else []))
    if match:
        dataset_parameters['run_id'] = match.group(3)
    learning_parameters["fold"] = int(re.search(r"fold([0-9]+)", filename).group(1))
    learning_parameters["restart"] = int(re.search(r"restart([0-9]+)", filename).group(1))
    return dataset_parameters, learning_parameters


def extract_all_parameters(base_path, base_name):
    all_parameters = OrderedDict()
    for name in glob(os.path.join(base_path, f"{base_name}*", "learning_stats-fold*-restart*")):
        parameters = extract_parameters(name)
        for ind, params in enumerate(parameters):
            for key, value in params.items():
                all_parameters.setdefault(key, {"values": set(), "type": "dataset" if not ind else "learning"})[
                    "values"].add(value)
    return all_parameters


def parse(f: typing.BinaryIO):
    """
    Parse Java .ser format and convert it to Python equivalent object.
    :return: Python dict, array, string or int
    """
    h = lambda s: ' '.join('%.2X' % x for x in s)  # format as hex
    p = lambda s: sum(x * 256 ** i for i, x in enumerate(reversed(s)))  # parse integer
    magic = f.read(2)
    assert magic == b'\xAC\xED', h(magic)  # STREAM_MAGIC
    assert p(f.read(2)) == 5  # STREAM_VERSION
    handles = []

    def parse_obj():
        b = f.read(1)
        if not b:
            raise StopIteration  # not necessarily the best thing to throw here.
        if b == b'\x70':  # p TC_NULL
            return None
        elif b == b'\x71':  # q TC_REFERENCE
            handle = p(f.read(4)) - 0x7E0000  # baseWireHandle
            o = handles[handle]
            return o[1]
        elif b == b'\x74':  # t TC_STRING
            string = f.read(p(f.read(2))).decode('utf-8')
            handles.append(('TC_STRING', string))
            return string
        elif b == b'\x75':  # u TC_ARRAY
            data = []
            cls = parse_obj()
            size = p(f.read(4))
            handles.append(('TC_ARRAY', data))
            array_types = {b'[B': {"size": 1, "format": 'B'},
                           b'[I': {"size": 4, "format": 'i'},
                           b'[F': {"size": 4, "format": 'f'},
                           b'[D': {"size": 8, "format": 'd'},
                           b'[S': {"size": 2, "format": 'e'}}
            assert cls['_name'] in array_types.keys(), cls['_name']
            data = struct.unpack('>' + str(size) + array_types[cls['_name']]["format"],
                                 f.read(array_types[cls['_name']]['size'] * size))
            return list(data)
        elif b == b'\x7E':  # ~ TC_ENUM
            enum = {}
            enum['_cls'] = parse_obj()
            handles.append(('TC_ENUM', enum))
            enum['_name'] = parse_obj()
            return enum
        elif b == b'\x72':  # r TC_CLASSDESC
            cls = {'fields': []}
            full_name = f.read(p(f.read(2)))
            cls['_name'] = full_name.split(b'.')[-1]  # i don't care about full path
            f.read(8)  # uid
            cls['flags'] = f.read(1)
            handles.append(('TC_CLASSDESC', cls))
            assert cls['flags'] in (b'\2', b'\3', b'\x0C', b'\x12'), h(cls['flags'])
            b = f.read(2)
            for i in range(p(b)):
                typ = f.read(1)
                name = f.read(p(f.read(2)))
                fcls = parse_obj() if typ in b'L[' else b''
                cls['fields'].append((name, typ, fcls.split(b'/')[-1]))  # don't care about full path
            b = f.read(1)
            assert b == b'\x78', h(b)
            cls['parent'] = parse_obj()
            return cls
        # TC_OBJECT
        assert b == b'\x73', (h(b), h(f.read(4)), repr(f.read(50)))
        obj = {}
        obj['_cls'] = parse_obj()
        obj['_name'] = obj['_cls']['_name']
        handle = len(handles)
        parents = [obj['_cls']]
        while parents[0]['parent']:
            parents.insert(0, parents[0]['parent'])
        handles.append(('TC_OBJECT', obj))
        for cls in parents:
            for name, typ, fcls in cls['fields'] if cls['flags'] in (b'\2', b'\3') else []:
                if typ == b'I':  # Integer
                    obj[name] = p(f.read(4))
                elif typ == b'S':  # Short
                    obj[name] = p(f.read(2))
                elif typ == b'J':  # Long
                    obj[name] = p(f.read(8))
                elif typ == b'Z':  # Bool
                    b = f.read(1)
                    assert p(b) in (0, 1)
                    obj[name] = bool(p(b))
                elif typ == b'F':  # Float
                    obj[name] = h(f.read(4))
                elif typ in b'BC':  # Byte, Char
                    obj[name] = f.read(1)
                elif typ in b'L[':  # Object, Array
                    obj[name] = parse_obj()
                else:  # Unknown
                    assert False, (name, typ, fcls)
            if cls['flags'] in (b'\3', b'\x0C'):  # SC_WRITE_METHOD, SC_BLOCKDATA
                b = f.read(1)
                if b == b'\x77':  # see the readObject / writeObject methods
                    block = f.read(p(f.read(1)))
                    if cls['_name'].endswith(b'HashMap') or cls['_name'].endswith(b'Hashtable'):
                        # http://javasourcecode.org/html/open-source/jdk/jdk-6u23/java/util/HashMap.java.html
                        # http://javasourcecode.org/html/open-source/jdk/jdk-6u23/java/util/Hashtable.java.html
                        assert len(block) == 8, h(block)
                        size = p(block[4:])
                        obj['data'] = []  # python doesn't allow dicts as keys
                        for i in range(size):
                            k = parse_obj()
                            v = parse_obj()
                            obj['data'].append((k, v))
                        try:
                            obj['data'] = dict(obj['data'])
                        except TypeError:
                            pass  # non hashable keys
                    elif cls['_name'].endswith(b'HashSet'):
                        # http://javasourcecode.org/html/open-source/jdk/jdk-6u23/java/util/HashSet.java.html
                        assert len(block) == 12, h(block)
                        size = p(block[-4:])
                        obj['data'] = []
                        for i in range(size):
                            obj['data'].append(parse_obj())
                    elif cls['_name'].endswith(b'ArrayList'):
                        # http://javasourcecode.org/html/open-source/jdk/jdk-6u23/java/util/ArrayList.java.html
                        assert len(block) == 4, h(block)
                        obj['data'] = []
                        for i in range(obj[b'size']):
                            obj['data'].append(parse_obj())
                    else:
                        assert False, cls['_name']
                    b = f.read(1)
                assert b == b'\x78', h(b) + ' ' + repr(f.read(30))  # TC_ENDBLOCKDATA
        handles[handle] = ('py', obj)
        return obj

    objs = []
    while 1:
        try:
            objs.append(parse_obj())
        except StopIteration:
            return objs


def params_to_name(base_name, params, dataset_parameters, output_folder=True):
    params = dict(params)
    params.pop("fold")
    params.pop("restart")
    dataset_params = ", ".join([f"{key}: {json.dumps(params[key])}" for key, value in dataset_parameters.items() if
                                value['type'] == 'dataset' and key in params])
    learning_params = ", ".join([f"{key}: {json.dumps(params[key])}" for key, value in dataset_parameters.items() if
                                 value['type'] == 'learning' and key in params])

    out = f"{base_name} <{dataset_params}>"
    if output_folder:
        out += f" ({learning_params})"
    if 'run_id' in params:
        out += f" [{params['run_id']}]"
    return out


class OldExampleFactory:
    def __init__(self):
        self.examples = []
        self.static_facts = []

    def add_ex(self, predicates, target_value):
        self.examples.append((target_value, predicates))

    def get_str(self):
        return "\n".join(
            [f"{target_value} {','.join(predicates+self.static_facts)}." for target_value, predicates in self.examples])

    def save(self, path, name="examples.pl"):
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, name), "w") as f:
            f.write(self.get_str())


class ExampleFactory:
    def __init__(self):
        self.examples = []
        self.static_facts = []

    def add_ex(self, evidence, query, target_value):
        self.examples.append((target_value, query, evidence))

    def get_str(self):
        return "\n".join([f"{target_value} {target_predicate} :- {','.join(predicates+self.static_facts)}." for
                          target_value, target_predicate, predicates in self.examples])

    def save(self, path, name="examples.pl"):
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, name), "w") as f:
            f.write(self.get_str())


def _task_dimensions(output_folder):
    settings = json.load(open(os.path.join(output_folder, "settings.json")))
    dimensions = [hv.Dimension("Epoch", range=(0, settings["learningSteps"])),
                  hv.Dimension("Restart", range=(0, settings["restartCount"] - 1)),
                  hv.Dimension("Fold", range=(0, settings["folds"] - 1))]
    return dimensions


def _svg_from_dot(dot_file: str):
    image_file = re.sub(".dot$", ".svg", dot_file)
    subprocess.run(["dot", "-Tsvg", dot_file, "-o", image_file])
    # Workaround for normal size
    svg_data = open(image_file, "r").read()
    svg_data = re.sub('<svg width="[0-9]+pt" height="[0-9]+pt"', '<svg width="100%" height="100%"', svg_data)
    return svg_data