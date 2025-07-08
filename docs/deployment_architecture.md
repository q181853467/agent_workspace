# 部署架构与容器化方案

## 1. 部署架构图 (Kubernetes)

本方案采用Kubernetes作为容器编排平台，以实现高可用、可扩展和自动化的部署。

```mermaid
graph TD
    subgraph "外部流量"
        DNS --> Ingress
    end

    subgraph "Kubernetes Cluster"
        Ingress(NGINX Ingress Controller)

        subgraph "API Gateway Namespace"
            APIGateway[Deployment: API Gateway]
        end

        subgraph "Core Services Namespace"
            AuthSvc[Deployment: Auth Service]
            UserSvc[Deployment: User Mgmt Service]
            RouterSvc[Deployment: Model Router Service]
        end

        subgraph "Model Serving Namespace"
            ModelAbsSvc[Deployment: Model Abstraction Service]
            DeepseekSvc[Deployment: Deepseek Adapter]
            GPTSvc[Deployment: GPT Adapter]
        end

        subgraph "Backend Services Namespace"
            PostgreSQL[StatefulSet: PostgreSQL]
            Redis[StatefulSet: Redis]
            RabbitMQ[StatefulSet: RabbitMQ]
        end

        subgraph "Monitoring Namespace"
            Prometheus[Deployment: Prometheus]
            Grafana[Deployment: Grafana]
            Loki[DaemonSet: Loki]
        end

        Ingress -- HTTPS --> APIGateway
        APIGateway -- gRPC --> AuthSvc
        APIGateway -- gRPC --> UserSvc
        APIGateway -- gRPC/HTTP --> RouterSvc
        
        RouterSvc -- gRPC/HTTP --> ModelAbsSvc
        ModelAbsSvc -- HTTP --> DeepseekSvc
        ModelAbsSvc -- HTTP --> GPTSvc

        AuthSvc -- TCP --> PostgreSQL
        UserSvc -- TCP --> PostgreSQL
        RouterSvc -- TCP --> Redis
        RouterSvc -- TCP --> RabbitMQ

        Prometheus --> APIGateway(scrape metrics)
        Prometheus --> CoreServices(scrape metrics)
        Prometheus --> ModelServing(scrape metrics)

        Grafana -- query --> Prometheus
        Grafana -- query --> Loki
    end

    style Ingress fill:#bbf,stroke:#333,stroke-width:2px
    style PostgreSQL fill:#f9f,stroke:#333,stroke-width:2px
    style Redis fill:#f9f,stroke:#333,stroke-width:2px
    style RabbitMQ fill:#f9f,stroke:#333,stroke-width:2px
```

## 2. 核心组件部署策略

- **Ingress Controller**: 使用`NGINX Ingress Controller`，负责处理外部流量，提供L7负载均衡和SSL终止。
- **API Gateway**: 作为无状态服务部署为`Deployment`，可根据流量轻松水平扩展Pod数量。
- **核心微服务**: 所有核心微服务（认证、用户、路由等）均部署为`Deployment`，通过`Horizontal Pod Autoscaler (HPA)`根据CPU和内存使用率自动伸缩。
- **数据库/缓存/消息队列**: 
  - 部署为`StatefulSet`，以保证稳定的网络标识符和持久化存储。
  - 使用`PersistentVolume (PV)`和`PersistentVolumeClaim (PVC)`来挂载持久化存储，确保数据在Pod重启后不丢失。
  - 建议在生产环境中使用云服务商提供的托管数据库服务（如AWS RDS, Google Cloud SQL），以简化运维。
- **模型服务**: 
  - 如果模型是自托管的，并且需要GPU资源，则应将模型服务部署在带有GPU的特定节点上，并使用Kubernetes的`nodeSelector`或`taints/tolerations`进行调度。
  - 如果是调用外部API（如OpenAI），则模型适配器服务是IO密集型的，部署为普通的`Deployment`即可。

## 3. 容器化方案

每个微服务都将被打包成一个独立的Docker镜像。

#### 3.1 `Dockerfile` 示例 (FastAPI后端服务)

```dockerfile
# 1. 使用官方Python镜像作为基础
FROM python:3.11-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 4. 安装系统依赖 (如果需要)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc

# 5. 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. 拷贝项目代码
COPY . .

# 7. 暴露端口
EXPOSE 8000

# 8. 运行应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3.2 `docker-compose.yml` 示例 (用于本地开发)

此文件用于在本地快速启动整个开发环境，模拟多服务架构。

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: llm_db
    environment:
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=secret
      - POSTGRES_DB=llm_platform
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    container_name: llm_cache
    ports:
      - "6379:6379"

  api_service:
    build: .
    container_name: llm_api
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://admin:secret@postgres/llm_platform
      - REDIS_URL=redis://redis:6379

volumes:
  postgres_data:
```

#### 3.3 Kubernetes `deployment.yaml` 示例 (API服务)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
  labels:
    app: api-service
spec:
  replicas: 3 # 初始副本数为3
  selector:
    matchLabels:
      app: api-service
  template:
    metadata:
      labels:
        app: api-service
    spec:
      containers:
      - name: api-service
        image: your-registry/llm-platform-api:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: redis-config
              key: url
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: api-service
spec:
  selector:
    app: api-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP # 仅在集群内部访问
```
