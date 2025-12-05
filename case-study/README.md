# Case Study

This directory contains the six case studies used to evaluate PerF.

Each case study demonstrates how PerF can instrument a distributed system model with faults, execute the transformed model, and optionally perform quantitative analysis via PVeStA.

Each directory contains its own README with the specific command needed to run that case.

## Directory Structure

```
├── 2pc-ctp/  # Two-Phase Commit protocol with the Cooperative 
├               Termination Protocol (CTP), with msgloss fault
├── raft/     # Raft leader election, with node crash fault
├── ramp/     # Read Atomic Multi-Partition (RAMP) system, 
├               with msgloss fault
├── dns/      # PowerDNS, with msg abnormal delay fault
├── quorum/   # Cassandra’s Quorum-based Consistency, 
├               with network partition fault
├── fhs/      # Byzantine fault-tolerant Fast-HotStuf protocol, 
├               with combination of equivocation and
├               network partition faults
└──pvesta/    # executable jar file of PVeStA for SMC
```


