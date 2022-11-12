import logging

from proxmoxer import ProxmoxAPI

ip = "10.10.10.10"
node_name = "dev-pve01"
password = "password"

logging.basicConfig()
loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
for logger in loggers:
    logger.setLevel(logging.DEBUG)

# prox = ProxmoxAPI(ip, user="root", password=password, backend="ssh_paramiko")
prox = ProxmoxAPI(ip, user="root@pam", password=password, verify_ssl=False)
node = prox.nodes(node_name)
print(prox.version.get())
print(prox.nodes.get())

upid = node.storage("local").upload.post(
    content="vztmpl",
    filename=open("/workspaces/proxmoxer/alpine-3.16-default_20220622_amd64.tar.xz", "rb"),
)

res = None
while True:
    res = node.tasks(upid).status.get()
    if res["status"] != "running":
        break

print(res)
print(node.tasks(upid).log.get())
