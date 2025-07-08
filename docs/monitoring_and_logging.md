# 监控与日志策略

## 1. 监控策略 (Prometheus + Grafana)

### 1.1 监控目标

- **系统健康度**: 确保所有服务和基础设施都处于正常运行状态。
- **性能瓶颈定位**: 快速发现并定位系统中的性能瓶颈（如高延迟、高资源消耗的服务）。
- **容量规划**: 基于历史趋势数据，预测未来的资源需求。
- **业务指标监控**: 跟踪关键业务指标（如API调用总数、活跃用户数、模型使用分布）。

### 1.2 关键监控指标 (Metrics)

#### a) API网关 (Gateway)
- **请求速率 (QPS/RPS)**: `sum(rate(nginx_http_requests_total[1m]))`
- **请求延迟**: `histogram_quantile(0.99, sum(rate(nginx_http_request_duration_seconds_bucket[5m])) by (le))` (P99延迟)
- **错误率**: `sum(rate(nginx_http_requests_total{status=~"5.."}[1m])) / sum(rate(nginx_http_requests_total[1m]))` (5xx错误率)
- **流量**: `sum(rate(nginx_http_request_size_bytes[1m]))` (入口流量), `sum(rate(nginx_http_response_size_bytes[1m]))` (出口流量)

#### b) 核心微服务 (e.g., Model Router)
- **gRPC/HTTP请求速率**: `sum(rate(grpc_server_handled_total[1m])) by (grpc_service, grpc_method)`
- **gRPC/HTTP请求延迟**: `histogram_quantile(0.95, sum(rate(grpc_server_handling_seconds_bucket[5m])) by (le, grpc_method))` (P95延迟)
- **CPU/内存使用率**: `container_cpu_usage_seconds_total`, `container_memory_working_set_bytes`
- **Pod重启次数**: `kube_pod_container_status_restarts_total`

#### c) 模型服务 (Model Serving)
- **模型调用成功率**: `sum(rate(model_inference_success_total[1m])) by (model_name)`
- **模型调用失败率**: `sum(rate(model_inference_failure_total[1m])) by (model_name, reason)`
- **端到端推理延迟**: `histogram_quantile(0.90, sum(rate(model_inference_latency_seconds_bucket[5m])) by (le, model_name))` (P90延迟)
- **Token生成速率**: `sum(rate(model_output_tokens_total[1m])) by (model_name)` (Tokens/sec)
- **GPU使用率/显存**: `dcgm_gpu_utilization`, `dcgm_memory_used_bytes` (如果使用NVIDIA GPU和DCGM exporter)

#### d) 数据库/缓存
- **连接数**: `pg_stat_activity_count`, `redis_connected_clients`
- **慢查询**: `pg_stat_statements_total_time`
- **缓存命中率**: `redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total)`

### 1.3 告警规则 (Alertmanager)

- **高延迟**: API网关或核心服务的P99延迟超过1秒。
- **高错误率**: 某个服务的错误率在5分钟内持续高于5%。
- **资源耗尽**: Pod的CPU或内存使用率持续超过其limit的90%。
- **服务不可用**: `up{job="my-service"} == 0` (服务实例掉线)
- **数据库主从延迟**: 主从复制延迟超过60秒。
- **API密钥即将过期**: `api_key_expiry_days < 7` (自定义指标)

## 2. 日志策略 (Loki + Promtail)

### 2.1 日志收集

- **架构**: 使用`Promtail`作为日志收集代理，它会以`DaemonSet`的形式部署在每个Kubernetes节点上。
- **自动发现**: Promtail会自动发现节点上的Pod，并根据Pod的标签（labels）来抓取其标准输出（stdout）和标准错误（stderr）的日志。
- **标签化**: 这是Loki的核心优势。Promtail会为日志流附加Pod的标签，如`{app="api-service", namespace="core-services"}`。这使得日志查询可以与Prometheus的指标查询方式保持一致。

### 2.2 日志格式

- **结构化日志**: 所有微服务都应输出**JSON格式**的结构化日志。这极大地提升了日志的可读性和可查询性。
- **日志内容**: 每条日志应至少包含以下字段：
  - `timestamp`: 日志时间
  - `level`: 日志级别 (e.g., INFO, WARN, ERROR)
  - `service`: 服务名称
  - `message`: 日志信息
  - `trace_id`: **分布式追踪ID**。这是关联一次完整请求流经所有微服务日志的关键。
  - `user_id`: 用户ID
  - `request_id`: 请求ID

**示例日志 (JSON):**
```json
{ 
  "timestamp": "2025-07-07T14:30:00Z",
  "level": "INFO", 
  "service": "model-router", 
  "message": "Routing request to model gpt-4o",
  "trace_id": "abc-123-xyz-789",
  "request_id": "req-550e8400",
  "user_id": 123,
  "model_name": "gpt-4o",
  "latency_ms": 15
}
```

### 2.3 日志查询 (LogQL)

在Grafana中使用LogQL进行查询。

- **查询某个服务的所有错误日志**: 
  `{app="model-router", level="ERROR"}`
- **查询特定追踪ID的所有日志**: 
  `{trace_id="abc-123-xyz-789"}`
- **从日志中提取指标并计算速率**: 
  `sum(rate({app="api-service"} | json | unwrap latency_ms [1m])) by (path)`

## 3. 分布式追踪 (OpenTelemetry)

为了完整地观察一个请求在复杂微服务架构中的完整生命周期，需要引入分布式追踪。

- **标准**: 使用`OpenTelemetry`作为标准。
- **实现**: 
  1. 在**API网关**接收到请求时，生成一个唯一的`trace_id`，并将其注入到请求头中。
  2. 每个微服务都集成OpenTelemetry SDK，从上游请求中提取`trace_id`，并在调用下游服务时继续传递。
  3. 每个服务记录自己的处理单元（Span），包括起止时间、关键操作和标签。
  4. 将这些Span数据发送到一个追踪后端，如`Jaeger`或`Zipkin`进行存储和可视化。