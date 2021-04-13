from astmanager import AstManager
from itopmanager import iTopManager


itop_user='restclient'
itop_pw='XrcKpT23jYDfxN6'
itop_host='192.168.0.33'
itop_port='8080'
ast_username='itop'
ast_secret='23zcgjxDrqvBA3PfwjwY'
ast_host='192.168.0.51'
ast_prefix='/asterisk'
queue='6002'

i = iTopManager(itop_user, itop_pw, host=itop_host, port=itop_port)
qmembers_sched=i.get_scheduled_members()
qmembers_sched

a = AstManager(ast_username, ast_secret, host=ast_host, prefix=ast_prefix)
a.login()
current_members = a.get_queue_members(queue)

add = []
for i in qmembers_sched:
    if i not in current_members:
        a.add_member(queue, "IAX2/%s" % i)

remove = []              
for i in current_members:
    if i not in qmembers_sched:
        a.remove_member(queue, "IAX2/%s" % i)
