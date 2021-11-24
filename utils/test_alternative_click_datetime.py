
from datetime import date

import click


#https://www.markhneedham.com/blog/2019/07/29/python-click-date-parameter-type/
#https://www.programcreek.com/python/?code=liiight%2Fnotifiers%2Fnotifiers-master%2Fnotifiers_cli%2Futils%2Fdynamic_click.py

@click.command()
@click.option('--date-start', type=click.DateTime(formats=["%Y-%m-%d"]),
              default=str(date.today()))
@click.option('--date-end', type=click.DateTime(formats=["%Y-%m-%d"]),
              default=str(date.today()))
def dummy(date_start, date_end):
    date_start = date_start.date()
    date_end = date_end.date()
    click.echo(f"Start: {date_start}, End: {date_end} ")
    
    
cli.add_command(dummy)

if __name__ == '__main__':
    cli()
    
def json_schema_to_click_type(schema: dict) -> tuple:
    """
    A generic handler of a single property JSON schema to :class:`click.ParamType` converter

    :param schema: JSON schema property to operate on
    :return: Tuple of :class:`click.ParamType`, `description`` of option and optionally a :class:`click.Choice`
     if the allowed values are a closed list (JSON schema ``enum``)
    """
    choices = None
    if isinstance(schema["type"], list):
        if "string" in schema["type"]:
            schema["type"] = "string"
    click_type = SCHEMA_BASE_MAP[schema["type"]]
    description = schema.get("title")
    if schema.get("enum"):
        # todo handle multi type enums better (or at all)
        enum = [value for value in schema["enum"] if isinstance(value, str)]
        choices = click.Choice(enum)
    return click_type, description, choices 
