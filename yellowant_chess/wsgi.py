"""
WSGI config for yellowant_todoapp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os
import subprocess


from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yellowant_chess.settings")

DEV_ENV = os.environ.get("ENV")
print(DEV_ENV)
if DEV_ENV == "heroku":
    os.system('echo "from django.contrib.auth.models import User; User.objects.create_superuser(\'admin\', \'admin@example.com\', \'pass\')" | python manage.py shell')
    #subprocess.call(['chmod 777 yellowant_chess/engine.sh'])
    #os.chmod('/app/stockfish/Linux/stockfish-9',0o777)
    os.system("/app/yellowant_chess/engine.sh")
    subprocess.call(['yellowant_chess/engine.sh'])


    #subprocess.call(['yellowant_chess/engine.sh'])

application = get_wsgi_application()

