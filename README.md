# Concatenate CellProfiler Analyst training sets


List tables in a database file
```
python  sqlite_list_db.py DefaultDB.db
```

List contents of a table
```
python sqlite_list_table.py DefaultDB.db MyExpt_Per_Object
```

Combine databases and training sets
```
python pandas_combine_training_sets.py --db-paths 'data/Default*db' --training-set-paths 'data/MyTrainingSet*csv' combined_database.db combined_training_set.csv

```
