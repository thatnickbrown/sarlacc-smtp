#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""accepts all smtp messages and records them, useful for honeypots"""

import asyncio # needed for "async def"
from aiosmtpd.controller import Controller
import toml
import yaml
import argparse
import signal
import time

#TODO add a configuration file
FORMAT = 'toml' # or 'yaml'
LOGDIR = './'
SERVERID = "email server"
#TODO support the unix mailbox format as in 
# https://aiosmtpd.readthedocs.io/en/latest/handlers.html

class EmailInhaler:
    """provides a hook to the aiosmtp that saves messages to disk"""

    async def handle_DATA(self, server, session, envelope):
        msgdict = { 'From': envelope.mail_from,
                    'To': envelope.rcpt_tos,
                    'message': envelope.content.decode().strip(),
        }

        # write the message to disk
        file_name = LOGDIR+str(time.time_ns())+'.'+FORMAT
        with open(file_name, 'w') as msg_file:
            if FORMAT=='toml':            
                msg_file.write(toml.dumps(msgdict))
            elif FORMAT=='yaml':
                msg_file.write(yaml.dump(msgdict))
            else:
                exit("Invalid format specified.")
        return '250 Message will be devoured'        

def get_arguments():
    """parses the command line arguments

    Returns:
        argparse.Namespace: parsed command line arguments
    """
    description="sarlacc-smtp consumes any message thrown at it "\
    +"and writes it to disk."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-a', '--address', default='')
    parser.add_argument('-p', '--port', default=10025)
    return parser.parse_args()

def main():
    """starts the smtp server"""
    args = get_arguments()
    print("creating email server controller")
    cont = Controller(EmailInhaler(), server_hostname=SERVERID, hostname=args.address, port=args.port)
    print(f"starting email server controller")
    cont.start()
    print(f"sarlacc-smtp is listening on port {args.port}")
    signal.sigwait([signal.SIGINT, signal.SIGQUIT])
    print("stopping email server controller")
    cont.stop()


if __name__ == "__main__":
    main()
