import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,'/var/www/html/filmlandia/')
 
from app import app as application
application.secret_key = 'ultramegahiperdificil'
