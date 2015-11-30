import yaml
import argparse
import pytest
from io import StringIO

from ansible_role.do_roles import (
    write_playbook_file,
    parse_host)


def test_playbook_file():

    def attempt(roles, includes, target):
        # Fake include files
        if includes is None:
            include_files = None
        else:
            include_files = []
            for include in includes:
                include_file = StringIO()
                include_file.write(include)
                include_file.seek(0)
                include_files.append(include_file)

        # Fake output file
        out_file = StringIO()

        # Build playbook
        write_playbook_file(roles, out_file, include_files)

        # Validate results
        res = out_file.getvalue()
        assert res.startswith("---\n")

        parsed_res = list(yaml.safe_load_all(res))
        assert parsed_res[0] == target

    attempt([], None, {
        "become": True,
        "hosts": "hosts",
        "roles": []
    })

    attempt(["123", "wer"], ["""
vars:
    foo: "asdf"
    bar: "wer123"
    """], {
        "become": True,
        "hosts": "hosts",
        "roles": ["123", "wer"],
        "vars": {
            "foo": "asdf",
            "bar": "wer123"
        }
    })


def test_parse_host():
    assert parse_host("host") == {
        "host": "host",
        "port": None,
        "user": None
    }

    assert parse_host("us-er123@host") == {
        "host": "host",
        "port": None,
        "user": "us-er123"
    }

    assert parse_host("host:8382") == {
        "host": "host",
        "port": "8382",
        "user": None
    }

    with pytest.raises(argparse.ArgumentTypeError):
        parse_host("ho st")

    with pytest.raises(argparse.ArgumentTypeError):
        parse_host("host:abcd")
