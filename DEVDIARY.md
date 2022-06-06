# Development diary

`dbify` = Turning a nested JSON file into a flat JSON database.

Consider the following JSON data.

    my_json_file.json:
    {
        "contents": {
            "version": 1,
            "authors": ["me", "the guys"],
            "tests passed": {
                "1.2": "failed",
                "1.0": "pass",
                "0.9": "pass"
            },
            "first_chapter": {
                "blob_of_data": "values"
            },
            "second_chapter": {
                "blob_of_data": "values",
                "addendum_to_blob": "values"
            }
    
        }
    }

**Nested JSON objects can be replaced by foreign keys to export nested JSON
objects to their own JSON file.**

Let's have a look at the `"contents"` JSON object in `my_json_file.json` for
example.

    my_json_file.json:
    {
        "contents": "contents_table.json"
    }
    contents_table.json:
     {
        "version": 1,
        "authors": ["me", "the guys"],
        "tests passed": "tests_passed_table.json",
        "first_chapter": "first_chapter_table.json",
        "second_chapter": "second_chapter_table.json"
    }

`"contents"` in the original JSON is replaced as a foreign key
by `"contents_table.json"`. There is still a problem with
names collisions.

A new file called `contents_table.json` is created containing the rest of the
information.

**The new files will be called as the respective foreign keys.**

**In order to avoid name collisions, `_table_$id.json` is appended at the end of
the file names instead of just
`_table.json`. $id should be a unique, incremental ID.**

The result might look something like this:

    my_json_file.json:
    {
        "contents": "contents_table_1.json"
    }
    contents_table_1.json:
     {
        "version": 1,
        "authors": ["me", "the guys"],
        "tests passed": "tests_passed_table_2.json",
        "first_chapter": "first_chapter_table_3.json",
        "second_chapter": "second_chapter_table_4.json"
    }
    "tests_passed_table_2.json":
    {
        "1.2": "failed",
        "1.0": "pass",
        "0.9": "pass"
    }
    "first_chapter_table_3.json":
    {
        "blob_of_data": "values",
        "testing": "testing_table_5.json"
    }
    "second_chapter_table_4.json":
    {
        "blob_of_data": "values",
        "addendum_to_blob": "values",
        "testing": "testing_table_6.json"
    }
    "testing_table_5.json":
    {
        "foo": "bar"
    }
    "testing_table_6.json":
    {
        "foo": "bar"
    }

The **problem** with this is that **multiple files on filesystem have worse
performance than a single JSON file
with all the tables in it**.

The solution to store all the tables in a single JSON file poses a new
challenge: how to store each table as a pair
of table name and table contents?

A first idea is to create a list of pairs, and to call the first table "root".

The end result would look like this:

    my_json_file_dbfied.json:
    [
        [
            "root",
            {
                "contents": "contents_table_1.json"
            }
        ],
        [
            "contents_table_1.json",
             {
                "version": 1,
                "authors": ["me", "the guys"],
                "tests passed": "tests_passed_table_2.json",
                "first_chapter": "first_chapter_table_3.json",
                "second_chapter": "second_chapter_table_4.json"
            }
        ],
        [
            "tests_passed_table_2.json",
            {
                "1.2": "failed",
                "1.0": "pass",
                "0.9": "pass"
            }
        ],
        [
            "first_chapter_table_3.json",
            {
                "blob_of_data": "values",
                "testing": "testing_table_5.json"
            }
        ],
        [
            "second_chapter_table_4.json",
            {
                "blob_of_data": "values",
                "addendum_to_blob": "values",
                "testing": "testing_table_6.json"
            }
        ],
        ["
            testing_table_5.json",
            {
                "foo": "bar"
            }
        ],
        [
            "testing_table_6.json",
            {
                "foo": "bar"
            }
        ]
    ]

