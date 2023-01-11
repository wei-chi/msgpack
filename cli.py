import click
import json
from msgpack import Converter


@click.command()
@click.option('--action', help='pack / parse')
@click.argument('data', required=True)
def run_msgpack(action, data):
    if action == 'pack':
        click.echo(Converter.to_msgpack(data))
    if action == 'parse':
        click.echo(json.dumps(Converter.to_json(data)))


if __name__ == '__main__':
    run_msgpack()