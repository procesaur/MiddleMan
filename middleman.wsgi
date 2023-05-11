import sys
from os import system
sys.path.insert(0, '/var/www/MiddleMan')
system("rq worker > /dev/null")
from main import app as application