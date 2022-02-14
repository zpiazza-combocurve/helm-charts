# Bytewax Helm Chart

* Installs the Python Stream Processing Library [Bytewax](https://bytewax.io/)

## Get Repo Info

```console
helm repo add bytewax https://bytewax.github.io/helm-charts
helm repo update
```

_See [helm repo](https://helm.sh/docs/helm/helm_repo/) for command documentation._

## Installing the Chart

To install the chart with the release name `my-release`:

```console
helm install my-release bytewax/bytewax
```

This version requires Helm >= 3.1.0.

## Uninstalling the Chart

To uninstall/delete the my-release deployment:

```console
helm delete my-release
```

The command removes all the Kubernetes components associated with the chart and deletes the release.

## Configuration

| Parameter                                 | Description                                   | Default                                                 |
|-------------------------------------------|-----------------------------------------------|---------------------------------------------------------|
| `image.repository`                        | Image repository                              | `bytewax/bytewax`                                       |
| `image.tag`                               | Image tag                                     | `0.7.0`                                                 |
| `image.pullPolicy`                        | Image pull policy                             | `Always`                                                |
| `imagePullSecrets`                        | Image pull secrets                            | `[]`                                                    |
| `serviceAccount.create`                   | Create service account                        | `true`                                                  |
| `serviceAccount.annotations`              | Annotations to add to the service account     | `{}`                                                    |
| `serviceAccount.name`                     | Service account name to use, when empty will be set to created account if `serviceAccount.create` is set else to `default` | `` |
| `extralabels`                             | Labels to add to common labels                | `{}`                                                    |
| `podLabels`                               | Statefulset pod labels                        | `{}`                                                    |
| `podAnnotations`                          | Statefulset pod annotations                   | `{}`                                                    |
| `podSecurityContext`                      | Statefulset pod securityContext               | `{"runAsNonRoot": true, "runAsUser": 65532, "runAsGroup": 3000, "fsGroup": 2000}`  |
| `securityContext`                         | Statefulset containers securityContext        | `{"allowPrivilegeEscalation": false, "capabilities": {"drop": ["ALL"], "add": ["NET_BIND_SERVICE"]}, "readOnlyRootFilesystem": true }`|
| `service.port`                            | Kubernetes port where service is exposed      | `9999`                                                  |
| `resources`                               | CPU/Memory resource requests/limits           | `{}`                                                    |
| `nodeSelector`                            | Node labels for pod assignment                | `{}`                                                    |
| `tolerations`                             | Toleration labels for pod assignment          | `[]`                                                    |
| `affinity`                                | Affinity settings for pod assignment          | `{}`                                                    |
| `env`                                     | Extra environment variables passed to pods    | `{}`                                                    |
| `envValueFrom`                            | Environment variables from alternate sources. See the API docs on [EnvVarSource](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.17/#envvarsource-v1-core) for format details.  | `{}` |
| `envFromSecret`                           | Name of a Kubernetes secret (must be manually created in the same namespace) containing values to be added to the environment. Can be templated | `""` |
| `envRenderSecret`                         | Sensible environment variables passed to pods and stored as secret | `{}`                               |
| `extraSecretMounts`                       | Secret mounts to get secrets from files instead of env vars | `[]`                                      |
| `extraVolumeMounts`                       | Additional volume mounts                      | `[]`                                                    |
| `configuration.pythonFileName`            | Path of the python file to run                | `basic.py`                                              |
| `configuration.processesCount`            | Number of concurrent processes to run         | `1`                                                     |
| `configuration.workersPerProcess`         | Number of workers per process                 | `1`                                                     |
| `configuration.keepAlive`                 | Keep the container process alive after dataflow executing ended to prevent a container restart by Kubernetes | `true` |
| `configuration.configMap.create`          | Create a configmap to store python file(s)    | `true`                                                  |
| `configuration.configMap.customName`      | Configmap which has python file(s) created manually | ``                                                |
| `configuration.configMap.files.pattern`   | Files to store in the ConfigMap to be created | `examples/*`                                            |
| `configuration.configMap.files.tarName`   | Tar file to store in the ConfigMap to be created | ``                                                   |


### Example running basic.py obtained from a Configmap created by Helm

```yaml
configuration:
  pythonFileName: "basic.py"
  configMap:
    files:
      pattern: "examples/*"
      tarName:
```

### Example running pagerank.py obtained from a Configmap created by Helm

```yaml
configuration:
  pythonFileName: "examples/pagerank.py"
  configMap:
    files:
      pattern: 
      tarName: "examples.tar"
```

In this example, we store a tar file in the configmap. This is useful when you need a tree of nested files and directories. 

Following our example, the tar file has this content:
```console
├── examples
│   ├── anomaly_detector.py
│   ├── basic.py
│   ├── events_to_parquet.py
│   ├── pagerank.py
│   ├── sample_data
│   │   ├── easy_count.txt
│   │   ├── graph.txt
│   │   ├── lyrics.txt
│   │   └── wordcount.txt
│   ├── search_session.py
│   ├── sleepyworkers.py
│   ├── subflow.py
│   ├── translator.py
│   ├── twitter_stream.py
│   ├── utils
│   │   ├── fake_events.py
│   │   ├── __init__.py
│   │   └── twitter.py
│   ├── wikistream.py
│   └── wordcount.py
```
So, because that tar file is going to be extracted to the container working directory then the container is going to have that tree available to work with.
Our `pagerank.py` script opens a file located in `examples/sample_data` as we can see in this portion of its code:
```python
ec = bytewax.Executor()
flow = ec.Dataflow(read_edges("examples/sample_data/graph.txt"))
```

## How to include your own python code

So far the examples of the `configuration` block described how to use one of the python files already included in the chart.
We included those files to show you how to use this chart, but of course, you will want to run your own code. You have two ways to accomplish that:

### Install Bytewax chart using a local copy and put your file(s) inside it

In this case, you will need to fetch the Bytewax chart to your machine and copy your python file(s) inside the chart directory.
Then, you can use the chart settings to generate a Configmap storing your file(s) and run it in the container.

There are the steps to include `my-code.py` and execute it:

1. Fetch Bytewax chart and decompress it
```console
$ helm repo add bytewax https://bytewax.github.io/helm-charts
$ helm repo update
$ helm fetch bytewax/bytewax
$ tar -xvf bytewax-0.1.0.tgz
```
2. Copy your file to the chart directory
```console
$ cp ./my-code.py ./bytewax/
```
3. Install Bytewax chart using your local copy
```console
$ helm upgrade --install my-dataflow ./bytewax \
  --set configuration.pythonFileName="my-code.py" \
  --set configuration.configMap.files.pattern="my-code.py"
```

### Create a Configmap before install Bytewax chart

In this option, you will need to provide a Configmap with your file(s) and then configure your chart values to use it.

There are the steps to create a Configmap to store `my-code.py` and use it with the Bytewax chart:

1. Create the configmap
```console
$ kubectl create configmap my-configmap --from-file=my-code.py
```
2. Install Bytewax helm chart using `my-configmap`
```console
$ helm repo add bytewax https://bytewax.github.io/helm-charts
$ helm repo update
$ helm upgrade --install my-dataflow ./bytewax \
  --set configuration.pythonFileName="my-code.py" \
  --set configuration.configMap.create=false \
  --set configuration.configMap.customName=my-configmap
```

## How to securely reference secrets in your code

In my-workload.py:

```python
f = open('/etc/secrets/auth_generic_oauth/client_id','r');
client_id = f.read();
f = open('/etc/secrets/auth_generic_oauth/client_secret','r');
client_secret = f.read();
```

Existing secret, or created along with helm:

```yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: auth-generic-oauth-secret
type: Opaque
stringData:
  client_id: <value>
  client_secret: <value>
```

Include in the `extraSecretMounts` configuration flag:

```yaml
- extraSecretMounts:
  - name: auth-generic-oauth-secret-mount
    secretName: auth-generic-oauth-secret
    defaultMode: 0440
    mountPath: /etc/secrets/auth_generic_oauth
    readOnly: true
```

### extraSecretMounts using a Container Storage Interface (CSI) provider

This example uses a CSI driver e.g. retrieving secrets using [Azure Key Vault Provider](https://github.com/Azure/secrets-store-csi-driver-provider-azure)

```yaml
- extraSecretMounts:
  - name: secrets-store-inline
    mountPath: /run/secrets
    readOnly: true
    csi:
      driver: secrets-store.csi.k8s.io
      readOnly: true
      volumeAttributes:
        secretProviderClass: "my-provider"
      nodePublishSecretRef:
        name: akv-creds
```