"""
Crazy horse is a library for nothing
"""

def do_aynthing(msg):
    """
    This function does also nothing

    .. asyncapi_channels::
       :format: yaml

       crazy_horse/<id>/msg:
        publish:
          summary: Current crazy horse message of the day
          message:
            contentType: application/json
            payload:
              properties:
                at: 
                  type: number
                  format: unix epoch in seconds

       crazy_pig/<id>/msg:
        subscribe:
          summary: Current crazy horse message of the day
          message:
            contentType: application/json
            payload:
              properties:
                at: 
                  type: number
                  format: unix epoch in seconds
    """
    pass

