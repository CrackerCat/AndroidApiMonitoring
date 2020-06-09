# AndroidApiMonitoring

### Installation

- install virtualenv

```shell
pip install virtualenv
```

- install requirements

```shell
pip install -r requirements
```

- adb in path file
- emulator/device already running and connect

### Usage

Let's start by looking at the help message:
```shell
python frida_monitoring --help  
Start dynamic API monitoring

optional arguments:
  -h, --help            show this help message and exit
  -f APK, --file-apk APK
                        file apk to analyze
  -v VERSION, --version VERSION
                        Version API Monitoring,
                         -v 1 => Original,
                         -v 2 => Based on https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security
  -p PACKAGENAME, --package-name PACKAGENAME
                        Package Name of app to analyze
  --list-api API [API ...]
                        List of api file to monitoring, 
                        e.g., file_api.txt
  --api API             Single API to Monitoring, 
                        e.g., android.webkit.WebView,loadUrl
  --filter              { Device Data,Device Info,SMS,System Manager,
                          Base64 encode/decode,Dex  Class Loader,
                          Network,Crypto,Crypto - Hash,Binder,IPC,Database,
                          SharedPreferences,WebView,Java Native Interface,
                          Command,Process,FileSytem - Java,ALL, NONE } 
  --store-script        TRUE/FALSE
                        Saving of Frida code used to the app instrumentation
```

Usage example:

```shell
python frida_monitoring.py -v 1 --file-apk app.apk --list-api api_personalized_1.txt api_personalized_2.txt
```

```shell
python frida_monitoring.py -v 1 --package-name com.example.analyticsapptesting --list-api api_personalized_1.txt
```   

```shell
python frida_monitoring.py -v 2 --package-name com.example.analyticsapptesting
```   

```shell
python frida_monitoring.py -v 2 --file-apk app.apk --list-api api_personalized_1.txt api_personalized_2.txt
```    

```shell
python frida_monitoring.py -v 2 -p com.example.analyticsapptesting --list-api api_personalized_1.txt api_personalized_2.txt
```    

```shell    
python frida_monitoring.py -v 2 --package-name com.example.analyticsapptesting
```    

```shell  
python frida_monitoring.py -v 2 -p com.example.app --list-api api_personalized.txt api_personalized_2.txt --store-script True --filter "Crypto" "Crypto - Hash"
```

