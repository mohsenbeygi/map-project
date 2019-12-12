class RoutingWeights:
  def __init__(self):
    self.Weightings = {
      'motorway': {'car':10},
      'trunk':    {'car':10},
      'primary':  {'car':2, 'foot':1},
      'secondary': {'car':1.5, 'foot':1},
      'tertiary': {'car':1, 'foot':1},
      'unclassified': {'car':1, 'foot':1},
      'minor': {'car':1, 'foot':1},
      'cycleway': {'foot':0.2},
      'residential': {'car':0.7, 'foot':1},
      'track': {'car':1, 'foot':1},
      'service': {'car':1, 'foot':1},
      'bridleway': {'foot':1},
      'footway': {'foot':1},
      'steps': {'foot':1},
      }

  def get(self, transport, wayType):
    try:
      return(self.Weightings[wayType][transport])
    except KeyError:
      # Default: if no weighting is defined, then assume it can't be routed
      return(0)


