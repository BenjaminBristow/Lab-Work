.PHONY: test

topo: topology.py
	mn --custom topology.py --topo tutorialTopology --controller none --mac --switch lxbr --link tc

test:
	apt install python3-pytest -y
	PYTHONPATH=`pwd` RUN_MININET_TESTS=1 pytest --verbosity=5 -q 

clean:
	mn -c