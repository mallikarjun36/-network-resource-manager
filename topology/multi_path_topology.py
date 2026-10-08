from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel


def create_network():
    net = Mininet(
        controller=None,
        link=TCLink
    )

    print("*** Adding hosts")
    h1 = net.addHost("h1")
    h2 = net.addHost("h2")

    print("*** Adding switches")
    s1 = net.addSwitch("s1", failMode="standalone")
    s2 = net.addSwitch("s2", failMode="standalone")
    s3 = net.addSwitch("s3", failMode="standalone")
    s4 = net.addSwitch("s4", failMode="standalone") 

    print("*** Adding Path A")
    net.addLink(h1, s1, bw=100, delay="1ms")
    net.addLink(s1, s2, bw=50, delay="10ms")
    net.addLink(s2, s4, bw=50, delay="10ms")

    print("*** Adding Path B")
    net.addLink(s1, s3, bw=30, delay="15ms")
    net.addLink(s3, s4, bw=30, delay="15ms")

    net.addLink(h2, s4, bw=100, delay="1ms")

    print("*** Starting network")
    net.start()

    print("\n*** Network topology started")
    print("*** Path A: 50 Mbps")
    print("*** Path B: 30 Mbps")
    print("*** Type 'nodes' to see the network")
    print("*** Type 'links' to see the links")
    print("*** Type 'exit' to stop\n")

    CLI(net)

    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    create_network()