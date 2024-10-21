from kubernetes import client, config

config.load_incluster_config()

v1 = client.CoreV1Api()

service = v1.read_namespaced_service(name="backend-service", namespace="default")
print(service.status.load_balancer.ingress[0].hostname)
