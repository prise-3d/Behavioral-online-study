#! /bin/bash

username=$(cat credentials.json | python -c "import sys, json; print(json.load(sys.stdin)['username'])")
password=$(cat credentials.json | python -c "import sys, json; print(json.load(sys.stdin)['password'])")
email=$(cat credentials.json | python -c "import sys, json; print(json.load(sys.stdin)['email'])")
echo "from django.contrib.auth.models import User; User.objects.create_superuser('${username}', '${email}', '${password}')" | python manage.py shell