import click
import os
import pandas as pd
import shutil
import sqlite3

def get_number_of_images(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM MyExpt_Per_Image")
    number_of_images = cursor.fetchone()[0]
    conn.close()
    return number_of_images

def get_column_names(cursor, table_name):
    #conn = sqlite3.connect(db_path)
    #cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    #conn.close()
    return column_names

def combine_training_sets(training_set_paths, image_counts, output_training_set_path):
    combined_df = pd.DataFrame()
    current_image_offset = 0

    for i, training_set_path in enumerate(training_set_paths):
        df = pd.read_csv(training_set_path)
        
        # Adjust ImageNumber based on the current offset
        df['ImageNumber'] += current_image_offset
        
        # Update the current image offset
        current_image_offset += image_counts[i]
        
        # Append to the combined DataFrame
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    
    # Save the combined DataFrame to a new CSV file
    combined_df.to_csv(output_training_set_path, index=False)

def combine_databases(db_paths, image_counts, output_db_path):
    if os.path.exists(output_db_path):
        os.remove(output_db_path)
    shutil.copyfile(db_paths[0], output_db_path)
    
    conn_output = sqlite3.connect(output_db_path)
    cursor_output = conn_output.cursor()
    
    current_image_offset = image_counts[0]

    for i, db_path in enumerate(db_paths[1:], start=1):
        # Make a writable copy of the database
        temp_db_path = f"temp_{i}.db"
        shutil.copyfile(db_path, temp_db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Adjust ImageNumber in MyExpt_Per_Object
        cursor.execute(f"UPDATE MyExpt_Per_Object SET ImageNumber = ImageNumber + ?", (current_image_offset,))
        
        # Adjust ImageNumber in MyExpt_Per_Image
        cursor.execute(f"UPDATE MyExpt_Per_Image SET ImageNumber = ImageNumber + ?", (current_image_offset,))
        
        # Get column names for MyExpt_Per_Object and MyExpt_Per_Image
        per_object_columns = get_column_names(cursor, 'MyExpt_Per_Object')
        per_image_columns = get_column_names(cursor, 'MyExpt_Per_Image')
        
        # Copy data to the output database
        cursor.execute("SELECT * FROM MyExpt_Per_Object")
        rows = cursor.fetchall()
        placeholders = ', '.join(['?'] * len(per_object_columns))
        insert_query = f"INSERT INTO MyExpt_Per_Object ({', '.join(per_object_columns)}) VALUES ({placeholders})"
        cursor_output.executemany(insert_query, rows)
        
        cursor.execute("SELECT * FROM MyExpt_Per_Image")
        rows = cursor.fetchall()
        placeholders = ', '.join(['?'] * len(per_image_columns))
        insert_query = f"INSERT INTO MyExpt_Per_Image ({', '.join(per_image_columns)}) VALUES ({placeholders})"
        cursor_output.executemany(insert_query, rows)
        
        conn.close()
        
        # Update the offset
        current_image_offset += image_counts[i]
    
    conn_output.commit()
    conn_output.close()

@click.command()
@click.option('--db-paths', required=True, help='Comma-separated list of database paths.')
@click.option('--training-set-paths', required=True, help='Comma-separated list of training set paths.')
@click.argument('output_db_path', type=click.Path())
@click.argument('output_training_set_path', type=click.Path())
def cli(db_paths, training_set_paths, output_db_path, output_training_set_path):
    """Combine multiple SQLite databases and training set CSV files."""
    db_paths = db_paths.split(',')
    training_set_paths = training_set_paths.split(',')
    image_counts = [get_number_of_images(db_path) for db_path in db_paths]
    combine_training_sets(training_set_paths, image_counts, output_training_set_path)
    combine_databases(db_paths, image_counts, output_db_path)

if __name__ == '__main__':
    cli()


