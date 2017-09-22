from django.contrib.auth.models import User


def run():
    ###
    try:
        u = User.objects.create_superuser('admin', 'info@crowdly.com', 'admin')
    except:
        print "Already created"
        
    ####
    # try:
    #     email = EmailAddress.objects.create(user=u, email=u.email, verified=True, primary=True)
    # except:
    #     print "Problem in email setup"
    #
    # try:
    #     email = EmailAddress.objects.create(user=u, email=u.email, verified=True, primary=True)
    # except:
    #     print "Problem in email setup :"

        
    ####
    #
    # try:
    #     site = Site.objects.get(pk=1)
    #     site.name = 'demo.cloudmatix.com'
    #     site.domain = 'cloudmatix.com'
    #     site.save()
    # except:
    #     print "Error in setup of site"
