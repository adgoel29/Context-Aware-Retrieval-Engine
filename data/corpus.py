CORPUS = [
    # 0 - Load Balancing
    "A load balancer distributes incoming requests across multiple backend servers using strategies like "
    "round-robin, least-connections, or IP hash. This ensures no single server bears the full traffic burden. "
    "Health checks are run continuously to route requests only to healthy instances. "
    "Modern reverse proxies like NGINX or HAProxy can perform this request distribution at layer 4 or layer 7.",

    # 1 - Autoscaling
    "Horizontal scaling adds more compute instances when CPU or memory utilization crosses a defined threshold. "
    "An autoscaler monitors metrics and provisions new replicas automatically during traffic spikes. "
    "When demand drops, it terminates excess instances to reduce cost. "
    "Managed instance groups or Kubernetes HPA handle this compute provisioning without manual intervention.",

    # 2 - Caching
    "An in-memory cache like Redis or Memcached stores frequently accessed data close to the application layer. "
    "Cache hits avoid expensive database round-trips, reducing both latency and backend load. "
    "TTL-based expiry and cache invalidation strategies keep data fresh. "
    "CDNs extend caching to the network edge, serving static assets from geographically close nodes.",

    # 3 - Database Replication
    "Primary-replica replication keeps one writable leader node in sync with one or more read-only followers. "
    "Write-ahead logs are streamed to replicas to maintain consistency across nodes. "
    "In the event of leader failure, a replica can be promoted to maintain data availability. "
    "Eventual consistency models allow replicas to lag slightly, trading strict consistency for higher throughput.",

    # 4 - API Gateway
    "An API gateway acts as the single entry point for all client requests to backend microservices. "
    "It handles cross-cutting concerns like authentication, SSL termination, and request routing. "
    "Transformations such as protocol translation and response aggregation can be applied at this layer. "
    "Kong, AWS API Gateway, and Apigee are common implementations in production stacks.",

    # 5 - Rate Limiting
    "Rate limiting controls how many requests a client can make within a sliding time window. "
    "Token bucket and leaky bucket algorithms are widely used to enforce these request quotas. "
    "When a client exceeds its quota, the server returns a 429 Too Many Requests response. "
    "This protects backend services from being overwhelmed by bursty or abusive traffic patterns.",

    # 6 - Circuit Breakers
    "A circuit breaker monitors outgoing calls to a dependent service and tracks failure rates. "
    "When failures exceed a threshold, the circuit opens and subsequent calls are short-circuited immediately. "
    "This prevents a slow or failing downstream service from cascading failures to the entire system. "
    "After a cooldown period, the circuit enters a half-open state to test if the dependency has recovered.",

    # 7 - Message Queues
    "Message queues like Kafka or RabbitMQ decouple producers from consumers using an async publish-subscribe model. "
    "Producers write events to topics without waiting for consumers to process them. "
    "Consumers pull messages at their own pace, enabling backpressure handling and retry logic. "
    "Durable queues persist messages to disk so they survive broker restarts without data loss.",

    # 8 - Monitoring and Observability
    "Observability is achieved through three pillars: metrics, logs, and distributed traces. "
    "Prometheus scrapes time-series metrics from instrumented services and stores them for querying. "
    "Structured logs aggregated in systems like Elasticsearch or Loki allow root-cause analysis. "
    "Distributed tracing tools like Jaeger link spans across service boundaries to identify latency bottlenecks.",

    # 9 - Disaster Recovery
    "A disaster recovery plan defines RTO (recovery time objective) and RPO (recovery point objective) targets. "
    "Automated failover routes traffic to a standby region when the primary region becomes unreachable. "
    "Periodic snapshot backups and cross-region replication minimize data loss during outages. "
    "Runbooks and chaos engineering drills ensure the team can execute recovery procedures under pressure.",
]

CORPUS_METADATA = [
    {"id": i, "topic": topic, "chunk_text": CORPUS[i]}
    for i, topic in enumerate([
        "load_balancing",
        "autoscaling",
        "caching",
        "database_replication",
        "api_gateway",
        "rate_limiting",
        "circuit_breakers",
        "message_queues",
        "monitoring_observability",
        "disaster_recovery",
    ])
]

# print(CORPUS_METADATA)