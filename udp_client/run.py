import subprocess

commands = [
    "python -m udp_client.main --requests 10000 --save-results",
    "python -m udp_client.main --session --requests 10000 --save-results",
    "python -m udp_client.main --session --print --requests 10000 --save-results",
    "python -m udp_client.main --session --file --requests 10000 --save-results",
    "python -m udp_client.main --print --requests 10000 --save-results",
    "python -m udp_client.main --print --file --requests 10000 --save-results",
    "python -m udp_client.main --file --requests 10000 --save-results",
    "python -m udp_client.main --session --print --file --requests 10000 --save-results"
]

for command in commands:
    for _ in range(10):
        subprocess.run(command, shell=True)
