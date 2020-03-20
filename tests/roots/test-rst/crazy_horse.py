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
