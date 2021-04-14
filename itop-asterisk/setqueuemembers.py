from astmanager import AstManager
from itopmanager import iTopManager
import config
import sys

if len(sys.argv) != 2:
    print("Usage: %s <queue number>" % sys.argv[0])
    exit(1)

queue = sys.argv[1]
i = iTopManager(config.itop_user, config.itop_pw, 
    host=config.itop_host, port=config.itop_port)
qmembers_sched=i.get_scheduled_members()
qmembers_sched

a = AstManager(config.ast_username, config.ast_secret, host=config.ast_host, prefix=config.ast_prefix)
a.login()
current_members = a.get_queue_members(queue)

add = []
for i in qmembers_sched:
    if i not in current_members:
        a.add_member(queue, "IAX2/%s" % i)
        print("Adding %s to %s" % (i, queue))

remove = []              
for i in current_members:
    if i not in qmembers_sched:
        a.remove_member(queue, "IAX2/%s" % i)
        print("Removing %s from %s" % (i, queue))
