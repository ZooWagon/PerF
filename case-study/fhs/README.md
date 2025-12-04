## Running command for model transformation

* Command1: get the model composed with fault injector and monitor
```
sh trans-script/run.sh fhs.maude init-fhs.maude fault-fhs.maude event-fhs.maude
```

## Simulation running command

The command generates results under equivocation fault, with equivocation node number from 0 to 5. Then it generates results under equivocation and network partition fault together, also with equivocation node number from 0 to 5. 
The running time is about two hour.
See file result-simu.txt for our example running results.
```
sh run-result-simu.sh > result-simu.txt
```
