import argparse
import tempfile
import subprocess
import json
import yaml
import os
import re


def parse_host(host):
    "Read username and port from host strings."
    m = re.match(
        r"(?:(?P<user>[a-zA-Z0-9_.-]+)@)?"
        r"(?P<host>[a-zA-Z0-9_.-]+)"
        r"(?::(?P<port>[0-9]+))?"
        r"$",
        host)
    if m:
        return m.groupdict()
    else:
        raise argparse.ArgumentTypeError("Malformed host: %r" % host)


def write_inventory_file(hosts, outfile):
    "Write the temporary inventory file."
    # Put everything in a generically named group
    print("[hosts]", file=outfile)

    # Add each host with a numeric nickname
    for ii, host in enumerate(hosts):
        desc = ["host_%d" % ii,
                "ansible_connection=ssh",
                "ansible_python_interpreter=/usr/bin/python2",
                "ansible_host=%s" % host['host']]

        if host.get('port'):
            desc.append("ansible_port=%s" % host['port'])

        if host.get('user'):
            desc.append("ansible_user=%s" % host['user'])

        inventory_line = "  ".join(desc)
        print(inventory_line, file=outfile)


def write_playbook_file(roles, outfile, include_files=None):
    "Write the temporary playbook file."
    base_doc = {
        "become": True,
        "hosts": "hosts",
        "roles": roles
    }

    if include_files is None:
        include_files = []

    for include_file in include_files:
        for doc in yaml.safe_load_all(include_file):
            for k, data in doc.items():
                if k not in base_doc:
                    base_doc[k] = data

    output = "---\n\n%s" % yaml.safe_dump(base_doc)

    print(output, file=outfile)


def build_environment(path, hosts, roles):
    "Construct the ansible environment."
    inventory_fn = os.path.join(path, "hosts")
    with open(inventory_fn, "w") as outf:
        write_inventory_file(hosts, outf)

    playbook_fn = os.path.join(path, "play.yml")
    with open(playbook_fn, "w") as outf:
        write_playbook_file(roles, outf)

    # for role in roles:
    #     role_name = os.path.basename(role)
    #     role_dst = os.path.join(path, role_name)

    #     if os.path.exists(role_dst):
    #         raise ValueError("Failed to link role.")
    #     else:
    #         os.symlink(role, role_dst)

    return {
        "inventory_fn": inventory_fn,
        "playbook_fn": playbook_fn
    }


def run_ansible(env, remaining_args):
    "Execute ansible with appropriate flags."
    ansible_path = "ansible-playbook"
    ansible_command = [
        ansible_path,
        "-i", env['inventory_fn'],
    ] + remaining_args + [
        env['playbook_fn']
    ]

    r = subprocess.call(ansible_command)


def prep_and_run(opts, remaining_args):
    with tempfile.TemporaryDirectory() as tmpdir:
        env = build_environment(tmpdir,
                                hosts=opts.hosts,
                                roles=opts.roles)
        run_ansible(env, remaining_args)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-H", "--host", type=parse_host,
                    dest='hosts', action="append",
                    help="Host descriptors")
    ap.add_argument("-d", "--directory", default="./roles",
                    help="Role directory")
    ap.add_argument("-y", "--yaml", type=argparse.FileType("r"),
                    help="Inject additional YAML files")
    ap.add_argument("roles", nargs="+")

    opts, unknown = ap.parse_known_args()

    # Validate hosts
    if not opts.hosts:
        ap.error("Provide at least one host.")

    # Validate roles
    role_paths = []
    for role in opts.roles:
        role_path = os.path.abspath(
            os.path.join(opts.directory, role))

        if not os.path.exists(role_path):
            ap.error("Could not find role %r" % role)

        role_paths.append(role_path)
    opts.roles = role_paths

    # Do it
    prep_and_run(opts, unknown)


if __name__ == "__main__":
    main()
