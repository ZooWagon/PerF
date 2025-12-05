# Running Example: The (Simplified) Two-Phase Commit Protocol

## Protocol

Two-Phase Commit (2PC)  is a distributed atomic commitment protocol that ensures all participants in a transaction either commit or abort. 

The Maude specification is in [2pc.maude](./input-modules/2pc.maude) with corresponding initial state in [init-2pc.maude](./input-modules/init-2pc.maude), in the directory [input-modules](./input-modules/).

The protocol starts from the coordinator initiating the proposal, 
then each cohort responds with its locally stored vote(yes or no) for it. 
Upon receiving a vote, the coordinator updates the aggregated decisions. 
Once all votes have been collected, the coordinator propagates the final decision and proceeds to issue the next proposal. 
Finally, the cohorts record the decision.

Note that this is a slightly simplified version of 2PC, in which a cohort is not required to acknowledge to the coordinator that it has received the decision.

## Configuring Fault Injection and Event Logging

PerF support seven faults to be injected by fault-injector, all defined in [fault-injector.maude](./fault-injector.maude).

We inject a message loss fault to the (simplified) 2PC protocol, with the fault configuration in [2pc-fault-config.maude](./input-modules/2pc-fault-config.maude), which drops the coordinator’s decision message to a cohort with rate 0.3. Note that this will not lead to a block in the simplified 2PC protocol.

We also record the starting and finishing time of a proposal, as specified in [event-2pc.maude](./input-modules/event-2pc.maude).

## Preparing for Statistical Model Checking (SMC)

The [latency.quatex](./latency.quatex) provides a QuaTEx expression of the desired metric, in this case, the average proposal latency.
Accordingly, the [analysis-2pc.maude](./analysis-2pc.maude) provides function to return the average proposal latency by dividing the total accumulated latency by the number of completed proposals.

## Running Command

* Command 1 : get the model composed with fault injector only, whose output is in directory [output-fault-comp](./output-fault-comp/).
```
sh run.sh 2pc.maude init-2pc.maude 2pc-fault-config.maude
```

* Command 2 : get the model composed with fault injector and monitor, whose output is in directory [out-moni-tran](./output-moni-tran/).
```
sh run.sh 2pc.maude init-2pc.maude 2pc-fault-config.maude event-2pc.maude
```

* Command 3 (full command): get the model composed with fault injector and monitor, and do statistical model checking(SMC) by calling PVeStA, whose output is shown below.

```
sh run.sh --pvesta -l serverlist -m analysis-2pc.maude -f latency.quatex -a 0.01 -d 0.01 2pc.maude init-2pc.maude 2pc-fault-config.maude event-2pc.maude
```

## Example Running Result

Following figure shows a screenshot of PerF running under the command 3 (full command).
It shows that the model composition and model transformation complete instantly.
Moreover, 600 simulations finish in approximately 2.27 seconds and yield an
expected average latency of 1.13 (time units), using 85.578 MB of memory. The SMC result of the example run is also in file [result.txt](result.txt)

![Screenshot of running](../images/screenshot-run.png)



## File Structure and Description

```
├── input-modules/      
├── output-fault-comp/  
├── output-moni-tran/   
├── tool/       
├── fault-injector.maude  
├── events.maude
├── run.sh
├── analysis-2pc.maude
├── latency.quatex
├── result.txt
├── ...  # other auxiliary files        
└── README.md
```

| Path / File               | Description |
|-------------------------- |-------------|
| `input-modules/`          | Original user-provided 2PC model and initialization modules, with fault and event configuration, which is `2pc.maude`,`init-2pc.maude`,`2pc-fault-config.maude`,`event-2pc.maude` |
| `output-fault-comp/`      | Generated files after model preprocessing and model composition (composition with fault injector by command 1). |
| `output-moni-tran/`       | Generated files after model transformation (added monitor by command 2). |
| `tool/`                   | Internal execution scripts used by PerF. |
| `run.sh`                  | Script to start PerF. |
| `analysis-2pc.maude`      | Maude module of defining analysis functions for SMC (e.g., average latency computation). |
| `fault-injector.maude`    | Fault-injection library. |
| `events.maude`            | Event-monitoring mechanism. |
| `latency.quatex`          | QuaTEx formula |
| `result.txt`              | SMC result of running command 3. |
| `README.md`               | Documentation for this 2PC |running example. |
