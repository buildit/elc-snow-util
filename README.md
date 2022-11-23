# Summary

Python CLI that includes a couple of reports and a utility commands that run against ServiceNow
with the Employee Center application.

# How to Install

* Install Python 3.10
* Download a tarball of a release of this command
* Run the following to install

    pip install elc-snow-util-1.0.0.tar.gz

# Configuration File

The command-line needs a configuration file in `%APPDATA%\snowutil.ini`.  On Linux/MacOS, it will look for this file in `$HOME/.config/snowutil.conf`.

The format of the file as as follows:

```
endpoint: https://host-name-of-service-now/api
username: admin_username
password: admin_password
taxonomy: name-of-the-employee-center-taxonomy
```

No credentials are stored with the software itself.

# Commands

The software supports the following sub-commands:

| Command Name   | Description | 
|----------------|-------------|
| `catalog-report` | Creates a report on all Catalog Items (`sc_cat_item`) connected to a topic in the Taxonomy |
| `sort-content` | Modify the `order` of all content (`m2m_connected_content`) connected to a topic in the taxonomy |
| `topics-report` | Creates a report on all Topics (`topic`) in the taxonomy |
| `topic-icons` | Download the icons for each topic in the taxonomy |


## Uage and Common Options

You can always find out the usage of a command by using the `-h` option with that command.  As an example, the command-line below finds the usage for the catalog-report:

```
elc-snow-util catalog-report -h
```

All of these commands support the following common options:

| Long Option | Short Option | Description |
|-------------|--------------|-------------|
| `--config path` | `-c path` | You can have a different file for each service now instance |
| `--quiet` | `-q` | By default, the command tells you how many API calls it has made and shows some progress |


## Catalog Report

The catalog report requires an `OUTPUT` path which can be a CSV or XLSX.  It supports the following options:

| Long Option | Short Option | Description |
|-------------|--------------|-------------|
| `--drop-missing` | None     | Drops catalog items that are not connected to the taxonomy |
| `--active-items` | None | Query only on active items |
| `--active-topics` | None | Report only menu items for active topics in the taxonomy |

An example of calling this command is as follows:

```
elc-snow-util catalog-report --drop-missing --active-topics Items-Connected-to-Active-Topics.xlsx
```

## Topics Report

The topics report uses the REST Table Api of the `topics` and `m2m_connnected_content` tables to report on the number of catalog items connected to each topic, or menu item.  It requires an `OUTPUT` path which can be a CSV or XLSX.  

It supports the following options:

| Long Option | Short Option | Description |
|-------------|--------------|-------------|
| `--active` | `-a` | Report only on active topics |

An example of calling this command is as follows:

```
elc-snow-util -a Active-Topic-with-Content-Count.xlsx
```

## Topics Icons

The topic icons command uses the REST Table API against the `topics` table to get the id of each Icon, which it then downloads.  It uses a python package linked with [libmagic](https://man7.org/linux/man-pages/man3/libmagic.3.html) that determines from the file's contents whether it is a PNG, JPEG, or SVG, and then renames the file based on the menu path and the appropriate extension.

The topic icons command requires an `OUTPUT` which should be the path to a directory, which will be created if it does not exist.

The command supports the following options:

| Long Option | Short Option | Description |
|-------------|--------------|-------------|
| `--active` | `-a` | Report only on active topics |

An example of calling it is as follows

```
elc-snow-util topic-icons --active Menu-Icons
dir/w Menu-Icons
```

## Sort Content Utility

This command is the only utility which modifies service now.  It takes an `TOPIC_PATH` argument which tells it which connected content to reorder.  An example of calling this command is as follows:

```
elc-snow-util sort-content "Software /"
```

This would sort all of the content items connected to the Software topic.  This command only 
queries on content connected to active topics.