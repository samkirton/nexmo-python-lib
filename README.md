nexmo-python-lib
================

A helper class that sends and parses the response of text messages sent through the Nexmo API

Example usage:
```python
import Nexmo import NexmoREST
from Nexmo import NexmoSMS

nexmoRest = NexmoREST("xxxxxx","xxxxxxx")
nexmoSMS = NexmoSMS(nexmoRest)
nexmoResponse = nexmoSMS.sendPlainTextSMS("447738492309","61497790304","Hello, this is a text message!")
```
