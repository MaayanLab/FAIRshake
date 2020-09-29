import itertools as it
from collections import deque

def minmax(it, key=lambda t: t):
  _min = None
  _max = None
  for el in map(key, it):
    if _min is None or _min > el:
      _min = el
    if _max is None or _max < el:
      _max = el
  #
  return (_min, _max)

class UnionPaginatorPage:
  def __init__(self, paginator, querysets, page):
    self.paginator = paginator
    self.has_previous = page > 1
    self.number = page
    self.has_next = page < paginator.num_pages
    self._querysets = querysets
  #
  def __iter__(self):
    Q = deque(iter(qs) for qs in self._querysets)
    while Q:
      qs_iter = Q.popleft()
      try:
        yield next(qs_iter)
        Q.append(qs_iter)
      except StopIteration:
        pass

class UnionPaginator:
  def __init__(self, itemsets, page_size):
    self.paginator = self
    self._page_size = page_size
    self._itemsets = itemsets
    self._sizes = [items.filter(id__isnull=False).count() for items in itemsets]
    self._iteminds = [zip(it.repeat(ind), range(size)) for ind, size in enumerate(self._sizes)]
    self._total_size = sum(self._sizes)
    self._init_plan()
    self.num_pages = len(self._plan)
  #
  def _init_plan(self):
    self._plan = []
    if not self._total_size:
      return
    self._plan.append([])
    Q = deque(map(iter, self._iteminds))
    while Q:
      try:
        items = Q.pop()
        item = next(items)
        if len(self._plan[-1]) >= self._page_size:
          self._plan.append([])
        self._plan[-1].append(item)
        Q.appendleft(items)
      except StopIteration:
        pass
  #
  def _get_plan_qs(self, plan):
    ranges = {
      itemset_ind: minmax(item_ind, key=lambda t: t[1])
      for itemset_ind, item_ind in it.groupby(
        sorted(plan), key=lambda t: t[0]
      )
      if item_ind
    }
    _, querysets = zip(*sorted([
      (itemset_ind, self._itemsets[itemset_ind][_min:_max+1])
      for itemset_ind, (_min, _max) in ranges.items()
    ]))
    return querysets
  #
  def get_page(self, page):
    if not self._plan:
      return UnionPaginatorPage(self, [], 1)
    try:
      page = min(max(1, int(page)), self.num_pages)
    except:
      page = 1
    #
    return UnionPaginatorPage(
      self, self._get_plan_qs(self._plan[page-1]), page
    )
