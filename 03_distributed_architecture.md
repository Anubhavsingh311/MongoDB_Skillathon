# 03 — Distributed Database Architecture

## Why Distribution Matters

Modern databases must support critical applications globally with zero tolerance for downtime or data loss. A banking app that drops a transaction or goes offline for any period of time causes real, direct harm.

MongoDB uses a **distributed architecture** to ensure performance, availability, and scalability regardless of load or failure.

---

## Scaling

**Scaling** = adjusting hardware to meet demand.

- **Scale up** → add hardware capacity
- **Scale down** → reduce hardware

### Why It's Critical
- Too few resources → missed transactions, poor UX, potential crash
- Too many resources → wasted cost, no performance gain

### Vertical Scaling
Increase the power of a single machine (faster CPU, more RAM, larger disk).

| Pros | Cons |
|---|---|
| Simple architecture | Hardware has a ceiling |
| Good for single-node setups | High-end components cost disproportionately more |
| | Can't scale down easily on-premises |
| | Must over-provision for peak load |

> Example: If peak load is 10,000 users but normal load is 5,000, you pay for 10,000-user capacity 100% of the time.

### Horizontal Scaling (Sharding)
Distribute the database across multiple machines. Each machine holds a subset of the data.

| Pros | Cons |
|---|---|
| Use cheaper, commodity hardware | Added architectural complexity |
| Distribute workload across nodes | Requires careful shard key design |
| Scales elastically in the cloud | |

> **Sharding** = the process of splitting data across multiple nodes horizontally.

---

## Cloud and Elastic Provisioning

**Cloud provisioning** = reserving virtual CPU, storage, memory, and networking resources on demand.

Because cloud resources are virtual, scaling up or down is fast and cheap. This makes horizontal scaling especially powerful — you pay for what you use, and you can respond to spikes without over-provisioning.

> The cloud also makes vertical scaling easier since you have access to high-spec hardware without upfront purchase costs.

---

## Replication

**Replication** = storing multiple copies of data across multiple nodes and keeping them synchronized.

Purpose: **redundancy and availability** — if one node fails, others continue serving data.

### Replica Sets in MongoDB
- A **replica set** is a group of nodes all containing the same data
- Minimum: **3 nodes** (must be an odd number)
- **1 Primary node** — handles all writes
- **N Secondary nodes** — replicate from the primary; can serve reads

### Why Odd Numbers?
An odd number ensures a clear majority vote during elections (when the primary goes down, secondaries elect a new primary).

---

## Data Consistency: Read and Write Concerns

Writing to a distributed system creates a consistency challenge — data lands on one node first, then propagates.

**Read Concerns** and **Write Concerns** are configurable rules that govern how MongoDB responds to CRUD operations in terms of when a write is acknowledged and how fresh a read is.

The administrator chooses the tradeoff based on the application's requirements.

---

## The CAP Theorem

The CAP Theorem states that a distributed system can only guarantee **two of the three** following properties simultaneously:

| Property | Description |
|---|---|
| **C**onsistency | Every read receives the most recent write (or an error) |
| **A**vailability | Every request receives a response (not guaranteed to be the most recent) |
| **P**artition Tolerance | The system continues operating even if network partitions separate nodes |

### How MongoDB Handles It
MongoDB is **CP by default** (Consistency + Partition Tolerance), but Read/Write Concerns let administrators tune the balance toward availability when the use case demands it.

> There is always a tradeoff. The administrator's job is to choose the right balance for the expected workload.

---

## Key Takeaways

- **Vertical scaling** = bigger machine; **horizontal scaling** = more machines (sharding)
- Cloud provisioning makes elastic horizontal scaling practical and cost-effective
- **Replication** ensures availability and protects against data loss from node failure
- Replica sets use a primary/secondary model with an odd number of nodes
- The **CAP Theorem** defines the fundamental tradeoff: Consistency, Availability, Partition Tolerance — pick two
- MongoDB exposes this tradeoff through configurable **Read and Write Concerns**
