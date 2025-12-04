## Running command

* Command1: get the model composed with fault injector and monitor
```
sh trans-script/run.sh dns.maude init-dns.maude fault-dns.maude event-dns.maude
```

* Command2: get the model composed with fault injector and monitor, and do SMC by PVeStA

```
sh trans-script/run.sh --pvesta -l serverlist -m pvesta-test.maude -f latency.quatex -a 0.01 dns.maude init-dns.maude fault-dns.maude event-dns.maude
```

Example SMC running result of command 2(in file result.txt)
```
Confidence (alpha): 0.01
Threshold (delta): 0.01
Samples generated: 60
SMC result: 6000.000053963677
Memory usage: 128.586 MB
F&M-trans time used: 0.026716 seconds
SMC time used: 3.628904 seconds
Total time used: 3.655620 seconds
```


## Simulation running command

single simulation of f-output

```
sh test-script/fg-test.sh f-output
```

multiple simulations of f-output, from 0 to 1000 with step 100
```
sh run-result-simu.sh 0.0 1000.0 100.0
```

## Command for only use PVeStA
start the PVeStA server
```
java -jar ../pvesta/pvesta-server.jar > server.out &
```
run the PVeStA client and do SMC
```
java -jar ../pvesta/pvesta-client.jar -l serverlist -m pvesta-test.maude -f latency.quatex -a 0.01 > pvesta-output.txt
```