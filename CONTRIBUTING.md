# Contributing

If you wish to contribute to the SCAICT-uwu, feel free to fork the repository
and submit a pull request.

All development happens on the `development` branch. Make sure to submit pull
requests in the correct branch.

## Coding conventions

### File formatting

#### Indentation

For JSON and Python files, lines should be indented with 4 whitespace characters
per indenting level.

For YAML files, lines should be indented with 2 whitespace characters per
indenting level.

#### Newlines

* All files should use Unix-style newlines (single LF character, not a CR+LF
  combination).
* All files should have a newline at the end.

#### Encoding

All text files must be encoded with UTF-8 without a
[Byte Order Mark](https://en.wikipedia.org/wiki/Byte_order_mark).

Do not use Microsoft Notepad to edit files, as it always inserts a BOM.

#### Whitespace

The general whitespace style for Python would be:

```py
statement # Inline comments
```

```py
if condition and condition or condition:
```

```py
if (
    condition and
    condition or
    condition
):
```

```py
def function_name(arg_1: type = "value 1", arg_2: type) -> type:
```

```py
def function_name(
    arg_1: type = "value 1",
    arg_2: type
) -> type:
```

#### Trailing whitespace

Developers should avoid adding trailing whitespace.

#### Line width

Lines should be broken with a line break at maximum 80 characters.

#### Import order

Imports should use the following order first, then the alphabetical order:

```py
# Standard imports
# Third-party imports
# Local imports
```

See
[wrong-import-order / C0411](https://pylint.readthedocs.io/en/latest/user_guide/messages/convention/wrong-import-order.html)
for further information.

### Naming conventions

Naming cases:

* `snake_case`
* `camelCase`
* `PascalCase`
* `UPPER_CASE`

#### Python

| Name Type           | Case         |
| ------------------- | ------------ |
| module (file names) | `snake_case` |
| const               | `UPPER_CASE` |
| class               | `PascalCase` |
| function            | `snake_case` |
| method              | `snake_case` |
| variable            | `snake_case` |
| attribute           | `snake_case` |
| argument            | `snake_case` |

Example:

```txt
python_module.py
```

```py
CONST = 1

class ClassName:
    def method_name(self, arg_name: int) -> int:
        print(arg_name)

        return arg_name
```

See
[invalid-name / C0103](https://pylint.readthedocs.io/en/latest/user_guide/messages/convention/invalid-name.html)
for further information.

#### Database

* ALWAYS and ONLY capitalize SQL reserved words in SQL queries.
  * See the official documentations of SQL and the
  [complete list on English Wikipedia](https://en.wikipedia.org/wiki/List_of_SQL_reserved_words)
  as references.
* ALWAYS use `snake_case` for database, table, column, trigger names.
  * Table names and column names may NOT be case-sensitive in SQLite.
  * Database, table, and trigger names may NOT be case-sensitive in
  MySQL/MariaDB.
* Column names should be unique, i.e., same column name should not exist in
  different tables.
* Column names should be prefixed with table names or abbrieviations.
  * For example, `user_id` in `user`, `ug_user` in `user_groups`.

Examples:

```sql
INSERT INTO user (uid) VALUE (6856)
```

```sql
UPDATE game SET game_seq = game_seq + 1
```
