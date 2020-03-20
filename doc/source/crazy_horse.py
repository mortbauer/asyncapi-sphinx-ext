"""
Crazy horse is a library for nothing
"""


def do_nothing(msg):
    """
    This function does nothing

    .. asyncapi_channels::
       :format: rst
      
       crazy_horse/<id>/state
         publish
           :summary: Current crazy horse status
          
           message
             :contentType: application/json

             payload
               properties
                 at
                   :type: number
                   :format: unix epoch in seconds

                 temperature
                   :type: number

    """
    pass


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

