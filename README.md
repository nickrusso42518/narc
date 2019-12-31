[![Build Status](
https://travis-ci.org/nickrusso42518/narc.svg?branch=master)](
https://travis-ci.org/nickrusso42518/narc)

# Nornir ASA Rule Checker
This simple program uses the Cisco ASA `packet-tracer` utility to test traffic
flows across the firewall. On a per-ASA basis, users specify a list of
simulations in YAML or JSON format. This program returns the result of those
tests in a variety of formats. Both IPv4 and IPv6 are supported.

## High-level Structure
This project is built on two powerful Python-based tools:
  1. [Nornir](https://github.com/nornir-automation/nornir),
     a  task execution framework with concurrency support
  2. [Netmiko](https://github.com/ktbyers/netmiko),
     a library for accessing network device command lines

## Variables
The `host_vars/` directory contains individual YAML files, one per ASA, that
contain a list of dictionaries named `checks`. Using Nornir for concurrency
and Netmiko for SSH-based device access, the tool issues a `packet-tracer`
command for each check. The data is returned as XML which is easily converted
into Python data structures. An example file might be `host_vars/asa1.yaml`,
which is shown below.

```
---
checks:
  - id: "DNS OUTBOUND"
    in_intf: "inside"
    proto: "udp"
    src_ip: "192.0.2.2"
    src_port: 5000
    dst_ip: "8.8.8.8"
    dst_port: 53
    should: "allow"
  - id: "HTTPS OUTBOUND"
    in_intf: "inside"
    proto: "tcp"
    src_ip: "192.0.2.2"
    src_port: 5000
    dst_ip: "20.0.0.1"
    dst_port: 443
    should: "allow"
  - id: "SSH INBOUND"
    in_intf: "management"
    proto: "tcp"
    src_ip: "fc00:192:0:2::2"
    src_port: 5000
    dst_ip: "fc00:8:8:8::8"
    dst_port: 22
    should: "drop"
  - id: "PING OUTBOUND"
    in_intf: "inside"
    proto: "icmp"
    src_ip: "192.0.2.2"
    icmp_type: 8
    icmp_code: 0
    dst_ip: "8.8.8.8"
    should: "allow"
  - id: "L2TP OUTBOUND"
    in_intf: "inside"
    proto: 115
    src_ip: "192.0.2.1"
    dst_ip: "20.0.0.1"
    should: "drop"
...
```

You can also use JSON format, which may bring better performance when `checks`
is very large. If both `.json` and `.yaml` files exist for a given host, the
JSON file is given preference and the YAML file is ignored. If neither file
is specified, the Nornir task raises a `FileNotFoundError`.

You can use the IP protocol number (1-255) or the protocol name, assuming the
ASA supports it. Currently, only the names `icmp`, `tcp`, and `udp` are
supported. For `icmp`, you must specify the `icmp_type` and `icmp_code`.
For `tcp` or `udp`, you must specify the `src_port` and `dst_port`. For
all other protocols, you only need to specify the `src_ip` and `dst_ip`.
If you specify protocol number of `6` instead of `tcp`, this script will treat
it as a `rawip` packet, which can be desirable for generalized TCP testing
if you want to omit ports. The same is true for UDP (17) and ICMP (1).

Note that it is uncommon for firewalls to filter traffic based on source port.
The `packet-tracer` utility **requires** specifying a value. Additionally, the
`id` key is useful for documentation to describe each check. This string
is also displayed in some of the output format styles.

## Validation
Each individual `check` dictionary is checked for validity. The
following checks are performed on each check:
  * All required keys are present: `id in_intf proto should src_ip dst_ip`.
    These keys are required regardless of the check type.
  * `should` is `"allow"` or `"drop"`
  * All conditional keys are present
    * `src_port` and `dst_port` for TCP/UDP
    * `icmp_type` and `icmp_code` for ICMP
  * `src_ip` and `dst_ip` are valid IPv4 or IPv6 addresses
  * `src_ip` and `dst_ip` are using the same IP version (both v4 or both v6)
  * `src_port` and `dst_port` are integers in the range 0-65535 when present
  * `icmp_type` and `icmp_code` are integers in the range 0-255 when present
  * `proto` is one of the following:
    * A string equal to `"tcp"`, `"udp"`, or `"icmp"`
    * An integer in the range 0-255 (uses the `rawip` ASA protocol option)

Once the individual checks are validated, one final test ensures
that there are no duplicate `id` fields across any checks.

## Output Formats
In the past, this program gave the user many options regarding formats. Those
options are gone, replaced by the following actions.
  1. A terse, text-based output is written to a file named `outputs/result.txt` 
     The format is: `{host} {check id} -> {PASS or FAIL}`
     The final field measures whether the actual result matched the intended
     result. Rules that have `should: allow` that actually result in `ALLOW`
     receive a `PASS`. Rules with `should: drop` that actually `DROP` also get a
     `PASS`. Any other combination receives a `FAIL`, indicating a mismatch
     between intent and reality.
  2. To provide additional detail, a CSV-formatted string is written to a file
     name `outputs/result.csv`. This option displays a superset of the data in
     the "terse" format. The output includes column headers as well,
     simplifying shell redirection to output files. The command
     below is a handy way to view CSV files from the shell (use arrows to pan):
     `column -s, -t outputs/result.csv | less -S`
  3. Finally, the program returns the results as structured data in
     JSON format to `outputs/result.json`. This data is largely unchanged,
     with the exception of wrapping all of a given host's results under a
     subdictionary with a key equal to the check `id` field. Note that
     this output is verbose and explains every processing phase of the
     firewall for a given simulation. 

## Other Options
To improve usability, the tool offers some command-line options:

  * To reduce the output generated, users may opt to only see the failures. Use
   `-f` or `--failonly` to apply this filter, which is handy on large
   `check` lists. Note that this affects the terse, CSV, and JSON formats.
  * Some users prefer to see status updates as the script runs. Use
    `-s` or `--status` to enable logging to `stdout` in the following format:
    {hostname}@{utc_timestamp}: {msg}

Here are some example outputs to demonstrate these options.

```
$ python runbook.py && cat outputs/result.txt
ASAV1        DNS OUTBOUND             -> FAIL
ASAV1        HTTPS OUTBOUND           -> PASS
ASAV1        SSH INBOUND              -> PASS
ASAV1        PING OUTBOUND            -> PASS
ASAV1        L2TP OUTBOUND            -> PASS
ASAV2        DNS OUTBOUND             -> PASS
ASAV2        HTTPS OUTBOUND           -> FAIL
ASAV2        SSH INBOUND              -> PASS
ASAV2        PING OUTBOUND            -> PASS
ASAV2        L2TP OUTBOUND            -> PASS

$ python runbook.py --failonly && cat outputs/result.txt
ASAV1        DNS OUTBOUND             -> FAIL
ASAV2        HTTPS OUTBOUND           -> FAIL

$ python runbook.py --status
ASAV1@2019-12-31T18:37:57.975656: loading YAML vars
ASAV1@2019-12-31T18:37:57.978265: loading vars succeeded
ASAV1@2019-12-31T18:37:57.978427: starting  check DNS OUTBOUND (1/5)
ASAV2@2019-12-31T18:37:57.978814: loading JSON vars
ASAV2@2019-12-31T18:37:57.978965: loading vars succeeded
ASAV2@2019-12-31T18:37:57.979099: starting  check DNS OUTBOUND (1/5)
ASAV1@2019-12-31T18:38:03.976345: completed check DNS OUTBOUND (1/5)
ASAV1@2019-12-31T18:38:03.976397: starting  check HTTPS OUTBOUND (2/5)
ASAV2@2019-12-31T18:38:04.076485: completed check DNS OUTBOUND (1/5)
ASAV2@2019-12-31T18:38:04.076538: starting  check HTTPS OUTBOUND (2/5)
ASAV1@2019-12-31T18:38:04.578326: completed check HTTPS OUTBOUND (2/5)
ASAV1@2019-12-31T18:38:04.578377: starting  check SSH INBOUND (3/5)
ASAV2@2019-12-31T18:38:04.678691: completed check HTTPS OUTBOUND (2/5)
ASAV2@2019-12-31T18:38:04.678740: starting  check SSH INBOUND (3/5)
ASAV1@2019-12-31T18:38:05.180719: completed check SSH INBOUND (3/5)
ASAV1@2019-12-31T18:38:05.180774: starting  check PING OUTBOUND (4/5)
ASAV2@2019-12-31T18:38:05.280919: completed check SSH INBOUND (3/5)
ASAV2@2019-12-31T18:38:05.280967: starting  check PING OUTBOUND (4/5)
ASAV1@2019-12-31T18:38:05.782703: completed check PING OUTBOUND (4/5)
ASAV1@2019-12-31T18:38:05.782752: starting  check L2TP OUTBOUND (5/5)
ASAV2@2019-12-31T18:38:05.883009: completed check PING OUTBOUND (4/5)
ASAV2@2019-12-31T18:38:05.883055: starting  check L2TP OUTBOUND (5/5)
ASAV1@2019-12-31T18:38:06.384632: completed check L2TP OUTBOUND (5/5)
ASAV2@2019-12-31T18:38:06.485029: completed check L2TP OUTBOUND (5/5)
```

## Limitations
To keep things simple (for now), the tool has some limitations:
  1. Only source and destination IP matches are supported.
  2. All YAML var files must use `.yaml`, not `.yml`, as their
     file extensions. This minimizes Nornir modifications.

## Testing
This project is extensively tested.

### Regression
A GNU `Makefile` is used to automate testing with the following targets:
  * `lint`: Runs `yamllint` and `pylint` linters, a custom JSON linter,
    and the `black` formatter
  * `unit`: Runs unit tests on helper functions via `pytest`.
  * `dry`: Runs a series of local tests to ensure the code works. These
    do not communicate with any ASAs and are handy for regression testing
  * `clean`: Deletes any artifacts, such as `.pyc`, `.log`, and `output/` files
  * `all`: Default target that runs the sequence `clean lint unit dry`

### Scalability/performance
It is unlikely that this project will be run on a large number of inventory
devices. That is, the number of ASAs in scope is likely to be small. However,
the length of the `checks` list for each ASA is likely to be large, especially
for more complex rulesets. The outputs below provide some "wall clock"
completion times for a variety of `checks` list lengths.


