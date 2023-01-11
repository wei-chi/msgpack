import json, struct


class MessagePack:

    def null_to_hex(self):
        return 'c0'

    def bool_to_hex(self, b: bool):
        return 'c3' if b else 'c2'

    def str_to_hex(self, s: str):
        if len(s) <= 15:
            result = f'a{len(s):x}'
        elif len(s) <= 31:
            result = f'b{len(s)-16:x}'
        elif len(s) < 2**8:
            result = f'd9{len(s):02x}'
        elif len(s) < 2**16:
            result = f'da{len(s):04x}'
        elif len(s) < 2**32:
            result = f'db{len(s):08x}'
        else:
            raise NotImplementedError
        chars = []
        for character in s:
            chars.append(hex(ord(character))[-2:])
        data = ''.join(chars)
        return result + data

    def int_to_hex(self, i: int):
        # positive
        if i >= 0 and i < 2**7:  # [0, 127]
            result = f'{i:02x}'
        elif i >= 2**7 and i < 2**8:  # [128, 255]
            result = f'cc{i:02x}'
        elif i >= 2**8 and i < 2**16:  # [256, 65535]
            result = f'cd{i:04x}'
        elif i >= 2**16 and i < 2**32:  # [65536, 4294967295]
            result = f'ce{i:08x}'
        elif i >= 2**32:  # [4294967296,]
            result = f'cf{i:016x}'
        # negative
        elif i < 0 and i >= -2**4:  # [-16, -1]
            result = f'f{i+2**4:x}'
        elif i < -2**4 and i >= -2**5:  # [-32, -17]
            result = f'e{i+2**5:x}'
        elif i < -2**5 and i > -2**7:  # [-127, -33]
            result = f'd0{i+2**8:02x}'
        elif i <= -2**7 and i > -2**15:  # [-32767, -128]
            result = f'd1{i+2**16:04x}'
        elif i <= -2**15 and i > -2**31:  # [-2147483647, -32768]
            result = f'd2{i+2**32:08x}'
        elif i <= -2**31 and i > -2**63:  # [, -2147483648]
            result = f'd3{i+2**64:016x}'
        else:
            raise NotImplementedError
        return result

    def float_to_hex(self, f: float):
        hex_str = struct.pack('d', f).hex()
        return 'cb' + ''.join(reversed([hex_str[i:i + 2] for i in range(0, len(hex_str), 2)]))

    def list_to_hex(self, l: list):
        if len(l) < 2**4:
            result = f'9{len(l):x}'
        elif len(l) < 2**16:
            result = f'dc{len(l):04x}'
        elif len(l) < 2**32:
            result = f'dd{len(l):08x}'
        else:
            raise NotImplementedError
        hex_list = []
        for element in l:
            hex_list.append(self.convert(element))
        data = ''.join(hex_list)
        return result + data

    def dict_to_hex(self, d: dict):
        if len(d) < 2**4:
            result = f'8{len(d):x}'
        elif len(d) < 2**16:
            result = f'de{len(d):04x}'
        elif len(d) < 2**32:
            result = f'df{len(d):08x}'
        else:
            raise NotImplementedError
        hex_list = []
        for key, value in d.items():
            hex_list.append(self.str_to_hex(key))
            hex_list.append(self.convert(value))
        data = ''.join(hex_list)
        return result + data

    def convert(self, data):
        if data is None:
            return self.null_to_hex()
        elif isinstance(data, bool):
            return self.bool_to_hex(data)
        elif isinstance(data, str):
            return self.str_to_hex(data)
        elif isinstance(data, int):
            return self.int_to_hex(data)
        elif isinstance(data, float):
            return self.float_to_hex(data)
        elif isinstance(data, list):
            return self.list_to_hex(data)
        elif isinstance(data, dict):
            return self.dict_to_hex(data)
        else:
            raise NotImplementedError


class Parser:

    def parse(self, hex_str: str):
        prefix = hex_str[:2]
        if hex_str[0] in '01234567':  # positive fixint
            value = int(hex_str[:2], 16)
            return value, hex_str[2:]

        elif hex_str[0] == '8':  # map
            d = {}
            dict_size = int(hex_str[1], 16)
            current_size = 0
            hex_str = hex_str[2:]
            while current_size < dict_size:
                # key
                key, hex_str = self.parse(hex_str)
                # value
                value, hex_str = self.parse(hex_str)
                d[key] = value
                current_size += 1
            return d, hex_str

        elif hex_str[0] == '9':  # array
            l = []
            list_size = int(hex_str[1], 16)
            current_size = 0
            hex_str = hex_str[2:]
            while current_size < list_size:
                value, hex_str = self.parse(hex_str)
                l.append(value)
                current_size += 1
            return l, hex_str

        elif hex_str[0] == 'a':  # str
            str_size = int(hex_str[1], 16)
            str_value = hex_str[2:str_size * 2 + 2]
            s = ''
            for i in range(0, str_size * 2, 2):
                s += chr(int(str_value[i:i + 2], 16))
            hex_str = hex_str[str_size * 2 + 2:]
            return s, hex_str

        elif hex_str[0] == 'b':  # str
            str_size = int(hex_str[1], 16) + 16
            str_value = hex_str[2:str_size * 2 + 2]
            s = ''
            for i in range(0, str_size * 2, 2):
                s += chr(int(str_value[i:i + 2], 16))
            hex_str = hex_str[str_size * 2 + 2:]
            return s, hex_str

        elif prefix == 'c0':
            return None, hex_str[2:]
        elif prefix == 'c2':
            return False, hex_str[2:]
        elif prefix == 'c3':
            return True, hex_str[2:]

        elif prefix == 'ca':  # float 32
            buffer = ''.join(reversed([hex_str[i:i + 2] for i in range(2, 10, 2)]))
            value = struct.unpack('f', bytes.fromhex(buffer))[0]
            return value, hex_str[10:]
        elif prefix == 'cb':  # float 64
            buffer = ''.join(reversed([hex_str[i:i + 2] for i in range(2, 18, 2)]))
            value = struct.unpack('d', bytes.fromhex(buffer))[0]
            return value, hex_str[18:]

        elif prefix == 'cc':  # uint 8
            value = int(hex_str[2:4], 16)
            return value, hex_str[4:]
        elif prefix == 'cd':  # uint 16
            value = int(hex_str[2:6], 16)
            return value, hex_str[6:]
        elif prefix == 'ce':  # uint 32
            value = int(hex_str[2:10], 16)
            return value, hex_str[10:]
        elif prefix == 'cf':  # uint 64
            value = int(hex_str[2:18], 16)
            return value, hex_str[18:]

        elif prefix == 'd0':  # int 8
            value = int(hex_str[2:4], 16) - 2**8
            return value, hex_str[4:]
        elif prefix == 'd1':  # int 16
            value = int(hex_str[2:6], 16) - 2**16
            return value, hex_str[6:]
        elif prefix == 'd2':  # int 32
            value = int(hex_str[2:10], 16) - 2**32
            return value, hex_str[10:]
        elif prefix == 'd3':  # int 64
            value = int(hex_str[2:18], 16) - 2**64
            return value, hex_str[18:]

        elif prefix == 'd9':  # str 8
            str_size = int(hex_str[2:4], 16)
            str_value = hex_str[4:str_size * 2 + 4]
            s = ''
            for i in range(0, str_size * 2, 2):
                s += chr(int(str_value[i:i + 2], 16))
            hex_str = hex_str[str_size * 2 + 4:]
            return s, hex_str

        elif prefix == 'da':  # str 16
            str_size = int(hex_str[2:6], 16)
            str_value = hex_str[6:str_size * 2 + 6]
            s = ''
            for i in range(0, str_size * 2, 2):
                s += chr(int(str_value[i:i + 2], 16))
            hex_str = hex_str[str_size * 2 + 6:]
            return s, hex_str

        elif prefix == 'db':  # str 32
            str_size = int(hex_str[2:10], 16)
            str_value = hex_str[10:str_size * 2 + 10]
            s = ''
            for i in range(0, str_size * 2, 2):
                s += chr(int(str_value[i:i + 2], 16))
            hex_str = hex_str[str_size * 2 + 10:]
            return s, hex_str

        elif prefix == 'dc':  # array 16
            l = []
            list_size = int(hex_str[2:6], 16)
            current_size = 0
            hex_str = hex_str[6:]
            while current_size < list_size:
                value, hex_str = self.parse(hex_str)
                l.append(value)
                current_size += 1
            return l, hex_str

        elif prefix == 'dd':  # array 32
            l = []
            list_size = int(hex_str[2:10], 16)
            current_size = 0
            hex_str = hex_str[10:]
            while current_size < list_size:
                value, hex_str = self.parse(hex_str)
                l.append(value)
                current_size += 1
            return l, hex_str

        elif prefix == 'de':  # map 16
            d = {}
            dict_size = int(hex_str[2:6], 16)
            current_size = 0
            hex_str = hex_str[6:]
            while current_size < dict_size:
                # key
                key, hex_str = self.parse(hex_str)
                # value
                value, hex_str = self.parse(hex_str)
                d[key] = value
                current_size += 1
            return d, hex_str

        elif prefix == 'df':  # map 32
            d = {}
            dict_size = int(hex_str[2:10], 16)
            current_size = 0
            hex_str = hex_str[10:]
            while current_size < dict_size:
                # key
                key, hex_str = self.parse(hex_str)
                # value
                value, hex_str = self.parse(hex_str)
                d[key] = value
                current_size += 1
            return d, hex_str

        elif hex_str[0] == 'f':  # negative int
            value = int(hex_str[1], 16) - 2**4
            return value, hex_str[2:]
        elif hex_str[0] == 'e':  # negative int
            value = int(hex_str[1], 16) - 2**5
            return value, hex_str[2:]

        else:
            raise Exception('invalid hex string')


class Converter:

    @staticmethod
    def to_msgpack(input: str):
        msgpack = MessagePack()
        if input is None:
            return msgpack.null_to_hex(input)
        data = json.loads(input)
        return msgpack.convert(data)

    @staticmethod
    def to_json(input: str):
        parser = Parser()
        result, hex_str = parser.parse(input)
        if hex_str:
            raise Exception('invalid hex string')
        return result