## Running command

* Command1: get the model composed with fault injector and monitor
```
sh trans-script/run.sh raft.maude init-raft.maude fault-raft.maude event-raft.maude
```

* Command2: get the model composed with fault injector and monitor, and do SMC by PVeStA

```
sh trans-script/run.sh --pvesta -l serverlist -m test-m.maude -f electT.quatex -a 0.01 raft.maude init-raft.maude fault-raft.maude event-raft.maude 
```

Example SMC running result of command 2(in file result.txt)
```
Confidence (alpha): 0.01
Threshold (delta): 0.01
Samples generated: 60
SMC result: 11.777222167822824
Memory usage: 135.449 MB
F&M-trans time used: 0.008066 seconds
SMC time used: 57.544516 seconds
Total time used: 57.552582 seconds
```


## Command for only use PVeStA
start the PVeStA server
```
java -jar ../pvesta/pvesta-server.jar > server.out &
```
run the PVeStA client and do SMC
```
java -jar ../pvesta/pvesta-client.jar -l serverlist -m test-m.maude -f electT.quatex -a 0.01 > pvesta-output.txt
```

## Simulation running command
single simulation of m-output
```
sh test-script/fg-test.sh 100 m-output
```
