from fabric.operations import local



def create_dbuser():
    local("sudo -u postgres psql -c \"CREATE USER crowdly WITH PASSWORD 'crowdly';\"")

def create_db(db='crowdly'):
    # Local
    local("sudo -u postgres dropdb --if-exists " + db + "")
    local("sudo -u postgres createdb " + db + "")
    local("sudo -u postgres psql -c \"GRANT ALL ON DATABASE " + db + " to crowdly;\"")


def run():
    local("python crowdly/manage.py runserver 0.0.0.0:7878 --settings=crowdly.settings")


def makemigrations():
    local("python crowdly/manage.py makemigrations")


def update_db():
    local("python crowdly/manage.py migrate")


def create_cache():
    local("python crowdly/manage.py createcachetable")


def create_superuser():
    local("python crowdly/manage.py runscript create_superuser")


def install_proj():
    create_dbuser()
    create_db()
    makemigrations()
    update_db()
    create_cache()
    create_superuser()

