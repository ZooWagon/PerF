## Running command

* Command1: get the model composed with fault injector and monitor
```
sh trans-script/run.sh ramp-f.maude init-ramp-f.maude fault-ramp-f.maude event-ramp-f.maude
```

* Command2: get the model composed with fault injector and monitor, and do SMC by PVeStA

```
sh trans-script/run.sh --pvesta -l serverlist -m ana1-ramp-f.maude -f latency.quatex -a 0.01 ramp-f.maude init-ramp-f.maude fault-ramp-f.maude event-ramp-f.maude 
```

Example SMC running result of command 2(in file result.txt)
```
Confidence (alpha): 0.01
Threshold (delta): 0.01
Samples generated: 3900
SMC result: 9.163624188269237
Memory usage: 224.461 MB
F&M-trans time used: 0.028705 seconds
SMC time used: 85.242224 seconds
Total time used: 85.270929 seconds
```


## Command for only use PVeStA
start the PVeStA server
```
java -jar ../pvesta/pvesta-server.jar > server.out &
```
run the PVeStA client and do SMC
```
java -jar ../pvesta/pvesta-client.jar -l serverlist -m ana1-ramp-f.maude -f latency.quatex -a 0.01 > pvesta-output.txt
```

## Simulation running command
This command will generate result of ramp-f's average latency with the initial configuration pf 50% read txn and 50% write txn. Msg loss rate is from 0.1 to 0.3 with step 0.1 .
Example simulation running result is in file result-simu.txt
```
sh run-simu-50.sh 0.1 0.3 0.1
```
