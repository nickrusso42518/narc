[![Build Status](
https://travis-ci.org/nickrusso42518/narc.svg?branch=master)](
https://travis-ci.org/nickrusso42518/narc)

# Nornir ASA Rule Checker
This simple program uses the Cisco ASA `packet-tracer` utility to test traffic
flows across the firewall. On a per-ASA basis, users specify a list of
simulations in YAML format. This program returns the result of those tests
in a variety of formats. Both IPv4 and IPv6 are supported.

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
    src_ip: "8.8.8.8"
    src_port: 5000
    dst_ip: "192.0.2.2"
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
it as a raw IP packet, which can be desirable for generalized TCP testing
if you want to omit ports. The same is true for UDP and ICMP.

Note that it is uncommon for firewalls to filter traffic based on source port.
The `packet-tracer` utility requires specifying a value. Additionally, the
`id` key is useful for documentation to describe each check. This string
is also displayed in some of the output format styles.

## Output Formats
There are many output format style options. From the command line, use the
`-s` or `--style` options to choose. The default style is `terse`. Check the
`samples/` directory to see an example of each style.
  1. `terse`: This option displays a single line of output for each processed
     rule. The format is as follows:
     `{host} {check id} -> {PASS or FAIL}`
     The `{success}` field measures whether the actual result matched the intended
     result. Rules that have `should: allow` that actually result in `ALLOW`
     receive a "PASS". Rules with `should: drop` that actually `DROP` also get a
     "PASS". Any other combination receives a "FAIL", indicating a mismatch
     between intent and reality.
  2. `csv`: This option displays a superset of the data in the `terse` format,
     except using comma-separated values. This includes column headers as well,
     simplifying shell redirection to output files. This option also includes
     the `id` key to provide additional context about each check. The command
     below is a handy way to view CSV files from the shell:
     `column -s, -t output.csv | less -S`
  3. `json`: This option displays the structured data returned by the ASA in
     JSON format. This data is largely unchanged, with the exception of
     wrapping all of a given host's results under a subdictionary with a
     key equal to the check `id` field. Note that this output
     is verbose and explains every processing phase of the firewall for
     a given simulation. The output is generally unchanged and is simply the
     JSON representation of the XML data returned by the ASA.

## Other Options
To improve usability, the tool offers some minor options.

For each output format style, users may opt to only see the failures. Use
`-f` or `--failonly` to apply this filter, which is handy on large
checklists. It is also common to use the `terse` format to discover
failures, then a more verbose format to diagnose/troubleshoot them.

```
$ python runbook.py
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

$ python runbook.py --failonly
ASAV1        DNS OUTBOUND             -> FAIL
ASAV2        HTTPS OUTBOUND           -> FAIL
```

## Limitations
To keep things simple (for now), the tool has some limitations:
  1. Only source and destination IP matches are supported
  2. All YAML var files must use `.yaml`, not `.yml`, as their
     file extensions. This minimizes Nornir modifications

## Testing
A GNU `Makefile` is used to automate testing with the following targets:
  * `lint`: Runs `yamllint` and `pylint` linters, pls the `black` formatter
  * `unit`: Runs unit tests on helper functions via `pytest`. The `test_unit.py`
     file serves as the main entrypoint for unit tests in the `tests/` directory.
  * `dry`: Runs a series of local tests to ensure the code works. These
    do not communicate with any ASAs and are handy for regression testing
  * `clean`: Deletes any application artifacts, such as `.pyc` and `.log` files
  * `all`: Default target that runs the sequence `clean lint unit dry`
