# Parallel Genetic Algorithm for Traffic Signal Control

## Table of Contents

1. [Description and Motivation](#1-description-and-motivation)
2. [Setup and Usage Instructions](#2-setup-and-usage-instructions)

---

## 1. Description and Motivation

### Overview

This project applies a **Parallel Genetic Algorithm (PGA)** to optimize real-world **Traffic Signal Control Systems**. By evolving signal timing plans across parallel computation threads, the algorithm reduces vehicle waiting times and improves overall traffic throughput.

### Motivation

Urban traffic congestion — particularly in rapidly growing smart cities across India — poses a significant challenge to daily commuters and emergency response systems alike. Existing traffic signal infrastructure is largely static and fails to adapt dynamically to incidents such as accidents, which compound congestion and increase risk for road users.

This project addresses that gap by building an intelligent, adaptive traffic control system capable of detecting disruptions and rerouting signal timings in real time, with the goal of minimizing delays for all road users.

---

## 2. Setup and Usage Instructions

### 2.1 Clone the Repository

Create a directory for the project, open a terminal inside it, and run one of the following commands depending on your preferred Git authentication method:

```bash
# Method 1: HTTPS
git clone https://github.com/VarunRajV28/Parallel-GA-Traffic.git

# Method 2: SSH
git clone git@github.com:VarunRajV28/Parallel-GA-Traffic.git
```

### 2.2 Create a Python Virtual Environment

It is recommended to isolate project dependencies using a virtual environment.

```bash
# Create a virtual environment
python -m venv .venv
```

**Activate the environment:**

```bash
# Windows (PowerShell) — allow script execution if not already enabled
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
python .\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

### 2.3 Install Dependencies

```bash
# Navigate to the project directory
cd Parallel-GA-Traffic

# Install required packages
pip install -r requirements.txt
```