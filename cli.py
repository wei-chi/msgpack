import click
from msgpack import MessagePack


@click.command()
@click.argument('json', required=True)
def run_msgpack(json):
    click.echo(MessagePack.to_msgpack(json))


if __name__ == '__main__':
    run_msgpack()