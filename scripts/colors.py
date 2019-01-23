def hex_to_rgba(val, alpha=1.):
  val = val | 0x1000000
  return 'rgba(%d, %d, %d, %0.2f)' % (
    int(hex(val)[3:5], 16),
    int(hex(val)[5:7], 16),
    int(hex(val)[7:9], 16),
    alpha,
  )
