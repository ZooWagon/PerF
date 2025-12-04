# Running Example: 2PC
In paper's Appendix A.

## Running command

* Command 1: get the model composed with fault injector only
```
sh run.sh 2pc.maude init-2pc.maude 2pc-fault-config.maude
```

* Command 2: get the model composed with fault injector and monitor, and do SMC by PVeStA

```
sh run.sh --pvesta -l serverlist -m analysis-2pc.maude -f latency.quatex -a 0.01 -d 0.01 2pc.maude init-2pc.maude 2pc-fault-config.maude event-2pc.maude
```

* Command 3: get the model composed with fault injector and monitor
```
sh run.sh 2pc.maude init-2pc.maude 2pc-fault-config.maude event-2pc.maude
```

## Example running result
See file result.txt
```
Confidence (alpha): 0.01
Threshold (delta): 0.01
Samples generated: 600
SMC result: 1.1308343837856487
Memory usage: 85.578 MB
Model composition and transformation time used: 0.002770 seconds
SMC time used: 2.270604 seconds
Total time used: 2.273374 seconds
```

## Command for only use PVeStA
start PVeStA server
```
java -jar ./tool/pvesta/pvesta-server.jar > server.out &
```
start PVeStA client and do SMC
```
java -jar ./tool/pvesta/pvesta-client.jar -l serverlist -m analysis-2pc.maude -f latency.quatex -a 0.01 -d1 0.01 > pvesta-output.txt
```

