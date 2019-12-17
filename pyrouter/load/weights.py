# weights for different types of roads (considering
# thickness, road quality, manuever, maneuverability, etc)

class RoutingWeights:
  def __init__(self):
    self.Weightings = {
      'motorway': 10,
      'trunk': 10,
      'primary':  2,
      'secondary': 1.5,
      'tertiary': 1,
      'unclassified': 1,
      'minor': 1,
      'residential': 0.7,
      'track': 1,
      'service': 1,
      }

  def get(self, wayType):
    try:
      return(self.Weightings[wayType])
    except KeyError:
      # Default: if no weighting is defined,
      # then assume it can't be routed
      return(0)


