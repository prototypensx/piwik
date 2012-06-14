#!/usr/bin/python
"""Set Piwik admin password, email and domain

Option:
    --pass=     unless provided, will ask interactively
    --email=    unless provided, will ask interactively
    --domain=   unless provided, will ask interactively
                DEFAULT=www.example.com

"""

import re
import sys
import getopt
import hashlib

from dialog_wrapper import Dialog
from mysqlconf import MySQL
from executil import system

def usage(s=None):
    if s:
        print >> sys.stderr, "Error:", s
    print >> sys.stderr, "Syntax: %s [options]" % sys.argv[0]
    print >> sys.stderr, __doc__
    sys.exit(1)

DEFAULT_DOMAIN="www.example.com"

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h",
                                       ['help', 'pass=', 'email=', 'domain='])
    except getopt.GetoptError, e:
        usage(e)

    password = ""
    email = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--pass':
            password = val
        elif opt == '--email':
            email = val
        elif opt == '--domain':
            domain = val

    if not password:
        d = Dialog('TurnKey Linux - First boot configuration')
        password = d.get_password(
            "Piwik Password",
            "Enter new password for the Piwik 'admin' account.")

    if not email:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        email = d.get_email(
            "Piwik Email",
            "Enter email address for Piwik 'admin' account.",
            "admin@example.com")

    if not domain:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        domain = d.get_input(
            "Piwik Domain",
            "Enter the domain to serve Piwik.",
            DEFAULT_DOMAIN)

    if domain == "DEFAULT":
        domain = DEFAULT_DOMAIN

    domain = domain.strip("/")
    if not domain.startswith("http://"):
        domain = "http://%s/" % domain

    m = MySQL()
    m.execute('UPDATE piwik.piwik_option SET option_value=\"%s\" WHERE option_name=\"piwikUrl\";' % domain)

    hash = hashlib.md5(password).hexdigest()

    config = "/var/www/piwik/config/config.ini.php"
    s = file(config).read()
    s = re.sub("email.*", "email = \"%s\"" % email, s)
    s = re.sub("password.*", "password = \"%s\"" % hash, s, count=1)
    file(config, "w").write(s)

    # set ownership and permissions
    system("chown www-data:www-data %s" % config)
    system("chmod 640 %s" % config)


if __name__ == "__main__":
    main()
