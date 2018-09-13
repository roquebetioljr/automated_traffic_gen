import asyncio
from jsonrpc2 import JsonRpc
import os
import json

interface = 'eth0'

ports_map = {
    '5100': {'status': 'idle', 'type': 'RT'},
    '5200': {'status': 'idle', 'type': 'RT'},
    '5300': {'status': 'idle', 'type': 'RT'},
    '5400': {'status': 'idle', 'type': 'RT'},
    '5500': {'status': 'idle', 'type': 'NRT'},
    '5600': {'status': 'idle', 'type': 'NRT'},
}

roadmap = [
    {'RT': {'data_rate': 1375}, 'NRT': {'data_rate': 0}, 'repetitions': 30},
    {'RT': {'data_rate': 1375}, 'NRT': {'data_rate': '337k'}, 'repetitions': 30},
    {'RT': {'data_rate': 1375}, 'NRT': {'data_rate': '675k'}, 'repetitions': 30},
    {'RT': {'data_rate': 1375}, 'NRT': {'data_rate': '1012k'}, 'repetitions': 30},
    {'RT': {'data_rate': 1375}, 'NRT': {'data_rate': '1350k'}, 'repetitions': 30},
    {'RT': {'data_rate': 1375}, 'NRT': {'data_rate': '1687k'}, 'repetitions': 30},
    {'RT': {'data_rate': 1375}, 'NRT': {'data_rate': '2025k'}, 'repetitions': 30},
    {'RT': {'data_rate': 1375}, 'NRT': {'data_rate': '2362k'}, 'repetitions': 30},
    {'RT': {'data_rate': 1375}, 'NRT': {'data_rate': '2700k'}, 'repetitions': 30},
    {'RT': {'data_rate': 1375}, 'NRT': {'data_rate': '3037k'}, 'repetitions': 30},
    {'RT': {'data_rate': 1375}, 'NRT': {'data_rate': '3375k'}, 'repetitions': 30},
    {'RT': {'data_rate': 2750}, 'NRT': {'data_rate': 0}, 'repetitions': 30},
    {'RT': {'data_rate': 2750}, 'NRT': {'data_rate': '337k'}, 'repetitions': 30},
    {'RT': {'data_rate': 2750}, 'NRT': {'data_rate': '675k'}, 'repetitions': 30},
    {'RT': {'data_rate': 2750}, 'NRT': {'data_rate': '1012k'}, 'repetitions': 30},
    {'RT': {'data_rate': 2750}, 'NRT': {'data_rate': '1350k'}, 'repetitions': 30},
    {'RT': {'data_rate': 2750}, 'NRT': {'data_rate': '1687k'}, 'repetitions': 30},
    {'RT': {'data_rate': 2750}, 'NRT': {'data_rate': '2025k'}, 'repetitions': 30},
    {'RT': {'data_rate': 2750}, 'NRT': {'data_rate': '2362k'}, 'repetitions': 30},
    {'RT': {'data_rate': 2750}, 'NRT': {'data_rate': '2700k'}, 'repetitions': 30},
    {'RT': {'data_rate': 2750}, 'NRT': {'data_rate': '3037k'}, 'repetitions': 30},
    {'RT': {'data_rate': 2750}, 'NRT': {'data_rate': '3375k'}, 'repetitions': 30},
    {'RT': {'data_rate': 2750}, 'NRT': {'data_rate': 0}, 'repetitions': 30},
    {'RT': {'data_rate': 4125}, 'NRT': {'data_rate': '337k'}, 'repetitions': 30},
    {'RT': {'data_rate': 4125}, 'NRT': {'data_rate': '675k'}, 'repetitions': 30},
    {'RT': {'data_rate': 4125}, 'NRT': {'data_rate': '1012k'}, 'repetitions': 30},
    {'RT': {'data_rate': 4125}, 'NRT': {'data_rate': '1350k'}, 'repetitions': 30},
    {'RT': {'data_rate': 4125}, 'NRT': {'data_rate': '1687k'}, 'repetitions': 30},
    {'RT': {'data_rate': 4125}, 'NRT': {'data_rate': '2025k'}, 'repetitions': 30},
    {'RT': {'data_rate': 4125}, 'NRT': {'data_rate': '2362k'}, 'repetitions': 30},
    {'RT': {'data_rate': 4125}, 'NRT': {'data_rate': '2700k'}, 'repetitions': 30},
    {'RT': {'data_rate': 4125}, 'NRT': {'data_rate': '3037k'}, 'repetitions': 30},
    {'RT': {'data_rate': 4125}, 'NRT': {'data_rate': '3375k'}, 'repetitions': 30},
    {'RT': {'data_rate': 5500}, 'NRT': {'data_rate': 0}, 'repetitions': 30},
    {'RT': {'data_rate': 5500}, 'NRT': {'data_rate': '337k'}, 'repetitions': 30},
    {'RT': {'data_rate': 5500}, 'NRT': {'data_rate': '675k'}, 'repetitions': 30},
    {'RT': {'data_rate': 5500}, 'NRT': {'data_rate': '1012k'}, 'repetitions': 30},
    {'RT': {'data_rate': 5500}, 'NRT': {'data_rate': '1350k'}, 'repetitions': 30},
    {'RT': {'data_rate': 5500}, 'NRT': {'data_rate': '1687k'}, 'repetitions': 30},
    {'RT': {'data_rate': 5500}, 'NRT': {'data_rate': '2025k'}, 'repetitions': 30},
    {'RT': {'data_rate': 5500}, 'NRT': {'data_rate': '2362k'}, 'repetitions': 30},
    {'RT': {'data_rate': 5500}, 'NRT': {'data_rate': '2700k'}, 'repetitions': 30},
    {'RT': {'data_rate': 5500}, 'NRT': {'data_rate': '3037k'}, 'repetitions': 30},
    {'RT': {'data_rate': 5500}, 'NRT': {'data_rate': '3375k'}, 'repetitions': 30}
]

global current_repetition
global current_test_case
current_repetition = 0
current_test_case = 0

def start(port):
    """
    Start tcpdump to monitoring incoming data and iperf server.
    :param port: port of traffic generation
    :return: current status
    """
    global current_repetition
    global current_test_case
    st_type = ports_map[str(port)]['type']
    data_rate = roadmap[current_test_case][st_type]['data_rate']
    if st_type == 'RT':
        cmd = "bash server_start.sh {} {} {} {}".format("server_{}".format(data_rate), interface, port, current_repetition)
        os.system(cmd)
    ports_map[str(port)]['status'] = 'waiting'
    start_test = True
    for station in ports_map:
        if ports_map[station]['status'] != 'waiting':
            start_test = False
            break
    if start_test:
        for station in ports_map:
            ports_map[station]['status'] = 'run'
    return {'test_number': current_repetition,
            'data_rate' : data_rate,
            'status': ports_map[str(port)]['status']}

def stop(port):
    """
    Stop tcpdump and iperf server.
    :param port: port of traffic generation
    :return: current status
    """
    global current_repetition
    global current_test_case
    ports_map[str(port)]['status'] = 'stopped'
    stop_test = True
    for station in ports_map:
        if ports_map[station]['status'] != 'stopped':
            stop_test = False
            break
    if stop_test:
        cmd = "bash server_stop.sh"
        os.system(cmd)
        for station in ports_map:
            ports_map[station]['status'] = 'idle'
        current_repetition += 1
        if current_repetition == roadmap[current_test_case]['repetitions']:
            current_test_case += 1
            current_repetition = 0
            if current_test_case == len(roadmap):
                raise Exception('Test finished')
    return {'status': ports_map[str(port)]['status']}

def status(port):
    """
    Check current status
    :param port: port of traffic generation
    :return: current status
    """
    return {'status': ports_map[str(port)]['status']}

rpc = JsonRpc()
rpc['start'] = start
rpc['stop'] = stop
rpc['status'] = status


async def receive(reader, writer):
    """
    Handle received message from clients
    :param reader: socket reader component
    :param writer: socket writer component
    :return: None
    """
    data = await reader.read(500)
    message = data.decode()
    addr = writer.get_extra_info('peername')
    print("Received %r from %r" % (message, addr))
    message = json.loads(message)
    response = rpc(message)
    response = json.dumps(response)
    print("Send: %r" % response)
    writer.write(response.encode())
    await writer.drain()

    print("Close the client socket")
    writer.close()

loop = asyncio.get_event_loop()
coro = asyncio.start_server(receive, '127.0.0.1', 8888, loop=loop)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
