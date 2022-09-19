# Celery + Redis + Django

============
1. Download Redis
    - Using apt package manager:
        ```
        sudo apt install lsb-release
        curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
        echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
        
        sudo apt-get update
        sudo apt-get install redis
        ```

    - Using [Snap](https://snapcraft.io/store)


2. Open & Test Redis:
    - open Terminal
    - start  redis service   : `sudo systemctl start redis`
    - **redis-cli ping**
        ```
        $ redis-cli ping
        PONG
        ```

    - **redis-server**
        ```
        $ redis-server
        206002:C 19 Sep 2022 22:14:46.927 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
        206002:C 19 Sep 2022 22:14:46.927 # Redis version=6.2.7, bits=64, commit=00000000, modified=0, pid=206002, just started
        206002:C 19 Sep 2022 22:14:46.927 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
        206002:M 19 Sep 2022 22:14:46.928 * monotonic clock: POSIX clock_gettime
        206002:M 19 Sep 2022 22:14:46.928 # A key '__redis__compare_helper' was added to Lua globals which is not on the globals allow list nor listed on the deny list.
                        _._                                                  
                _.-``__ ''-._                                             
            _.-``    `.  `_.  ''-._           Redis 6.2.7 (00000000/0) 64 bit
        .-`` .-```.  ```\/    _.,_ ''-._                                  
        (    '      ,       .-`  | `,    )     Running in standalone mode
        |`-._`-...-` __...-.``-._|'` _.-'|     Port: 6379
        |    `-._   `._    /     _.-'    |     PID: 206002
        `-._    `-._  `-./  _.-'    _.-'                                   
        |`-._`-._    `-.__.-'    _.-'_.-'|                                  
        |    `-._`-._        _.-'_.-'    |           https://redis.io       
        `-._    `-._`-.__.-'_.-'    _.-'                                   
        |`-._`-._    `-.__.-'    _.-'_.-'|                                  
        |    `-._`-._        _.-'_.-'    |                                  
        `-._    `-._`-.__.-'_.-'    _.-'                                   
            `-._    `-.__.-'    _.-'                                       
                `-._        _.-'                                           
                    `-.__.-'                                               

        206002:M 19 Sep 2022 22:14:46.929 # Server initialized
        206002:M 19 Sep 2022 22:14:46.929 # WARNING overcommit_memory is set to 0! Background save may fail under low memory condition. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
        206002:M 19 Sep 2022 22:14:46.929 * Ready to accept connections

        ```
        **Close Redis** with `control` + `c` to quit

3. Install Celery + Redis in your virtualenv.
    ```
    pip install celery
    pip install redis
    pip install django-celery-beat
    pip install django-celery-results
    pip freeze > requirements.txt
    ```

4. Update Django `settings.py`:
    ```
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django_celery_beat',
        'django_celery_results',
    ]


    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'
    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = TIME_ZONE
    ```

5. Create `celery.py` to setup `Celery app`:
    Navigate to project config module (where `settings` and `urls` modules are) and create a `celery.py` file with the contents:
    ```py
    from __future__ import absolute_import, unicode_literals
    import os
    from celery import Celery
    
    
    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_celery.settings")
    
    app = Celery("proj")
    
    # Using a string here means the worker don't have to serialize
    # the configuration object to child processes.
    # - namespace='CELERY' means all celery-related configuration keys
    #   should have a `CELERY_` prefix.
    app.config_from_object("django.conf:settings", namespace="CELERY")
    
    # Load task modules from all registered Django app configs.
    app.autodiscover_tasks()
    
    
    @app.task(bind=True)
    def debug_task(self):
    print("Request: {0!r}".format(self.request))

    ```
6. Update project conf folder's `__init__.py` file:
    ```py
    # This will make sure the app is always imported when
    # Django starts so that shared_task will use this app.
    from .celery import app as celery_app
    
    __all__ = ("celery_app",)

    ```
   
7. Create `tasks.py` in your Django app (a valid app in `INSTALLED_APPS`):
    ```py
    import random
    from celery import shared_task
    import time
    from .models import SalesForecast
    
    
    @shared_task
    def add(x, y):
        return x + y
    
    
    @shared_task
    def mul(x, y):
        total = x * (y * random.randint(3, 100))
        return total
    
    
    @shared_task
    def get_sf_data(sku):
        time.sleep(5)
    
        obj = SalesForecast.objects.create(
            product_name=sku,
            sales_value=random.randint(0, 200),
            price_value=random.uniform(0, 1000),
        )
    
        return sku

    ```
8. Run migrations: 
    `python manage.py makemigrations` 
    and 
    `python manage.py migrate`


9. Test tasks:
    1. Open a terminal window, `Run Celery` with in your `project root` where `manage.py` lives:

        ```
        celery -A yourproject worker -l info
        # like 
        celery -A django_celery worker -l info
        ```

    2. Open another terminal window, in your Django project `python manage.py shell`:

        ```
        >>> from yourapp.tasks import add, mul, xsum
        >>> add(1,3)
        4
        >>> add.delay(1,3)
        <AsyncResult: 7bb03f9a-5702-4661-b737-2bc54ed9f558>
        ```
    