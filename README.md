# Journal Transporter

Journal Transporter is a Python 3 CLI application that facilitates the transfer of scholarly journal data to and from different online publishing platforms.

## Requirements

* Python 3.9 / Pip3
* Linux or Unix-based OS
  * Untested on Windows. It may work, except for included Bash scripts

## Installation

Clone this repo and navigate to it. Install dependencies with `bin/install`.

## Usage

CLI commands can be executed with:

```shell
bin/journal-transporter <COMMAND>
```

or

```shell
python -m journal_transporter <COMMAND>
```

Note: If you use the latter syntax and invoke python directly, you'll likely want to activate the virtual environment first with `source ./venv/bin/activate`. `bin/journal-transporter` does this for you.

`bin/install` also by default creates a symlink for `journal-transporter` in `user/local`. If this is permitted, the application can be invoked simply at `journal-transporter`.

### Options

```
  -v, --verbose         Enable verbose output
  --version             Show the application's version and exit
  --help                Show this message and exit.
```

### Commands

#### `configure`
  Apply configuration options.

  These options will be used as default values for the transfer command, unless
  different options are provided.
```
Options:
  -d, --data-directory TEXT       Path to data directory location
  --default-source, --s TEXT      Name of an already-defined source server to
                                  use by default (see define-server)
  --default-target, --t TEXT      Name of an already-defined target server to
                                  use by default (see define-server)
  -k, --keep / -K, --discard      Should the dataset from this transfer be
                                  kept? This could use a lot of disk space
  --keep-max INTEGER              If --keep is true, how many transfers should
                                  be kept? Older transfer will be discarded.
  -v, --verbose / -V, --succinct  Verbose output by default
  --help                          Show this message and exit.
```

#### `define-server`
  Defines a server that can be referenced later as a source or destination.

  If `NAME` already exists in the config (case sensitive), this command will
  update that server rather than creating a new one.
```
Arguments:
  NAME  Name of the server to create or update  [required]

Options:
  -h, --host TEXT        The server's URL or hostname that can be used to
                         access it from this machine
  -t, --type [ssh|http]  Method that should be used to connect to the server
  -u, --user TEXT        Username of a user authorized to access the
                         information
  -p, --password TEXT    Password of a user authorized to access the
                         information
  --port INTEGER         The port to which the client should connect
  --help                 Show this message and exit.
```

#### `delete-server`
  Deletes a server configuration.
```
Arguments:
  NAME  Name of the server you wish to delete  [required]

Options:
  -f, --force  Perform delete without confirmation prompt
  --help       Show this message and exit.
```

#### `get-config`
Displays the current application configuration.
```
Options:
--help  Show this message and exit.
```

#### `init`

Initialize the application for use. Must be called first.

This command should be called before all else. It creates the data directory
and config file, so is required before any other configuration.
```
Options:
-d, --data-directory TEXT  Path to data directory location
--help                     Show this message and exit.
```

#### `transfer`

Initiates a transfer of data from a source server to a target server.

By default, this command invokes 3 actions - index, fetch, and push. These actions can be invoked
individually by using the `--index-only`, `--fetch-only`, and `--push-only` flags. When using
`--index-only` or `--fetch-only`, only a `--source` must be defined. When using `--push-only`,
only a `--target` must be defined.

Note that `--fetch-only` will inherently invoke index unless indexes have already been cached
for the provided source. `--push-only` can only be used if data has already been indexed
and fetched.

```
Options:
-j, --journals TEXT         Any number of journal key names (also known as
                            'paths' or 'codes') that are to be transferred
-s, --source TEXT           Name of an already-defined source server to use
                            (see define-server)
-t, --target TEXT           Name of an already-defined target server to use
                            (see define-server)
--fetch-only                If true, only fetch data and do not transfer to
                            target server.
--push-only                 If true, only take currently-stored data and
                            transfer to target server. Do not fetch new
                            data.
--index-only                If true, only index data and do not fetch or
                            push.
--data-directory, --d TEXT  Path to data directory location  [default:
                            /Users/timfrazee/Library/Application
                            Support/journal_transporter]
-k, --keep / -K, --discard  Should the dataset from this transfer be kept?
                            This could use a lot of disk space
--debug                     Enable debug output
-f, --force                 Run without prompts
--help                      Show this message and exit.
```

All commands are described by invoking `bin/jt --help`. Detail on individual commands can be viewed with `bin/jt <COMMAND> --help`.

### Workflow

Generally speaking, the process of transferring a journal from a source server to a target server involves the following commands:

1) Define the source server
```bash
journal-transporter define-server <source_server_name> --host <source_server_plugin_api_url> --username <auth_user> --password <auth_password>
```

2) Define the target server
```bash
journal-transporter define-server <target_server_name> --host <destination_server_plugin_api_url> --username <auth_user> --password <auth_password>
```

3) Initiate the transfer, referencing the servers created above
```bash
journal-transporter transfer --source <source_server_name> --target <target_server_name> --journals <journal_path>
```

See documentation for the `transfer` command (`jt transfer --help`) for more options.

### Examples

Let's say there is a source OJS server at https://ojs.example.com, with Journal Transporter
plugin available at `/jt`. On this server instance, there is a privileged user with username
`ojs_admin` and password `abc_easy`.

There is also a Janeway server located at https://janeway.example.com, which has the
Journal Transporter plugin installed at`/plugins/journal-transporter`.
On this Janeway instance, there is a privileged user with username `janeway_admin`
and password `as_123`.

#### Set Up

First, you must define the source OJS server in Journal Transporter. We'll name is "ojs":

```bash
journal-transporter define-server ojs --host https://ojs.example.com/jt --user ojs_admin --password abc_easy
```

Then, you must define the target Janeway server. We'll name it "janeway":

```bash
journal-transporter define-server janeway --host https://janeway.example.com/plugins/journal-transporter --user janeway_admin --password as_123
```

#### Full transfer

Let's say you have a journal called `sample_journal` that exists on the OJS server, and you want to transfer it to the Janeway server.

With your servers defined, you can now initiate the transfer of the desired journal. In this example, we'll set verbose output for more detailed progress reporting:

```bash
journal-transporter --verbose transfer --source ojs --target janeway --journals sample_journal
```

This process may take quite a long time, depending on how much data there is to be transferred.

#### Index and/or fetching only

Since transfers can take quite a long time, you may want to split it up into multiple discrete actions. This also allows you to review the data that's been fetched before pushing it.

Journal Transporter performs transfers in 3 distinct stages:
- Indexing
- Fetching
- Pushing

You can invoke these stages separately, if desired, but they must occur in this order.

##### Indexing

If you want to perform a full index of all resources that will be transferred as part of the process, you can perform indexing as a standalone action.

```bash
journal-transporter --verbose transfer --index-only --source ojs --journal sample_journal
```

When finished, the data directory's "current" directory will contain two top-level directories: "journals" and "users". See the [data structure](#data-structure) for more detail. These directories will contain at least a partial data structure and an index for each index-able resource. These indexes are primarily used for lookups during the fetching process, and only contain a small amount of the data to ultimately be transferred.

##### Fetching

After indexing, Journal Transporter can fetch all of the data and files necessary for the transfer. This can be invoked independently with

```bash
journal-transporter --verbose transfer --fetch-only --source ojs --journal sample_journal
```

Depending on the size of the journal, this process may consume a significant amount of disk space.

Fetching will pull detailed JSON data for each indexed object, as well as referenced binary files. They will all be stored in the structure defined in the [data structure](#data-structure) section.

##### Pushing

The final step of the transfer process is pushing the fetched data to the target server (in this example, a Janeway instance). This can be done, provided indexing and fetching have already been completed, with:

```bash
journal-transporter --verbose transfer --push-only --target janeway --journal sample_journal
```

Note that the plugin on the target server (in this case, the Janeway plugin) is responsible for handling the raw data pushed to it by Journal Transporter. Before starting the push, ensure that the target database is ready to accept the data (i.e. sufficient space, no impending journal code conflicts, etc.)

If a fatal error occurs during this process, you will be notified, but Journal Transporter will not, itself, perform any clean up of your target server (plugins are responsible for their own clean-up, if any is to be performed). After addressing the issue, you will likely need to seek out and delete any created resources on the target server (journals, files, etc) before trying again.

## Data Structure

Journal Transporter saves all indexed and fetched data to the data directory defined in the application's configuration file. By default, data is stored in a directory called "current", indicating that it is relevant to the current (or most recent) transfer process invoked. If you used the `--keep` flag or configuration, "current" may be a symlink to a dated directory that will be retained.

Within the data directory is a nested hierarchy of resource directories, named after the type of resource contained. Note that this name may not be the same as the resource in the source server. Names in Journal Transporter are designed to be as generic and simply descriptive as possible, but do not account for different systems' naming schemes.

All indexed and fetched objects are assigned a unique UUID. This UUID is stored in the index, as well as used as the directory name for that resource.

### Hierarchy

Files fall into a data hierarchy that resembles the following:

- users
- journals
  - roles
  - issues
  - sections
  - review_forms
    - elements
  - articles
    - editors
    - authors
    - files
    - revision_requests
    - rounds
      - assignments
        - response

### Files

The above translates into a file structure that looks something like the following example (truncated for brevity):

- users/
  - index.json
  - e82dfaef-9555-45c9-98cd-b4cb84dc595f/
    - user.json
  - 37a6c228-d0b1-41fb-b141-559768f1b113/
    - user.json
- journals/
  - index.json
  - 46c807b7-7426-431d-9e02-4dcc108c67c6/
    - journal.json
    - issues/
      - index.json
      - c460af58-49f9-4cd1-a73d-38711b856e04/
        - issue.json
    - articles/
      - index.json
      - d766b878-951e-455a-b8b1-7c512a74d386/
        - article.json
        - authors/
          - index.json
          - 8eaae381-d8a9-4738-8ca7-65b90e1a8f4d/
            - author.json
        - files/
          - index.json
          - 33ba4f36-982c-4d58-b65a-e71f34f04351/
            - file.json
            - example_file.pdf

... and so on.

Except for binary files, all files are text and can be opened and reviewed in any text editor.

## Licensing
TBD

## Contributions
TBD
