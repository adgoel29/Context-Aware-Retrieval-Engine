# Retrieval Benchmark: Strategy A vs Strategy B

**Strategy A** — raw query embedding search  

**Strategy B** — LLM query expansion → embedding search


---

## Query: *How does the system handle peak load?*

**Expanded (B):** How does the infrastructure, application, or platform manage and cope with high traffic, burst load, or sudden spikes in demand? What mechanisms and strategies are employed to sustain performance, availability, and resilience under maximum capacity, overload conditions, or stress events? Describe the system's scalability (horizontal and vertical), load balancing, auto-scaling, rate limiting, caching, queuing, and other architectural patterns for handling peak concurrency. How is capacity planning conducted to ensure fault tolerance and efficient resource allocation during periods of high utilization?


|   Rank | A — Topic        |   A Score | B — Topic      |   B Score |
|-------:|:-----------------|----------:|:---------------|----------:|
|      1 | load_balancing   |    0.4327 | autoscaling    |    0.4702 |
|      2 | autoscaling      |    0.3878 | rate_limiting  |    0.4556 |
|      3 | circuit_breakers |    0.3402 | load_balancing |    0.4294 |


## Query: *What happens when a service becomes unavailable?*

**Expanded (B):** What are the consequences, symptoms, detection methods, incident response procedures, impact, troubleshooting steps, and recovery processes when a service, application, microservice, or infrastructure component experiences an outage, downtime, failure, crash, unresponsiveness, error state, or becomes unavailable, offline, degraded, inaccessible, or out of service, including alerts, monitoring, fault detection, and potential effects on user experience, data integrity, and system performance?


|   Rank | A — Topic         |   A Score | B — Topic                |   B Score |
|-------:|:------------------|----------:|:-------------------------|----------:|
|      1 | circuit_breakers  |    0.3832 | disaster_recovery        |    0.4512 |
|      2 | message_queues    |    0.3238 | circuit_breakers         |    0.4333 |
|      3 | disaster_recovery |    0.313  | monitoring_observability |    0.405  |


## Query: *How is data consistency maintained across nodes?*

**Expanded (B):** How is data consistency, data integrity, or transactional integrity maintained, preserved, or ensured across multiple nodes, distributed systems, replicated databases, or clusters? What are the mechanisms, protocols, and algorithms used to achieve data synchronization, state replication, and data coherence in multi-node environments? Explore methods for guaranteeing consistency models such as strong consistency, eventual consistency, causal consistency, or linearizability, considering ACID and BASE principles. This includes consensus algorithms like Paxos or Raft, distributed transaction management, two-phase commit (2PC), three-phase commit (3PC), quorum-based replication, conflict resolution strategies, and techniques for preserving data integrity and reliability in distributed architectures and high-availability setups.


|   Rank | A — Topic            |   A Score | B — Topic                |   B Score |
|-------:|:---------------------|----------:|:-------------------------|----------:|
|      1 | database_replication |    0.4859 | database_replication     |    0.5762 |
|      2 | caching              |    0.3889 | message_queues           |    0.4223 |
|      3 | message_queues       |    0.3625 | monitoring_observability |    0.4045 |


## Query: *What mechanisms prevent the system from being overwhelmed by requests?*

**Expanded (B):** What mechanisms, techniques, strategies, or safeguards are employed to prevent, mitigate, or control an application, service, platform, or distributed system from becoming overwhelmed, overloaded, saturated, flooded, or degraded by an excessive volume of requests, traffic, queries, or API calls? This expanded query seeks information on congestion control, rate limiting, throttling, backpressure, load shedding, circuit breakers, flow control, queuing systems, message queues, resource management, concurrency limits, auto-scaling, and other resilience patterns designed to manage load, ensure system stability, high availability, and graceful degradation under peak or unexpected demand, thereby avoiding performance issues or service unavailability.


|   Rank | A — Topic        |   A Score | B — Topic      |   B Score |
|-------:|:-----------------|----------:|:---------------|----------:|
|      1 | rate_limiting    |    0.5322 | rate_limiting  |    0.6083 |
|      2 | load_balancing   |    0.4471 | load_balancing |    0.5194 |
|      3 | circuit_breakers |    0.3326 | message_queues |    0.4429 |


## Query: *How does the system recover from failures?*

**Expanded (B):** How does the system, application, service, or infrastructure implement mechanisms for recovery from failures, outages, crashes, and disruptions? Explore the fault tolerance, high availability, resilience engineering, and disaster recovery strategies, processes, and procedures, including self-healing capabilities, failover solutions, rollback methods, and incident response plans, designed to restore functionality, maintain uptime, ensure business continuity, and mitigate service degradation following errors, malfunctions, data loss, or system breakdowns.


|   Rank | A — Topic         |   A Score | B — Topic                |   B Score |
|-------:|:------------------|----------:|:-------------------------|----------:|
|      1 | disaster_recovery |    0.5013 | disaster_recovery        |    0.6865 |
|      2 | circuit_breakers  |    0.4581 | circuit_breakers         |    0.4387 |
|      3 | message_queues    |    0.3772 | monitoring_observability |    0.4322 |



Summary

| Query                                            |   Overlap |   Unique to A |   Unique to B |
|:-------------------------------------------------|----------:|--------------:|--------------:|
| How does the system handle peak load?...         |         2 |             1 |             1 |
| What happens when a service becomes unavailab... |         2 |             1 |             1 |
| How is data consistency maintained across nod... |         2 |             1 |             1 |
| What mechanisms prevent the system from being... |         2 |             1 |             1 |
| How does the system recover from failures?...    |         2 |             1 |             1 |

