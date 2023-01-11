from msgpack import Converter, MessagePack, Parser


def test_null_to_hex():
    msgpack = MessagePack()
    assert msgpack.null_to_hex() == 'c0'


def test_bool_to_hex():
    msgpack = MessagePack()
    assert msgpack.bool_to_hex(False) == 'c2'
    assert msgpack.bool_to_hex(True) == 'c3'


def test_str_to_hex():
    msgpack = MessagePack()
    assert msgpack.str_to_hex('a') == 'a161'
    assert msgpack.str_to_hex('aa') == 'a26161'
    assert msgpack.str_to_hex('a' * 15) == 'af' + '61' * 15
    assert msgpack.str_to_hex('a' * 16) == 'b0' + '61' * 16
    assert msgpack.str_to_hex('a' * 31) == 'bf' + '61' * 31
    assert msgpack.str_to_hex('a' * 32) == 'd920' + '61' * 32
    assert msgpack.str_to_hex('a' * 255) == 'd9ff' + '61' * 255
    assert msgpack.str_to_hex('a' * 256) == 'da0100' + '61' * 256
    assert msgpack.str_to_hex('a' * 65535) == 'daffff' + '61' * 65535
    assert msgpack.str_to_hex('a' * 65536) == 'db00010000' + '61' * 65536


def test_int_to_hex():
    msgpack = MessagePack()
    assert msgpack.int_to_hex(0) == '00'
    assert msgpack.int_to_hex(1) == '01'
    assert msgpack.int_to_hex(127) == '7f'
    assert msgpack.int_to_hex(128) == 'cc80'
    assert msgpack.int_to_hex(255) == 'ccff'
    assert msgpack.int_to_hex(256) == 'cd0100'
    assert msgpack.int_to_hex(65535) == 'cdffff'
    assert msgpack.int_to_hex(65536) == 'ce00010000'
    assert msgpack.int_to_hex(4294967295) == 'ceffffffff'
    assert msgpack.int_to_hex(4294967296) == 'cf0000000100000000'

    assert msgpack.int_to_hex(-1) == 'ff'
    assert msgpack.int_to_hex(-16) == 'f0'
    assert msgpack.int_to_hex(-17) == 'ef'
    assert msgpack.int_to_hex(-32) == 'e0'
    assert msgpack.int_to_hex(-33) == 'd0df'
    assert msgpack.int_to_hex(-127) == 'd081'
    assert msgpack.int_to_hex(-128) == 'd1ff80'
    assert msgpack.int_to_hex(-32767) == 'd18001'
    assert msgpack.int_to_hex(-32768) == 'd2ffff8000'
    assert msgpack.int_to_hex(-2147483647) == 'd280000001'
    assert msgpack.int_to_hex(-2147483648) == 'd3ffffffff80000000'


def test_float_to_hex():
    msgpack = MessagePack()
    assert msgpack.float_to_hex(0.1) == 'cb3fb999999999999a'
    assert msgpack.float_to_hex(0.5) == 'cb3fe0000000000000'


def test_list_to_hex():
    msgpack = MessagePack()
    assert msgpack.list_to_hex([1, 2, 3]) == '93010203'
    assert msgpack.list_to_hex(['a', 'b']) == '92a161a162'
    assert msgpack.list_to_hex([1, 2, [3, 4]]) == '930102920304'
    assert msgpack.list_to_hex([1] * 16) == 'dc0010' + '01' * 16
    assert msgpack.list_to_hex([1] * 2**16) == 'dd00010000' + '01' * 2**16


def test_dict_to_hex():
    msgpack = MessagePack()
    assert msgpack.dict_to_hex({'a': 1}) == '81a16101'
    assert msgpack.dict_to_hex({
        'a': 1,
        'b': 2,
        'c': 3,
        'd': 4,
        'e': 5,
        'f': 6,
        'g': 7,
        'h': 8,
        'i': 9,
        'j': 10,
        'k': 11,
        'l': 12,
        'm': 13,
        'n': 14,
        'o': 15,
        'p': 16
    }) == 'de0010a16101a16202a16303a16404a16505a16606a16707a16808a16909a16a0aa16b0ba16c0ca16d0da16e0ea16f0fa17010'


def test_msgpack():
    input = '{"a":10, "b":20, "c":30}'
    result = Converter.to_msgpack(input)
    assert result == '83a1610aa16214a1631e'

    input = '{"employees": ["John", "Anna", "Peter"]}'
    result = Converter.to_msgpack(input)
    assert result == '81a9656d706c6f7965657393a44a6f686ea4416e6e61a55065746572'

    input = '[{"name":"Ram", "age":20}, {"name":"Bob", "age":30}]'
    result = Converter.to_msgpack(input)
    assert result == '9282a46e616d65a352616da36167651482a46e616d65a3426f62a36167651e'

    input = '{"x":0.1, "y":-2.3, "z":3.5}'
    result = Converter.to_msgpack(input)
    assert result == '83a178cb3fb999999999999aa179cbc002666666666666a17acb400c000000000000'

    input = '''
    {
        "id": "0001",
        "type": "donut",
        "name": "Cake",
        "image":
            {
                "url": "images/0001.jpg",
                "width": 200,
                "height": 200
            },
        "thumbnail":
            {
                "url": "images/thumbnails/0001.jpg",
                "width": 32,
                "height": 32
            }
    }
    '''
    result = Converter.to_msgpack(input)
    assert result == '85a26964a430303031a474797065a5646f6e7574a46e616d65a443616b65a5696d61676583a375726caf696d616765732f303030312e6a7067a57769647468ccc8a6686569676874ccc8a97468756d626e61696c83a375726cba696d616765732f7468756d626e61696c732f303030312e6a7067a5776964746820a668656967687420'


def test_msgpack_parser():
    parser = Parser()
    assert parser.parse('c0') == (None, '')
    assert parser.parse('c2') == (False, '')
    assert parser.parse('c3') == (True, '')

    # str
    assert parser.parse('a161') == ('a', '')
    assert parser.parse('a26161') == ('aa', '')
    assert parser.parse('af' + '61' * 15) == ('a' * 15, '')
    assert parser.parse('b0' + '61' * 16) == ('a' * 16, '')
    assert parser.parse('bf' + '61' * 31) == ('a' * 31, '')
    assert parser.parse('d920' + '61' * 32) == ('a' * 32, '')
    assert parser.parse('d9ff' + '61' * 255) == ('a' * 255, '')
    assert parser.parse('da0100' + '61' * 256) == ('a' * 256, '')
    assert parser.parse('daffff' + '61' * 65535) == ('a' * 65535, '')
    assert parser.parse('db00010000' + '61' * 65536) == ('a' * 65536, '')

    # int
    assert parser.parse('00') == (0, '')
    assert parser.parse('01') == (1, '')
    assert parser.parse('7f') == (127, '')
    assert parser.parse('cc80') == (128, '')
    assert parser.parse('ccff') == (255, '')
    assert parser.parse('cd0100') == (256, '')
    assert parser.parse('cdffff') == (65535, '')
    assert parser.parse('ce00010000') == (65536, '')
    assert parser.parse('ceffffffff') == (4294967295, '')
    assert parser.parse('cf0000000100000000') == (4294967296, '')

    assert parser.parse('ff') == (-1, '')
    assert parser.parse('f0') == (-16, '')
    assert parser.parse('ef') == (-17, '')
    assert parser.parse('e0') == (-32, '')
    assert parser.parse('d0df') == (-33, '')
    assert parser.parse('d081') == (-127, '')
    assert parser.parse('d1ff80') == (-128, '')
    assert parser.parse('d18001') == (-32767, '')
    assert parser.parse('d2ffff8000') == (-32768, '')
    assert parser.parse('d280000001') == (-2147483647, '')
    assert parser.parse('d3ffffffff80000000') == (-2147483648, '')

    # float
    assert parser.parse('cb3fb999999999999a') == (0.1, '')
    assert parser.parse('cb3fe0000000000000') == (0.5, '')

    # list
    assert parser.parse('93010203') == ([1, 2, 3], '')
    assert parser.parse('92a161a162') == (['a', 'b'], '')
    assert parser.parse('930102920304') == ([1, 2, [3, 4]], '')
    assert parser.parse('dc0010' + '01' * 16) == ([1] * 16, '')
    assert parser.parse('dd00010000' + '01' * 2**16) == ([1] * 2**16, '')

    # dict
    assert parser.parse('81a16101') == ({'a': 1}, '')
    assert parser.parse(
        'de0010a16101a16202a16303a16404a16505a16606a16707a16808a16909a16a0aa16b0ba16c0ca16d0da16e0ea16f0fa17010') == ({
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4,
            'e': 5,
            'f': 6,
            'g': 7,
            'h': 8,
            'i': 9,
            'j': 10,
            'k': 11,
            'l': 12,
            'm': 13,
            'n': 14,
            'o': 15,
            'p': 16
        }, '')


def test_msgpack_to_json():
    input = '83a1610aa16214a1631e'
    result = Converter.to_json(input)
    assert result == {"a": 10, "b": 20, "c": 30}

    input = '81a9656d706c6f7965657393a44a6f686ea4416e6e61a55065746572'
    result = Converter.to_json(input)
    assert result == {"employees": ["John", "Anna", "Peter"]}

    input = '9282a46e616d65a352616da36167651482a46e616d65a3426f62a36167651e'
    result = Converter.to_json(input)
    assert result == [{"name": "Ram", "age": 20}, {"name": "Bob", "age": 30}]

    input = '83a178cb3fb999999999999aa179cbc002666666666666a17acb400c000000000000'
    result = Converter.to_json(input)
    assert result == {"x": 0.1, "y": -2.3, "z": 3.5}

    input = '85a26964a430303031a474797065a5646f6e7574a46e616d65a443616b65a5696d61676583a375726caf696d616765732f303030312e6a7067a57769647468ccc8a6686569676874ccc8a97468756d626e61696c83a375726cba696d616765732f7468756d626e61696c732f303030312e6a7067a5776964746820a668656967687420'
    result = Converter.to_json(input)
    assert result == {
        "id": "0001",
        "type": "donut",
        "name": "Cake",
        "image": {
            "url": "images/0001.jpg",
            "width": 200,
            "height": 200
        },
        "thumbnail": {
            "url": "images/thumbnails/0001.jpg",
            "width": 32,
            "height": 32
        }
    }