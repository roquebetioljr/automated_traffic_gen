import asyncio
import json
import os

global server_state
server_state = 'idle'
local_state = 'idle'
curr_test_number = 0
local_port = int(input("Port (5100, 5200, 5300 or 5400): "))
interface = 'eth0'
server_address = '127.0.0.1'


def mount_message(method, **params):
    return json.dumps({
        "jsonrpc": "2.0",
        "method": str(method),
        "params": params,
        "id": 1})

def ready_to_start(test_number):
    message = mount_message("start", port=local_port, test_number=test_number)
    return message, 'waiting'

def start_test(test_number):
    cmd = "tcpdump -i {} udp port 5100 -vvv -ttt -c 19500 -w tcpdump_{}_{}.pcap &".format(interface, local_port, test_number)
    os.system(cmd)
    cmd = "iperf -c {} -b 4950 -i 1 -f l -p {} > iperf_{}_{}.log".format(server_address, test_number, local_port, local_port)
    os.system(cmd)
    test_number += 1
    message = mount_message("stop", port=local_port)
    return message, 'stopped'


def get_server_status():
    message = mount_message("status", port=local_port)
    return message


def update_status(message):
    #example: '{"jsonrpc": "2.0", "id": 1, "result": {"status": "idle"}}'
    global server_state
    message = json.loads(message)
    server_state = message['result']['status']


async def transmmit(message, loop):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888,
                                                   loop=loop)

    print('Send: %r' % message)
    writer.write(message.encode())

    data = await reader.read(1500)
    print('Received: %r' % data.decode())
    update_status(data.decode())

    print('Close the socket')
    writer.close()


loop = asyncio.get_event_loop()

while 1:
    try:
        message = get_server_status()
        loop.run_until_complete(transmmit(message, loop))
        message = None
        print("Current server state: {}".format(server_state))
        print("Current local state: {}".format(local_state))

        if local_state == 'idle' and server_state == 'idle':
            message, local_state = ready_to_start(curr_test_number)
        elif local_state == 'waiting' and server_state == 'waiting':
            print("Waiting other stations to start.")
        elif local_state == 'waiting' and server_state == 'run':
            message, local_state = start_test(curr_test_number)
        elif local_state == 'run':
            print("It was not supposed to reach here!")
        elif local_state == 'stopped' and server_state == 'stopped':
            print("Waiting other stations to stop.")
        elif local_state == 'stopped' and server_state == 'idle':
            local_state = 'idle'
        if message is not None:
            loop.run_until_complete(transmmit(message, loop))

        #input()
    except KeyboardInterrupt:
        break

loop.close()
