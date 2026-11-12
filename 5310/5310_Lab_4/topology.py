from mininet.topo import Topo


class TutorialTopology(Topo):

    def build(self):
        # add two host to the network
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        # add a switch to the network
        s1 = self.addSwitch('s1')

        # add a link between the hosts `h1` and `h2` and the `s1` switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)


# the topologies accessible to the mn tool's `--topo` flag
# You can run this topology using the command:
# mn --custom topology.py --topo tutorialTopology --controller none --mac --switch lxbr
topos = {'tutorialTopology': (lambda: TutorialTopology())}
