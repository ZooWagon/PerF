# PerF

This repository provides a command-line tool that automates the complete workflow of our formal fault-injection framework for distributed system models specified in Maude.

The tool performs:
1. Model preprocessing
2. Model composition with fault injector
3. (Optional) Model transformation with event monitor
4. (Optional) Quantitative analysis via PVeStA

## 1. Environment Requirements

To run the tool successfully, the following environment is required:

- Operating System: Linux (We conduct experiments on CentOS Linux 7)

- Python Versions Supported: Python 2.7, or Python 3.7 (We conduct experiments the two Python version)

- Maude Version: Maude 2.7.1 (required for PVeStA)

- Java Runtime: Java 1.8 (required for PVeStA)

Ensure that the following commands are available globally (in system `$PATH`):
```
python --version  # should be Python 2.7 or Python 3.7 or higher
maude             # should be Maude 2.7.1
java -version     # should report Java 1.8
```

## 2. Command Pattern
All tool commands follow a unified command-line structure.
The generic command pattern is:
```
sh run.sh [--pvesta serverlist ana-model quatex confidence] protocol init fault [event]
```
**Explanation of arguments**
| Argument     | Required? | Description                                                                 |
| ------------ | --------- | --------------------------------------------------------------------------- |
| `protocol`   | ✔         | User-provided system model (e.g. `2pc.maude`)                              |
| `init`       | ✔         | Module defining the initial system configuration (e.g., `init-2pc.maude`)   |
| `fault`      | ✔         | Module defining injected fault behaviors (e.g., `2pc-fault-config.maude`)          |
| `event`      | optional  | Event declaration module for model transformation (e.g., `event-2pc.maude`) |
| `--pvesta`   | optional  | Enables quantitative analysis using PVeStA. Once enabled, following arguments are all required                   |
| `serverlist` | optional  | PVeStA server configuration file                                            |
| `analysis-model`  | optional  | Maude module containing analysis functions (e.g., latency computation)      |
| `quatex`     | optional  | QuaTEx formula                                             |
| `confidence` | optional  | Confidence level, usually 0.05           |
| `threshold` | optional  | Error margin, usually 0.01                      |

This command pattern is valid for all case studies.
Each case directory contains its own README with the specific commands required. Thus, only the general pattern is presented here.

## 3. Repository Structure
```
.
├── 2pc-running-example/   # Running example: simplified 2PC protocol in paper's Appendix A
├── case-study             #  Case studies
└── README.md
```
