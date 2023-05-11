import sys
sys.path.insert(0, '/var/www/MiddleMan')
from os import system
system("rq worker &")
from main import app as application