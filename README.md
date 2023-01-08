# MessagePack converter
The converter is used to convert JSON string to MessagePack format.

## Usage
Covert the JSON string `{"compact":true,"schema":0}`
```sh
python cli.py '{\"compact\":true,\"schema\":0}'
```
The result shows in stdout `82a7636f6d70616374c3a6736368656d6100`

## Test
Run the test cases
```sh
pytest test_msgpack.py
```