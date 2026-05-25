#!/usr/bin/env python3
import sys

from factor_mining_agent_lib.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["setup", *sys.argv[1:]]))
