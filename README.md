# MessagePack converter
The converter is used to convert JSON string to MessagePack format, and convert MessagePack back to JSON.

## Usage

### JSON to MessagePack
Covert the JSON string `{"compact":true,"schema":0}`
```sh
python cli.py --action pack '{\"compact\":true,\"schema\":0}'
```
The result shows in stdout `82a7636f6d70616374c3a6736368656d6100`

### MessagePack to JSON
Convert the MessagePack `82a7636f6d70616374c3a6736368656d6100`
```sh
python cli.py --action parse '82a7636f6d70616374c3a6736368656d6100'
```
The result shows in stdout `{"compact":true,"schema":0}`

## Test
Run the test cases
```sh
pytest test_msgpack.py
```