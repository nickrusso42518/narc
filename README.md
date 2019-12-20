# Nornir ASA Rule Checker
This simple program uses the Cisco ASA `packet-tracer` utility to test traffic
flows across the firewall. On a per-ASA basis, users specify a list of
simulations in YAML format. This program returns the result of those tests
in a variety of formats. Both IPv4 and IPv6 are supported.

## High-level Structure
This project is built on two powerful Python-based tools:
  1. Nornir, a task execution framework with concurrency support
  2. Netmiko, a library for accessing network device command lines


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
  - name: DNS OUTBOUND
    in_intf: inside
    proto: udp
    src_ip: 192.0.2.1
    src_port: 5000
    dst_ip: 8.8.8.8
    dst_port: 53
    should: allow
  - name: HTTPS OUTBOUND
    in_intf: inside
    proto: tcp
    src_ip: 192.0.2.1
    src_port: 5000
    dst_ip: 20.0.0.1
    dst_port: 443
    should: allow
  - name: SSH INBOUND
    in_intf: outside
    proto: tcp
    src_ip: 20.0.0.1
    src_port: 5000
    dst_ip: 192.0.2.1
    dst_port: 22
    should: drop
...
```

Note that it is uncommon for firewalls to filter traffic based on source port.
The `packet-tracer` utility requires specifying a value. Additionally, the
`name` key is useful for documentation to describe each check. This string
is also displayed in some of the output format styles.

## Output Formats
There are many output format style options. From the command line, use the
`-s` or `--style` options to choose. The default style is `terse`. Check the
`samples/` directory to see an example of each style.
  1. `terse`: This option displays a single line of output for each processed
     rule. The format is as follows:
     `{success} {proto} s={src_ip}/{src_port} d={dst_ip}/{dst_port} {in_intf}->{out_intf}: {result}`
     The `{success}` field measures whether the actual result matched the intended
     result. Rules that have `should: allow` that actually result in `ALLOW`
     receive a `+`. Rules with `should: drop` that actually `DROP` also get a
     `+`. Any other combination receives a `-`, indicating failure.
     This style does **not** include the `name` string or ASA drop reason.
  2. `csv`: This option displays a superset of the data in the `terse` format,
     except using comma-separated values. This includes column headers as well,
     simplifying shell redirection to output files. This option also includes
     the `name` key to provide additional context about each check. Example:
  3. `json`: This option displays the structured data returned by the ASA in
     JSON format. This data is largely unchanged, with the exception of
     adding a `name` key to the `result` dictionary. This copies the
     user-supplied `name` string to each test result. Note that this output
     is verbose and explains every processing phase of the firewall for
     a given simulation. Also, a Boolean-value `success` key is added to
     indicate whether a flow behaves as expected.

## Other Options
To improve usability, the tool offers some minor options:
  1. For each output format style, users may opt to only see the failures. Use
     `-f` or `--failonly` to apply this filter, which is handy on large
     checklists. It is also common to use the `terse` format to discover
     failures, then a more verbose format to diagnose/troubleshoot them.

## Limitations
To keep things simple (for now), the tool has some limitations:
  1. Only `tcp` and `udp` are supported options for `proto`
  2. Only source and destination IP matches are supported
  3. All keys in the `checks` directionaries must be specified,
     even if not relevant to a particular test (source check, etc.)
  4. All YAML files must use `.yaml`, not `.yml`, as their
     file extensions. This minimizes Nornir modifications

# notes
