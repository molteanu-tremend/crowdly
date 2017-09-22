from fabric.operations import local


def create_db(db='crowdly'):
    # Local
    local("sudo -u postgres psql -c \"CREATE USER crowdly WITH PASSWORD 'crowdly';\"")
    local("sudo -u postgres dropdb --if-exists " + db + "")
    local("sudo -u postgres createdb " + db + "")
    local("sudo -u postgres psql -c \"GRANT ALL ON DATABASE " + db + " to crowdly;\"")


def run():
    local("python crowdly/manage.py runserver 0.0.0.0:5555 --settings=crowdly.settings")


def makemigrations():
    local("python crowdly/manage.py makemigrations")


def update_db():
    local("python crowdly/manage.py migrate")


def create_cache():
    local("python crowdly/manage.py createcachetable")