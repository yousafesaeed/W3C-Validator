#!/usr/bin/python3
"""
W3C validator for Holberton School

For HTML and CSS files.

Based on 2 APIs:

- https://validator.w3.org/nu/
- http://jigsaw.w3.org/css-validator/validator


Usage:

Simple file:

```
./w3c_validator.py index.html
```

Multiple files:

```
./w3c_validator.py index.html header.html styles/common.css
```

All errors are printed in `STDERR`

Return:
Exit status is the # of errors, 0 on Success

References

https://developer.mozilla.org/en-US/

"""
import sys
import requests
import os


def __print_stdout(msg):
    """Print message in STDOUT
    """
    sys.stdout.buffer.write(msg.encode('utf-8'))


def __print_stderr(msg):
    """Print message in STDERR
    """
    sys.stderr.buffer.write(msg.encode('utf-8'))


def __analyse_html(file_path):
    """Start analyse of HTML file
    """
    h = {'Content-Type': "text/html; charset=utf-8"}
    d = open(file_path, "r").read()
    u = "https://validator.w3.org/nu/?out=json"
    r = requests.post(u, headers=h, data=d)
    res = []
    messages = r.json().get('messages', [])
    # Check that files have something in them

    for m in messages:
        # Capture files that have incomplete or broken HTML
        if m['type'] == 'error' or m['type'] == 'info':
            res.append("[{}] {}".format(file_path, m['message']))
        else:
            res.append("[{}:{}] {}".format(
                file_path, m['lastLine'], m['message']))
    return res


def __analyse_css(file_path):
    """Start analyse of CSS file
    """
    d = {'output': "json"}
    f = {'file': (file_path, open(file_path, 'rb'), 'text/css')}
    u = "http://jigsaw.w3.org/css-validator/validator"
    r = requests.post(u, data=d, files=f)
    res = []
    # Check if there are errors, then append them to the response
    errors = r.json().get('cssvalidation', {}).get('errors', [])
    for e in errors:
        res.append("[{}:{}] {}".format(file_path, e['line'], e['message']))
    return res


def __analyse(file_path):
    """Start analyse of a file and print the result
    """
    nb_errors = 0
    try:
        result = None

        if file_path.endswith('.css'):
            result = __analyse_css(file_path)
        elif file_path.endswith((".html", "html", ".svg")):
            result = __analyse_html(file_path)
        else:
            allowed_files = "'.css', '.html', '.htm' and '.svg'"
            raise OSError(
                "File {} does not have a valid file extension. Only {} are "
                "allowed.".format(file_path, allowed_files)
                )

        if os.path.getsize(file_path) == 0:
            raise OSError(f"File {file_path} is empty")

        if len(result) > 0:
            for msg in result:
                __print_stderr("{}\n".format(msg))
                nb_errors += 1
        else:
            __print_stdout("{} => OK\n".format(file_path))

    except Exception as e:
        __print_stderr("[{}] {}\n".format(e.__class__.__name__, e))
    return nb_errors


def __files_loop():
    """Loop that analyses for each file from input arguments
    """
    nb_errors = 0
    for file_path in sys.argv[1:]:
        nb_errors += __analyse(file_path)

    return nb_errors


if __name__ == "__main__":
    """Main
    """
    if len(sys.argv) < 2:
        __print_stderr("usage: w3c_validator.py file1 file2 ...\n")
        exit(1)

    """execute tests, then exit. Exit status = # of errors (0 on success)
    """
    sys.exit(__files_loop())
