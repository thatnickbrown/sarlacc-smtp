#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""accepts all smtp messages and records them, useful for honeypots"""

import asyncio
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult
import toml
import yaml
import argparse
import signal
import time
import os

FORMAT = 'toml' # or 'yaml'
LOG_DIR = 'smtp/'
# verify the directory it writs to exists
if not os.path.exists(LOG_DIR):
    print(f"Creating the directory {LOG_DIR} to store collected SMTP data.")
    os.mkdir(LOG_DIR)

#TODO 
# set up a configuration file
# support mbox format: https://aiosmtpd.readthedocs.io/en/latest/handlers.html

class InhaleAuthenticator:
    def __call__(self, server, session, envelope, mechanism, auth_data):
        msg_dict = {'smtp_command': 'AUTH',
                    # https://aiosmtpd.readthedocs.io/en/latest/concepts.html#Session
                    'peer': session.peer,
                    'ssl': session.ssl,
                    'host_name': session.host_name,
                    'extended_smtp': session.extended_smtp,
                    'auth_data': session.auth_data,
                    'authenticated': session.authenticated,
                    'auth_data_login': auth_data.login.decode(),
                    'auth_data_password': auth_data.password.decode(),
        }
        log_dict(msg_dict)
        return AuthResult(success=False,
                          handled=False,
                          message='535 5.7.8 Authentication credentials invalid')

class EmailInhaler:
    """provides a hook to the aiosmtp that saves messages, login info, and more"""

    async def handle_DATA(self, server, session, envelope):
        msg_dict = {'smtp_command': 'DATA',
                    # https://aiosmtpd.readthedocs.io/en/latest/concepts.html#Session
                    'peer': session.peer,
                    'ssl': session.ssl,
                    'host_name': session.host_name,
                    'extended_smtp': session.extended_smtp,
                    'auth_data': session.auth_data,
                    'authenticated': session.authenticated,
                    # https://aiosmtpd.readthedocs.io/en/latest/concepts.html#Envelope
                    'mail_from': envelope.mail_from,
                    'mail_options': envelope.mail_options,
                    'content': envelope.content.decode(),#.strip(),
                    'rcpt_tos': envelope.rcpt_tos,
                    'rcpt_options': envelope.rcpt_options,
        }
        log_dict(msg_dict)
        return '250 Message will be devoured'
    
    async def handle_EHLO(self, server, session, envelope, hostname, responses):
        """taunt the client with AUTH and VRFY, then log the ehlo hostname"""
        responses = [f'250-{server.hostname}',
                    f'250-SIZE {server.data_size_limit}',
                    f'250-8BITMIME',
                    f'250-SMTPUTF8',
                    f'250-VRFY',
                    f'250 AUTH LOGIN PLAIN',
                    f'250 HELP',
                    ]
        session.host_name = hostname
        msg_dict = {'smtp_command': 'EHLO',
                    # https://aiosmtpd.readthedocs.io/en/latest/concepts.html#Session
                    'peer': session.peer,
                    'ssl': session.ssl,
                    'host_name': session.host_name,
                    'extended_smtp': session.extended_smtp,
                    'auth_data': session.auth_data,
                    'authenticated': session.authenticated,
        }
        log_dict(msg_dict)
        return responses
    
    async def handle_VRFY(self, server, session, envelope, address):
        msg_dict = {'smtp_command': 'VRFY',
                    # https://aiosmtpd.readthedocs.io/en/latest/concepts.html#Session
                    'peer': session.peer,
                    'ssl': session.ssl,
                    'host_name': session.host_name,
                    'extended_smtp': session.extended_smtp,
                    'auth_data': session.auth_data,
                    'authenticated': session.authenticated,
                    'vrfy_address': address,
        }
        log_dict(msg_dict)
        return f'250 {address}' # asking for trouble

    async def handle_NOOP(self, server, session, envelope, arg):
        msg_dict = {'smtp_command': 'NOOP',
                    'noop_arg': arg,} # I have no idea why NOOP takes arguments
        log_dict(msg_dict)
        return '250 OK'

def log_dict(msg_dict: dict) -> None:
    """write the message to disk"""
    file_name = LOG_DIR+str(time.time_ns())+'.'+FORMAT
    with open(file_name, 'w') as log_file:
        if FORMAT=='toml':            
            log_file.write(toml.dumps(msg_dict))
        elif FORMAT=='yaml':
            log_file.write(yaml.dump(msg_dict))
        else:
            exit("Invalid logging format specified.")


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
    parser.add_argument('-n', '--hostname', default='workgroup.local')
    parser.add_argument('-i', '--ident', default='email server')
    parser.add_argument('-s', '--sizelimit', default=524288)
    parser.add_argument('-c', '--calllimit', default=50)
    return parser.parse_args()

def main():
    """starts the smtp server"""
    args = get_arguments()
    print("creating email server controller")
    cont = Controller(  EmailInhaler(),
                        data_size_limit=args.sizelimit,
                        command_call_limit=args.calllimit,
                        server_hostname=args.hostname,
                        ident=args.ident,
                        hostname=args.address,
                        port=args.port,
                        auth_require_tls=False,
                        authenticator=InhaleAuthenticator(),
                        )
    cont.local_part_limit=10
    print(f"starting email server controller")
    cont.start()
    print(f"sarlacc-smtp is listening on port {args.port}")
    signal.sigwait([signal.SIGINT, signal.SIGQUIT])
    print("stopping email server controller")
    cont.stop()


if __name__ == "__main__":
    main()
