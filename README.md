# GLAMORISE
GLAMORISE (GeneraL Aggregation MOdule using a RelatIonal databaSE)  

Natural Language Interface to Databases (NLIDB) systems usually do not deal with aggregations, which can be of two types: aggregation functions (such as count, sum, average, minimum, and maximum) and grouping functions (GROUP BY). GLAMORISE addresses the creation of a generic module, to be used in NLIDB systems, that allows such systems to perform queries with aggregations, on the condition that the query results the NLIDB returns are or can be transformed into tables.

This project refers to the implementation of GLAMORISE Natural Language Interface to Databases (NLIDB). You can find out more about GLAMORISE in the following article:

* [A Novel Solution for the Aggregation Problem in Natural Language Interface to Databases (NLIDB)](./web_interface/static/paper/207509_1-A-Novel-Solution-for-the-Aggregation-Problem-in-Natural-Language-Interface-to-Databases-NLIDB.pdf). Novello, A., F.; and Casanova, M., A. Proc. XXXV Brazilian Symposium on Databases - SBBD. 2020. Awarded as the 2nd Best Short Paper.

A [working demo](http://glamorise.gruposantaisabel.com.br) of this project is available.

This implementation of GLAMORISE uses NaLIR as its integrated NLIDB, so you will have to clone the [nalir-glamorise](https://github.com/novello/nalir-glamorise) repository. This project is a customization of the [nalir-ssbd](https://github.com/pr3martins/nalir-sbbd) project which in turn is a Python port of the original [NaLIR project](https://github.com/umich-dbgroup/NaLIR). Please follow all the steps described in the README of the nalir-glamorise project.

The paths below are relative to the root path of the GLAMORISE project. You are expected to be in this position on the path.


## Setting up the environment

General dependencies 

``` bash
  $ pip3 install -r requirements.txt
```

NLTK dependencies used by NaLIR.

``` bash
  $ python3 ./config/setup/nltk_setup.py
```

NLTK also needs a Java environment working with the JAVA_HOME environment variable set. To do this installation on Ubuntu follow the steps below:

``` bash
  $ sudo apt update
  $ sudo apt install openjdk-11-jdk-headless
```

Update the environment file in a text editor:

``` bash
  $ sudo nano /etc/environment
```

 And configure the JAVA_HOME variable value in the file:

 ``` bash
  JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64/bin/java" 
```

## Setting up the database


### ANP MySQL database

Used by the NaLIR NLIDB which uses an ANP (Agência Nacional de Petróleo - Brazilian Petroleum Agency) MySQL database.

First create the database inside mysql:

``` mysql
    create database anp;    
```

And then run the following database dump:

``` bash
    $ mysql -D anp -u <user> -p < ./config/setup/dump_nalir_anp_mysql.sql
```

After this, run the following script, which is responsible for creating the configuration needed by NaLIR in order to work correctly with the ANP database:

``` bash
    mysql -D anp -u <user> -p < ./zfiles/setup_anp_nalir.sql
```


### MAS MySQL database

Used by the NaLIR NLIDB which uses the MAS (Microsoft Academic Search) MySQL database. This database is used in the NaLIR original paper.


First create the database inside mysql:

``` mysql
    create database mas;    
```

And then follow all the installation steps in the README of the nalir-glamorise project.


## Configuration files


### Path adjustment

You will have to adjust the relative path of the project nalir-glamorise (nalir_relative_path) in the following JSON file:

./config/environment/path.json
``` json
    {
        "nalir_relative_path" : "../nalir-glamorise",    
        "glamorise_relative_path" : "./"
    }  
```


### NaLIR database and special folders configurations

You will have to create the JSON files below with the correct database connection information and the path under the nalir-glamorise project to the folders zfiles and new_jars. You can use the respective template file to customize each one:


#### ANP database
create the file ./config/environment/nalir_anp_db.json
based on the file ./config/environment/nalir_anp_db_template.json
``` json
{
    "connection": {
        "host": "localhost",
        "password": "your_password",
        "user": "your_user",
        "database": "anp"
    },
    "loggingMode": "ERROR",
    "zfiles_path": "/path/to/nalir-glamorise/zfiles",
    "jars_path": "/path/to/nalir-glamorise/jars/new_jars"
}
```


#### MAS database
create the file ./config/environment/nalir_mas_db.json
based on the file ./config/environment/nalir_mas_db_template.json
``` json
{
    "connection": {
        "host": "localhost",
        "password": "your_password",
        "user": "your_user",
        "database": "mas"
    },
    "loggingMode": "ERROR",
    "zfiles_path": "/path/to/nalir-glamorise/zfiles",
    "jars_path": "/path/to/nalir-glamorise/jars/new_jars"
}
```


## Test Coverage

If you have changed the code and would like to test if it has broken anything, there is a simple set of tasks covering the Mock NLIDB in ./test_glamorise.py


## Web Interface

To use the project in a convenient way, a web interface was created. 

You can start the web interface with the shell script ./start_flask.sh

You can stop the web interface with the shell script ./stop_flask.sh

You can audit the log by looking at the file ./log.txt

## Running at the terminal

If your business is more about using the terminal than the web environment, you can customize one of these 6 files. Half of them are prepared to run a single NLQ and the other half is prepared to run a sequence of NLQs. The names are self explanatory:

./main_mock_single_nlq.py

./main_mock.py

./main_nalir_anp_single_nlq.py

./main_nalir_anp.py

./main_nalir_mas_single_nlq.py

./main_nalir_mas.py

## [OPTIONAL] Configuration files

### GLAMORISE and NaLIR customization of pattern files

If you want to change the config_glamorise accepted by GLAMORISE and NaLIR, this could be achieved by modifying the files below:


#### GLAMORISE Mock ANP

./config/environment/glamorise_mock.json


#### GLAMORISE with NaLIR

./config/environment/glamorise_nalir.json


#### NaLIR Configuration File

./config/environment/nalir_tokens.xml



