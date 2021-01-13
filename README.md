# Celery stubs

This is a small library for client side function stubs for celery.

The name `stubs` does not refer to the testing aspect but rather to a proxy behavior coming from the stub / skeleton pattern known from remote method invocations. At celery, there is no need to create a skeleton, since this is handled by the middleware.

The stubs approach uses the `send_task` to schedule a remote task for execution. Since the stub does not know the arguments to apply, this is the part of the blueprint method.

## Example

```python

## Server

@app.task(name="calculate_sum")
def sum(a, b):
    return a + b

## Client

# Proxy Definition
class _CalculateSumTask(celery_client_stubs.AsyncRemoteTask):
    def __init__(self, celery, *args):
        super().__init__("calculate_sum", celery, *args)

def celery_sum(celery, a, b):
    return _CalculateSumTask(celery, a, b)

# Definition of methods
app = Celery(...)

...

def sum(a, b):
    return celery_sum(app, a, b)

# Usage

async_result = sum(1, 2).schedule_immediately()

# Wait for method to complete ...

```

## Task Factory

The class itself provides an `RemoteTaskFactory`, that can be used:

```python

# Definition

class MyRemoteTasks(celery_client_stubs.RemoteTaskFactory):
    def sum(self, a, b):
        task = celery.AsyncRemoteTask("calculate_sum", self._celery, a, b)

        return task

# Usage

app = Celery(...)

tasks = MyRemoteTasks(app)
async_result = tasks.sum(1, 2).schedule_immediately()

```

## Licensing

This library is published under BSD-3-Clause license, just like Celery is.

## Versioning

This library follows semantic versioning 2.0. Any breaking change will produce a new major release. Versions below 1.0 are considered to have a unstable interface.
