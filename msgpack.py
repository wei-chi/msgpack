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

    @staticmethod
    def to_msgpack(input: str):
        msgpack = MessagePack()
        if input is None:
            return msgpack.null_to_hex(input)
        data = json.loads(input)
        return msgpack.convert(data)