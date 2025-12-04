## Running command for model transformation

* Command1: get the model composed with fault injector and monitor
```
sh trans-script/run.sh quorum.maude init-quorum.maude fault-quorum-pa.maude event-quorum.maude
```

## Simulation running command

The command generates results under network partition fault, with partition duration time from 0 to 25 step 5.
See file result-simu.txt for our example running results.
```
sh run-result-simu-partition.sh
```
