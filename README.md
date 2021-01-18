# GLAMORISE
GLAMORISE (GeneraL Aggregation MOdule using a RelatIonal databaSE)  

This project refers to the implementation of GLAMORISE Natural Language Interface to Databases (NLIDB). You can find out more about GLAMORISE in the following article:

* [A Novel Solution for the Aggregation Problem in Natural Language Interface to Databases (NLIDB)](./paper/207509_1-A-Novel-Solution-for-the-Aggregation-Problem-in-Natural-Language-Interface-to-Databases-NLIDB.pdf). Novello, A., F.; and Casanova, M., A. Proc. XXXV Brazilian Symposium on Databases - SBBD. 2020. Awarded as the 2nd Best Short Paper.

This implementation of GLAMORISE uses NaLIR as one of its integtared NLIDBs, so you will have to clone the [nalir-glamorise](https://github.com/novello/nalir-glamorise) repository. This project is a customization of the [nalir-ssbd](https://github.com/pr3martins/nalir-sbbd) project which in turn is a Python port of the original [NaLIR project](https://github.com/umich-dbgroup/NaLIR). Please follow all the steps described in the README of the nalir-glamorise project.

The paths below are relative to the root path of the GLAMORISE project. You are expected to be positioned on this path.


## Setting up the environment

General dependencies 

``` bash
  $ pip3 install -r requirements.txt
```

NLTK dependencies used by NaLIR.

``` bash
  python3 ./config/nltk_setup.py
```

## Setting up the database


### ANP MySQL database

Used with the NaLIR NLIDB which uses an ANP (Agência Nacional de Petróleo - Brazilian Petroleum Agency) MySQL database.

First create the databases inside mysql

``` mysql
    create database anp;
    create database mas;
```

``` bash
    $ mysql -D anp -u <user> -p < ./config/nalir_anp_mysql.sql
```


### MAS MySQL database

Used with the NaLIR NLIDB which uses the MAS (Microsoft Academic Search) MySQL database. This database is used in the NaLIR original paper.

First follow all the installation steps in the README of the nalir-glamorise project and then run the command below:


``` bash
    $ mysql -D mas -u <user> -p < ./config/setup_mas_glamorise.sql
```


## Configuration files


### Path adjustment

You will have to adjust the relative path of the project nalir-glamorise (nalir_relative_path) in the following JSON file:

./config/path.json
``` json
    {
        "nalir_relative_path" : "../nalir-glamorise",    
        "glamorise_relative_path" : "./"
    }  
```


### NaLIR database and special folders configurations

You will have to adjust the JSON files below with the correct database connection information and the path under the nalir-glamorise project to the folders zfiles and new_jars


#### ANP database
./config/nalir_anp_local_db.json
``` json
{
    "connection":{
            "host": "localhost",
            "password":"your password",
            "user":"your user",
            "database":"anp"
    },
    "loggingMode": "ERROR",
    "zfiles_path":"/path/to/nalir-glamorise/zfiles",
    "jars_path":"/path/to/nalir-glamorise/jars/new_jars"
}
```


#### MAS database
./config/nalir_mas_local_db.json
``` json
{
    "connection":{
            "host": "localhost",
            "password":"your password",
            "user":"your user",
            "database":"mas"
    },
    "loggingMode": "ERROR",
    "zfiles_path":"/path/to/nalir-glamorise/zfiles",
    "jars_path":"/path/to/nalir-glamorise/jars/new_jars"
}
```


## Test Coverage

If you have changed the code and would like to test if it has broken anything, there is a simple set of tasks covering the Mock NLIDB in ./test_glamorise.py


## Web Interface

To use the project in a convenient way, a web interface was created that can be loaded by running the file ./web_interface/web_api.py


## [OPTIONAL] Configuration files

### GLAMORISE and NaLIR customization of pattern files

If you want to change the patterns accepted by GLAMORISE and NaLIR, this could be achieved by modifying the following files below:


#### GLAMORISE Mock ANP

./config/glamorise_mock_anp.json


#### GLAMORISE with NaLIR (ANP database)

./config/glamorise_nalir_anp.json


#### GLAMORISE with NaLIR (MAS database)

./config/glamorise_nalir_mas.json


#### NaLIR Configuration File

./config/nalir_tokens.xml



