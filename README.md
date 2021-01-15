# GLAMORISE
GLAMORISE (GeneraL Aggregation MOdule using a RelatIonal databaSE)  

This project refers to the implementation of GLAMORISE Natural Language Interface to Databases (NLIDB). You can find out more about GLAMORISE in the following article:

* [A Novel Solution for the Aggregation Problem in Natural Language Interface to Databases (NLIDB)](./paper/207509_1-A-Novel-Solution-for-the-Aggregation-Problem-in-Natural-Language-Interface-to-Databases-NLIDB.pdf). Novello, A., F.; and Casanova, M., A. Proc. XXXV Brazilian Symposium on Databases - SBBD. 2020. Awarded as the 2nd Best Short Paper.

This implementation of GLAMORISE uses NaLIR as one of its integtared NLIDBs, so you will have to clone the [nalir-glamorise](https://github.com/novello/nalir-glamorise) repository. This project is a customization of the [nalir-ssbd](https://github.com/pr3martins/nalir-sbbd) project which in turn is a Python port of the original [NaLIR project](https://github.com/umich-dbgroup/NaLIR). Please follow all the steps described in the README of the nalir-glamorise project.

The paths below are relative to the root path of the GLAMORISE project. You are expected to be positioned on this path.


## Setting up the environment

``` bash
  $ pip install -r requirements.txt
```


## Setting up the database
### ANP SQLite database

Used with the Mock NLIDB (for testing purposes) which uses an ANP (Agência Nacional de Petróleo - Brazilian Petroleum Agency) SQLite database.

``` bash
  $sqlite3 ./datasets/mock_nlidb_anp.db < ./config/mock_nlidb_anp_sqlite.sql
```


### ANP MySQL database

Used with the NaLIR NLIDB which uses an ANP (Agência Nacional de Petróleo - Brazilian Petroleum Agency) MySQL database.


``` bash
    $ mysql -D mas -u <user> -p < ./config/nalir_anp_mysql.sql
```


### MAS MySQL database

Used with the NaLIR NLIDB which uses the MAS (Microsoft Academic Search) MySQL database. This database is used in the NaLIR original paper.

First follow all the installation steps in the README of the nalir-glamorise project and then run the command below:


``` bash
    $ mysql -D mas -u <user> -p < ./config/setup_mas_glamorise.sql
```


## Path adjustment

You will have to adjust the relative path of the project nalir-glamorise to the project GLAMORISE in the following file and line:

./nalir_nlidb.py

``` python
    sys.path.append(path.abspath('../nalir-glamorise'))
```

You will have to adjust the absolute path of the project nalir-glamorise and GLAMORISE in the following file and lines:

./web_interface/web_api.py
``` python
  sys.path.append(path.abspath('/home/novello/nalir-glamorise'))
  sys.path.append(path.abspath('/home/novello/GLAMORISE'))
```


## Configuration files


### NaLIR database and special folders configurations

You will have to adjust the JSON files bellow with the correct database connection information and the path under the project nalir-glamorise to the folders zfiles and new_jars


#### ANP database
./config/nalir_anp_local_db.json
``` json
{
    "connection":{
            "host": "localhost",
            "password":"desenvolvimento123",
            "user":"nalir",
            "database":"anp"
    },
    "loggingMode": "ERROR",
    "zfiles_path":"/home/novello/nalir-glamorise/zfiles",
    "jars_path":"/home/novello/nalir-glamorise/jars/new_jars"
}
```


#### MAS database
./config/nalir_mas_local_db.json
``` json
{
    "connection":{
            "host": "localhost",
            "password":"desenvolvimento123",
            "user":"nalir",
            "database":"mas"
    },
    "loggingMode": "ERROR",
    "zfiles_path":"/home/novello/nalir-glamorise/zfiles",
    "jars_path":"/home/novello/nalir-glamorise/jars/new_jars"
}
```


## Test Coverage

If you changed the code and want to test if it broke anything, there is a simple set of tasks covering the Mock NLIDB in ./test_glamorise.py


## Web Interface

To use the project in a convenient way, a web interface was created that can be loaded by running the file ./web_interface/web_api.py


## [OPTIONAL] Configuration files

### GLAMORISE and NaLIR customization of pattern files

If you want to change the patterns accepted by GLAMORISE and NaLIR, this could be achieved modifying the following files below:


#### GLAMORISE Mock ANP

./config/glamorise_mock_anp.json

``` json
{
    "units_of_measurement": [
        "cubic meters"
    ],
    "compound_pattern_dep": [
        {
            "POS": "NOUN",
            "DEP": "compound"
        },
        {
            "POS": "NOUN"
        }
    ],
    "compound_pattern_of": [
        {
            "POS": "NOUN",
            "LOWER": {
                "NOT_IN": [
                    "number"
                ]
            }
        },
        {
            "LOWER": "of",
            "POS": "ADP"
        },
        {
            "POS": "NOUN"
        }
    ],
    "default_pattern": [
        {
            "POS": "ADV",
            "OP": "*"
        },
        {
            "POS": "ADJ",
            "OP": "*"
        },
        {
            "POS": "NOUN",
            "LOWER": {
                "NOT_IN": [
                    "number"
                ]
            }
        }
    ],
    "patterns": {
        "than options": {
            "reserved_words": [
                "more than",
                "greater than",
                "less than",
                "equal to",
                "greater than or equal to",
                "less than or equal to"
            ],
            "pre_having_conditions": [
                ">",
                ">",
                "<",
                "=",
                ">=",
                "<="
            ],
            "specific_pattern": [
                {
                    "LIKE_NUM": true
                },
                {
                    "POS": "ADV",
                    "OP": "*"
                },
                {
                    "POS": "ADJ",
                    "OP": "*"
                },
                {
                    "POS": "NOUN",
                    "OP": "*"
                },
                {
                    "POS": "NOUN"
                }
            ],
            "pre_cut_text": false
        },
        "group by": {
            "reserved_words": [
                "by",
                "per",
                "for each",
                "of each"
            ],
            "pre_group_by": true,
            "pre_cut_text": true
        },
        "group by and": {
            "reserved_words": [
                "by",
                "per",
                "for each",
                "of each"
            ],
            "pre_group_by": true,
            "specific_pattern": [
                {
                    "POS": "ADV",
                    "OP": "*"
                },
                {
                    "POS": "ADJ",
                    "OP": "*"
                },
                {
                    "POS": "NOUN",
                    "LOWER": {
                        "NOT_IN": [
                            "number"
                        ]
                    }
                },
                {
                    "LOWER": "and"
                },
                {
                    "POS": "NOUN",
                    "LOWER": {
                        "NOT_IN": [
                            "number"
                        ]
                    }
                }
            ],
            "pre_cut_text": false
        },
        "how options": {
            "reserved_words": [
                "how many",
                "how much"
            ],
            "pre_aggregation_functions": [
                "count",
                "sum"
            ],
            "pre_cut_text": true
        },
        "other count": {
            "reserved_words": [
                "number of",
                "number of the"
            ],
            "pre_aggregation_functions": "count",
            "pre_cut_text": true
        },
        "other sum": {
            "reserved_words": [
                "total"
            ],
            "pre_aggregation_functions": "sum",
            "pre_cut_text": true
        },
        "average options": {
            "reserved_words": [
                "average",
                "avg",
                "mean"
            ],
            "pre_aggregation_functions": "avg",
            "pre_cut_text": true
        },
        "superlative min": {
            "reserved_words": [
                "least",
                "smallest",
                "tiniest",
                "shortest",
                "cheapest",
                "nearest",
                "lowest",
                "worst",
                "newest",
                "min",
                "minimum"
            ],
            "pre_aggregation_functions": "min",
            "pre_cut_text": true
        },
        "superlative max": {
            "reserved_words": [
                "most",
                "most number of",
                "biggest",
                "longest",
                "furthest",
                "highest",
                "tallest",
                "greatest",
                "best",
                "oldest",
                "max",
                "maximum"
            ],
            "pre_aggregation_functions": "max",
            "pre_cut_text": true
        },
        "time scale options": {
            "reserved_words": [
                "daily",
                "monthly",
                "yearly"
            ],
            "pre_time_scale_replace_text": {
                "daily": "day",
                "monthly": "month",
                "yearly": "year"
            },
            "pre_time_scale_aggregation_functions": "sum",
            "pre_cut_text": false
        }
    }
}
```


#### GLAMORISE with NaLIR (ANP database)

./config/glamorise_nalir_anp.json

``` json
{
    "units_of_measurement": [
        "cubic meters"
    ],
    "compound_pattern_dep": [
        {
            "POS": "NOUN",
            "DEP": "compound"
        },
        {
            "POS": "NOUN"
        }
    ],
    "compound_pattern_of": [
        {
            "POS": "NOUN",
            "LOWER": {
                "NOT_IN": [
                    "number"
                ]
            }
        },
        {
            "LOWER": "of",
            "POS": "ADP"
        },
        {
            "POS": "NOUN"
        }
    ],
    "default_pattern": [
        {
            "POS": "ADV",
            "OP": "*"
        },
        {
            "POS": "ADJ",
            "OP": "*"
        },
        {
            "POS": "NOUN",
            "LOWER": {
                "NOT_IN": [
                    "number"
                ]
            }
        }
    ],
    "nlidb_nlq_translate_fields": false,
    "nlidb_attempt_level": 3,
    "patterns": {
        "than options": {
            "reserved_words": [
                "more than",
                "greater than",
                "less than",
                "equal to",
                "greater than or equal to",
                "less than or equal to"
            ],
            "pre_having_conditions": [
                ">",
                ">",
                "<",
                "=",
                ">=",
                "<="
            ],
            "specific_pattern": [
                {
                    "LIKE_NUM": true
                },
                {
                    "POS": "ADV",
                    "OP": "*"
                },
                {
                    "POS": "ADJ",
                    "OP": "*"
                },
                {
                    "POS": "NOUN",
                    "OP": "*"
                },
                {
                    "POS": "NOUN"
                }
            ],
            "pre_cut_text": false
        },
        "group by": {
            "reserved_words": [
                "by",
                "per",
                "for each",
                "of each"
            ],
            "pre_group_by": true,
            "pre_cut_text": false
        },
        "group by and": {
            "reserved_words": [
                "by",
                "per",
                "for each",
                "of each"
            ],
            "pre_group_by": true,
            "specific_pattern": [
                {
                    "POS": "ADV",
                    "OP": "*"
                },
                {
                    "POS": "ADJ",
                    "OP": "*"
                },
                {
                    "POS": "NOUN",
                    "LOWER": {
                        "NOT_IN": [
                            "number"
                        ]
                    }
                },
                {
                    "LOWER": "and"
                },
                {
                    "POS": "NOUN",
                    "LOWER": {
                        "NOT_IN": [
                            "number"
                        ]
                    }
                }
            ],
            "pre_cut_text": false
        },
        "how options": {
            "reserved_words": [
                "how many",
                "how much"
            ],
            "pre_aggregation_functions": [
                "count",
                "sum"
            ],
            "pre_cut_text": false
        },
        "other count": {
            "reserved_words": [
                "number of",
                "number of the"
            ],
            "pre_aggregation_functions": "count",
            "pre_cut_text": true
        },
        "other sum": {
            "reserved_words": [
                "total"
            ],
            "pre_aggregation_functions": "sum",
            "pre_cut_text": true
        },
        "average options": {
            "reserved_words": [
                "average",
                "avg",
                "mean"
            ],
            "pre_aggregation_functions": "avg",
            "pre_cut_text": true
        },
        "superlative min": {
            "reserved_words": [
                "least",
                "smallest",
                "tiniest",
                "shortest",
                "cheapest",
                "nearest",
                "lowest",
                "worst",
                "newest",
                "min",
                "minimum"
            ],
            "pre_aggregation_functions": "min",
            "pre_cut_text": true
        },
        "superlative max": {
            "reserved_words": [
                "most",
                "most number of",
                "biggest",
                "longest",
                "furthest",
                "highest",
                "tallest",
                "greatest",
                "best",
                "oldest",
                "max",
                "maximum"
            ],
            "pre_aggregation_functions": "max",
            "pre_cut_text": true
        },
        "time scale options": {
            "reserved_words": [
                "daily",
                "monthly",
                "yearly"
            ],
            "pre_time_scale_replace_text": {
                "daily": "day",
                "monthly": "month",
                "yearly": "year"
            },
            "pre_time_scale_aggregation_functions": "sum",
            "pre_cut_text": false
        }
    }
}
```


#### GLAMORISE with NaLIR (MAS database)

./config/glamorise_nalir_mas.json

``` json
{
    "units_of_measurement": [],
    "compound_pattern_dep": [
        {
            "POS": "NOUN",
            "DEP": "compound"
        },
        {
            "POS": "NOUN"
        }
    ],
    "compound_pattern_of": [
        {
            "POS": "NOUN",
            "LOWER": {
                "NOT_IN": [
                    "number"
                ]
            }
        },
        {
            "LOWER": "of",
            "POS": "ADP"
        },
        {
            "POS": "NOUN"
        }
    ],
    "default_pattern": [
        {
            "POS": "ADV",
            "OP": "*"
        },
        {
            "POS": "ADJ",
            "OP": "*"
        },
        {
            "POS": "NOUN",
            "LOWER": {
                "NOT_IN": [
                    "number"
                ]
            }
        }
    ],
    "nlidb_nlq_translate_fields": false,
    "nlidb_attempt_level": 3,
    "patterns": {
        "than options": {
            "reserved_words": [
                "more than",
                "greater than",
                "less than",
                "equal to",
                "greater than or equal to",
                "less than or equal to"
            ],
            "pre_having_conditions": [
                ">",
                ">",
                "<",
                "=",
                ">=",
                "<="
            ],
            "specific_pattern": [
                {
                    "LIKE_NUM": true
                },
                {
                    "POS": "ADV",
                    "OP": "*"
                },
                {
                    "POS": "ADJ",
                    "OP": "*"
                },
                {
                    "POS": "NOUN",
                    "OP": "*"
                },
                {
                    "POS": "NOUN"
                }
            ],
            "pre_cut_text": false
        },
        "group by": {
            "reserved_words": [
                "by",
                "per",
                "for each",
                "of each"
            ],
            "pre_group_by": true,
            "pre_cut_text": false
        },
        "group by and": {
            "reserved_words": [
                "by",
                "per",
                "for each",
                "of each"
            ],
            "pre_group_by": true,
            "specific_pattern": [
                {
                    "POS": "ADV",
                    "OP": "*"
                },
                {
                    "POS": "ADJ",
                    "OP": "*"
                },
                {
                    "POS": "NOUN",
                    "LOWER": {
                        "NOT_IN": [
                            "number"
                        ]
                    }
                },
                {
                    "LOWER": "and"
                },
                {
                    "POS": "NOUN",
                    "LOWER": {
                        "NOT_IN": [
                            "number"
                        ]
                    }
                }
            ],
            "pre_cut_text": false
        },
        "how options": {
            "reserved_words": [
                "how many",
                "how much"
            ],
            "pre_aggregation_functions": [
                "count",
                "sum"
            ],
            "pre_cut_text": true
        },
        "other count": {
            "reserved_words": [
                "number of",
                "number of the"
            ],
            "pre_aggregation_functions": "count",
            "pre_cut_text": true
        },
        "other sum": {
            "reserved_words": [
                "total"
            ],
            "pre_aggregation_functions": "sum",
            "pre_cut_text": true
        },
        "average options": {
            "reserved_words": [
                "average",
                "avg",
                "mean"
            ],
            "pre_aggregation_functions": "avg",
            "pre_cut_text": true
        },
        "superlative min": {
            "reserved_words": [
                "least",
                "smallest",
                "tiniest",
                "shortest",
                "cheapest",
                "nearest",
                "lowest",
                "worst",
                "newest",
                "min",
                "minimum"
            ],
            "pre_aggregation_functions": "min",
            "pre_cut_text": true
        },
        "superlative max": {
            "reserved_words": [
                "most",
                "most number of",
                "biggest",
                "longest",
                "furthest",
                "highest",
                "tallest",
                "greatest",
                "best",
                "oldest",
                "max",
                "maximum"
            ],
            "pre_aggregation_functions": "max",
            "pre_cut_text": true
        },
        "time scale options": {
            "reserved_words": [
                "daily",
                "monthly",
                "yearly"
            ],
            "pre_time_scale_replace_text": {
                "daily": "day",
                "monthly": "month",
                "yearly": "year"
            },
            "pre_time_scale_aggregation_functions": "sum",
            "pre_cut_text": false
        }
    }
}
```


#### NaLIR Configuration File

``` xml
./config/nalir_tokens.xml
<?xml version="1.0" ?>
<!-- define tokens for dependency parse tree -->
<!-- all terms are in lower case -->
<types>
<!-- Command Token, verb -->
<CMT_V>
<phrase>what
<example>What was the production of oil in the state of Rio de Janeiro?</example>
</phrase>
<phrase>which
<example>Which field produces the most oil per month?</example>
</phrase>
<phrase>how
<example>How many fields are there in Paraná?</example>
</phrase>
<phrase>who</phrase>
<phrase>whom</phrase>
<phrase>where</phrase>
<phrase>when</phrase>
<phrase>tell
<example>Tell me all the books published in year 1993.</example>
</phrase>
<phrase>give
<example>Give me all the books published in year 1993.</example>
</phrase>
<phrase>return
<example>Return all the books published in year 1993.</example>
</phrase>
<phrase>list
<example>List all the books published in year 1993.</example>
</phrase>
<phrase>find
<example>Find all the books published in year 1993.</example>
</phrase>
<phrase>show
<example>Show all the books published in year 1993.</example>
</phrase>
<phrase>retrieve
<example>Retrieve all the books published in year 1993.</example>
</phrase>
<phrase>display
<example>Display all the books published in year 1993.</example>
</phrase>
<phrase>search
<example>Search all the books published in year 1993.</example>
</phrase>
<phrase>select
<example>Select all the books published in year 1993.</example>
</phrase>
<!-- TODO: double check this -->
<phrase>produce
<example>Produce all the books published in year 1993.</example>
</phrase>
<phrase>generate</phrase>
<phrase>list</phrase>
</CMT_V>
<!-- Order By Token -->
<OBT>
<phrase>sort by
<example>Find all the books published by Ayn Rand, sorted by title.</example>
</phrase>
<phrase>order by
<example>Find all the books published by Ayn Rand, ordered by title.</example>
</phrase>
<phrase>
in the order of
</phrase>
</OBT>
<!-- Function Token, adjective -->
<FT>
</FT>
<!-- Operator Token, adj -->
<OT>
<phrase>earlier
<operator>&lt;</operator>
<example>Find all the books of Ayn Rand, where the year of each book is earlier than the year of "Fountain Head".</example>
</phrase>
<phrase>later
<operator>&gt;</operator>
<example>Find all the books of Ayn Rand, where the year of each book is later than the year of "Fountain Head".</example>
</phrase>
<phrase>greater
<operator>&gt;</operator>
<example>Find all the books with greater than 2 editors.</example>
</phrase>
<phrase>more
<operator>&gt;</operator>
<example>Find all the books with more than 2 editors.</example>
</phrase>
<phrase>less
<operator>&lt;</operator>
<example>Find all the books with less than 5 authors.</example>
</phrase>
<phrase>larger
<operator>&gt;</operator>
<example>Find all the books, where the number of authors of each book is larger than 5.</example>
</phrase>
<phrase>smaller
<operator>&lt;</operator>
<example>Find all the books, where the number of authors of each book is smaller than 5.</example>
</phrase>
<phrase>higher
<operator>&gt;</operator>
<example>Find all the books, where the price of each book is higher than 100.</example>
</phrase>
<phrase>lower
<operator>&lt;</operator>
<example>Find all the books, where the price of each book is lower than 5.</example>
</phrase>
<phrase>at least
<operator>&gt;=</operator>
</phrase>
<phrase>before
<operator>&lt;</operator>
<example>Find all the books by Ayn Rand published before 1949.</example>
</phrase>
<phrase>after
<operator>&gt;</operator>
<example>Find all the books published after 2004.</example>
</phrase>
<phrase>equal
<operator>=</operator>
<example>Find all the books of Ayn Rand, where the year of each book is equal to the year of "Fountain Head".</example>
</phrase>
<phrase>same
<operator>=</operator>
<example>Return the articles where the author is the same as the author of "Java and XML" </example>
</phrase>
<phrase>as many
<operator>=</operator>
</phrase>
</OT>
<!-- Qualifier Token -->
<QT>
<phrase>every
<quantity>all</quantity>
<example>Return all the books, where the name of every author of each book ends with "Green". </example>
</phrase>
<phrase>each
<quantity>each</quantity>
</phrase>
<phrase>per
<quantity>each</quantity>
</phrase>
<phrase>by
<quantity>each</quantity>
</phrase>
<phrase>all
<quantity>all</quantity>
</phrase>
<phrase>some
<quantity>any</quantity>
<example>Return all the books, where the name of some authors of each book ends with "Green". </example>
</phrase>
<phrase>any
<quantity>any</quantity>
</phrase>
</QT>
<!-- Negation Token -->
<NEG>
<phrase>not</phrase>
<phrase>no</phrase>
<phrase>didn't</phrase>
<phrase>doesn't</phrase>
<phrase>haven't</phrase>
<phrase>hasn't</phrase>
<phrase>nothing</phrase>
</NEG>
</types>
```

