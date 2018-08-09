import asyncio
from jsonrpc2 import JsonRpc
import os
import json

interface = 'eth0'

ports_map = {
    '5100': {'status': 'idle', 'test_number': 0},
    '5200': {'status': 'idle', 'test_number': 0},
    '5300': {'status': 'idle', 'test_number': 0},
    '5400': {'status': 'idle', 'test_number': 0}
}

def start(port, test_number):
    """
    Start tcpdump to monitoring incoming data and iperf server.
    :param port: port of traffic generation
    :param test_number: test round
    :return: current status
    """
    cmd = "tcpdump -i {} port {} -vvv -ttt -c 19500 -w tcpdump_server_{}_{}.pcap &".format(interface, port, port, test_number)
    os.system(cmd)
    cmd = "iperf -s -u -i 1 -f k -p {} > iperf_server_{}_{}.txt &".format(port, port, test_number)
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
    return {'status': ports_map[str(port)]['status']}

def stop(port):
    """
    Stop tcpdump and iperf server.
    :param port: port of traffic generation
    :return: current status
    """
    cmd = "ps axf | grep iperf | grep {} | grep -v grep | awk '{print \"kill -9 \" $1}'" % port
    os.system(cmd)
    cmd = "ps axf | grep tcpdump | grep {} | grep -v grep | awk '{print \"kill -9 \" $1}'" % port
    os.system(cmd)
    ports_map[str(port)]['status'] = 'stopped'
    stop_test = True
    for station in ports_map:
        if ports_map[station]['status'] != 'stopped':
            stop_test = False
            break
    if stop_test:
        for station in ports_map:
            ports_map[station]['status'] = 'idle'
            ports_map[station]['test_number'] += 1
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
