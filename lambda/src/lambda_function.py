import boto3
import subprocess
import os

eks = boto3.client('eks')

def get_eks_credentials(cluster_name):
    """Obtém o token de autenticação do EKS e configura kubeconfig."""
    response = eks.describe_cluster(name=cluster_name)
    cluster_cert = response['cluster']['certificateAuthority']['data']
    endpoint = response['cluster']['endpoint']

    # Salvar o certificado em um arquivo temporário
    with open("/tmp/eks-ca.crt", "w") as cert_file:
        cert_file.write(base64.b64decode(cluster_cert).decode('utf-8'))
    
    # Atualizar kubeconfig
    os.environ['KUBECONFIG'] = '/tmp/kubeconfig'
    subprocess.run([
        'aws', 'eks', 'update-kubeconfig',
        '--name', cluster_name,
        '--kubeconfig', '/tmp/kubeconfig'
    ], check=True)

def restart_resource(resource_type, resource_name, namespace):
    """Reinicia o recurso Kubernetes (Deployment, Pod, etc.)."""
    if resource_type == 'deployment':
        command = [
            'kubectl', 'rollout', 'restart', f'deployment/{resource_name}',
            '-n', namespace
        ]
    elif resource_type == 'pod':
        command = [
            'kubectl', 'delete', f'pod/{resource_name}',
            '-n', namespace
        ]
    else:
        raise ValueError(f"Unsupported resource type: {resource_type}")
    
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Error restarting {resource_type}: {result.stderr}")
    else:
        print(f"Successfully restarted {resource_type}: {result.stdout}")

def lambda_handler(event, context):
    cluster_name = event.get('cluster_name')
    namespace = event.get('namespace', 'default')
    resource_name = event.get('resource_name')
    resource_type = event.get('resource_type', 'deployment')

    if not cluster_name or not resource_name:
        return {
            'statusCode': 400,
            'body': 'Missing required parameters: cluster_name or resource_name'
        }
    
    try:
        get_eks_credentials(cluster_name)
        restart_resource(resource_type, resource_name, namespace)
        return {
            'statusCode': 200,
            'body': f"{resource_type.capitalize()} {resource_name} restarted successfully in namespace {namespace}"
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }