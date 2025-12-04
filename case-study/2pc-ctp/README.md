## Running command

* Command1: get the model composed with fault injector and monitor
```
sh trans-script/run.sh 2pc-ctp.maude init-2pc-ctp.maude fault-ml.maude event-2pc-ctp.maude
```

* Command2: get the model composed with fault injector and monitor, and do SMC by PVeStA

```
sh trans-script/run.sh --pvesta -l serverlist -m test-m.maude -f latency.quatex -a 0.01 2pc-ctp.maude init-2pc-ctp.maude fault-ml.maude event-2pc-ctp.maude
```

Example SMC running result of command 2(in file result.txt)
```
Confidence (alpha): 0.01
Threshold (delta): 0.01
Samples generated: 2280
SMC result: 3.6453422593423057
Memory usage: 21.410 MB
F&M-trans time used: 0.005825 seconds
SMC time used: 130.422559 seconds
Total time used: 130.428384 seconds
```

## Command for only use PVeStA
start the PVeStA server
```
java -jar ../pvesta/pvesta-server.jar > server.out &
```
run the PVeStA client and do SMC
```
java -jar ../pvesta/pvesta-client.jar -l serverlist -m test-m.maude -f latency.quatex -a 0.01 > pvesta-output.txt
```

