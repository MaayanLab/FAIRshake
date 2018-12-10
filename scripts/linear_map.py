def linear_map(nums, cats):
  ''' Map values to categories
  Usage:
  m = linear_map([0, 1], ['small', 'medium', 'large'])
  m(0.30) == 'small'
  m(0.40) == 'medium'
  m(0.80) == 'large'
  '''
  sX, eX = nums[0], nums[1]
  sY, eY = 0, len(cats)

  def m(x):
    if x <= sX:
      return cats[0]
    elif x >= eX:
      return cats[1]
    else:
      return cats[int(x * ((eY - sY) / (eX - sX)))]
  return m
