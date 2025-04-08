import sqlite3
import click

def inspect_db_structure(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get the list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        click.echo(f"Database: {db_path}")
        for table in tables:
            table_name = table[0]
            click.echo(f"\nTable: {table_name}")
            
            # Get the schema of the table
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for column in columns:
                click.echo(f"Column: {column[1]}, Type: {column[2]}")
        
        conn.close()
    except sqlite3.Error as e:
        click.echo(f"Error: {e}")

@click.command()
@click.argument('db_path', type=click.Path(exists=True))
def cli(db_path):
    """Inspect the structure of an SQLite database."""
    inspect_db_structure(db_path)

if __name__ == '__main__':
    cli()
