import sqlite3
import click

def list_table_contents(db_path, table_name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get the contents of the table
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Get the column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        # Print the column names
        click.echo(', '.join(column_names))
        
        # Print the rows
        for row in rows:
            click.echo(', '.join(map(str, row)))
        
        conn.close()
    except sqlite3.Error as e:
        click.echo(f"Error: {e}")

@click.command()
@click.argument('db_path', type=click.Path(exists=True))
@click.argument('table_name')
def cli(db_path, table_name):
    """List the contents of a specific table in an SQLite database."""
    list_table_contents(db_path, table_name)

if __name__ == '__main__':
    cli()
