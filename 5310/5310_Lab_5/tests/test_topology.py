import os
import pytest


mininet = pytest.importorskip(
    "mininet", reason="Mininet not installed; skipping topology tests")


def test_topology_import_and_build():
    # Basic smoke test: can we import the topology class and instantiate it?
    from topology import TutorialTopology

    topo = TutorialTopology()
    assert topo is not None


# @pytest.mark.slow
def test_mininet_connectivity_smoke():
    """
    Optional integration test. Requires:
    - Mininet installed
    - Root privileges
    - RUN_MININET_TESTS=1 in the environment
    """
    if os.environ.get("RUN_MININET_TESTS") != "1":
        pytest.skip(
            "Set RUN_MININET_TESTS=1 to enable Mininet integration test")

    if os.geteuid() != 0:
        pytest.skip("Root privileges required for Mininet")

    from mininet.net import Mininet
    from topology import TutorialTopology
    from mininet.nodelib import LinuxBridge
    from mininet.link import TCLink

    topo = TutorialTopology()
    net = Mininet(topo=topo, controller=None, autoSetMacs=True,
                  build=True, switch=LinuxBridge, link=TCLink,
                  cleanup=True)
    try:
        net.start()
        result = net.pingAllFull()
        for (_, _, (_, _, _, _, _, loss)) in result:
            assert loss < 1.0
    finally:
        net.stop()
