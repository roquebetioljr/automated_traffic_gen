import asyncio
import json
import os
import time

global server_state
global test_number
global data_rate
global test_case
server_state = 'idle'
local_state = 'idle'
test_number = 0
test_case = 0
data_rate = None
local_port = int(input("Port (RT: 5100, 5200, 5300 or 5400) (NRT: 5500 or 5600): "))
interface = 'wlan0'
app_address = '150.162.57.167'
iperf_server = '192.168.1.1'

def mount_message(method, **params):
    return json.dumps({
        "jsonrpc": "2.0",
        "method": str(method),
        "params": params,
        "id": 1})


def ready_to_start():
    message = mount_message("start", port=local_port)
    return message, 'waiting'


def update_params(message):
    # example: '{"jsonrpc": "2.0", "id": 1, "result": {"test_number": 1, "data_rate": "1500", "status": "waiting", "test_case": 1}}'
    message = json.loads(message)
    global test_number
    global data_rate
    global server_state
    global test_case
    test_number = message['result']['test_number']
    data_rate = message['result']['data_rate']
    server_state = message['result']['status']
    test_case = message['result']['test_case']


def start_test():
    global test_number
    global data_rate
    global test_case
    if str(data_rate) != '0':
        cmd = "bash client.sh {} {} {} {} {} {}".format(
            "result_{}_{}_{}".format(local_port, data_rate, test_case),
            interface,
            iperf_server,
            local_port,
            data_rate,
            test_number)
        os.system(cmd)
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


async def transmmit(message, loop, receive_callback=None):
    reader, writer = await asyncio.open_connection(app_address, 8888,
                                                   loop=loop)

    print('Send: %r' % message)
    writer.write(message.encode())

    data = await reader.read(1500)
    print('Received: %r' % data.decode())
    if receive_callback is not None:
        receive_callback(data.decode())

    print('Close the socket')
    writer.close()


loop = asyncio.get_event_loop()

while 1:
    try:
        message = get_server_status()
        loop.run_until_complete(transmmit(message, loop, update_status))
        message = None
        print("Current server state: {}".format(server_state))
        print("Current local state: {}".format(local_state))
        callback = None

        if local_state == 'idle' and server_state == 'idle':
            message, local_state = ready_to_start()
            callback = update_params
        elif local_state == 'waiting' and server_state == 'waiting':
            print("Waiting other stations to start.")
        elif local_state == 'waiting' and server_state == 'run':
            message, local_state = start_test()
            callback = update_status
        elif local_state == 'run':
            print("It was not supposed to reach here!")
        elif local_state == 'stopped' and server_state == 'stopped':
            print("Waiting other stations to stop.")
        elif local_state == 'stopped' and server_state == 'idle':
            local_state = 'idle'
            print("Cooling down...")
            time.sleep(30)

        if message is not None:
            loop.run_until_complete(transmmit(message, loop, callback))

    except KeyboardInterrupt:
        break

loop.close()
