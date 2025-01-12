import os
from pathlib import Path

from bytewax.dataflow import Dataflow
from bytewax.connectors.stdio import StdOutput
from bytewax.connectors.files import DirInput, DirOutput, FileInput, FileOutput

input_dir = Path("./sample_data/cluster/")
output_dir = Path("./cluster_out/")

def to_tuple(x):
    return tuple(map(str, x.split(',')))

flow = Dataflow()
flow.input("inp", DirInput(input_dir))
flow.map(str.upper)
flow.map(to_tuple)
flow.output("out", DirOutput(output_dir, 5, assign_file=int))


# We are going to use Waxctl, you can download it from https://bytewax.io/downloads
# Run these commands in your terminal to run a cluster of two containers:

# $ tar -C ./ -cvf cluster.tar examples
# $ waxctl dataflow deploy ./cluster.tar --name k8s-cluster --python-file-name examples/k8s_cluster.py -p2

# Each worker will read the files in
# ./examples/sample_data/cluster/*.txt which have lines like
# `one1`.

# They will then both finish and you'll see ./cluster_out/part_0
# and ./cluster_out/part_1 with the data that each process in the
# cluster wrote with the lines uppercased.

# To see that files in each container you can run these commands:

# kubectl exec -it k8s-cluster-0 -cprocess -- cat /var/bytewax/cluster_out/part_0.out
# kubectl exec -it k8s-cluster-1 -cprocess -- cat /var/bytewax/cluster_out/part_1.out

# You could imagine reading from / writing to separate Kafka
# partitions, S3 blobs, etc.

# When using `cluster_main()` you have to coordinate ensuring each
# process knows the address of all other processes in the cluster
# and their unique process ID. You can address that easily by deploying your
# dataflow program using Waxctl or installing the Bytewax Helm Chart
# cluster_main(flow, recovery_config=recovery_config, **parse.proc_env())
