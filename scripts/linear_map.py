def linear_map_ints(left, right):
  sX, eX = left
  sY, eY = right

  def m(x):
    if x <= sX:
      return sY
    elif x >= eX:
      return eY
    else:
      return int(x * ((eY - sY) / (eX - sX)) + sY)
  return m

def linear_map(nums, cats):
  ''' Map values to categories
  Usage:
  m = linear_map([0, 1], ['small', 'medium', 'large'])
  m(0.30) == 'small'
  m(0.40) == 'medium'
  m(0.80) == 'large'
  '''
  m = linear_map_ints(nums, (0, len(cats)))
  return lambda x: cats[-1 if m(x) == len(cats) else m(x)]
