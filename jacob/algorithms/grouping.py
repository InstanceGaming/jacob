
def deltas(items):
    d = []
    for i, item in enumerate(items):
        if i:
            prev = items[i - 1]
            d.append(item - prev)
    return d


def stride_range(strides, index):
    stride = strides[index]
    if index == 0:
        return range(0, stride + 1)
    else:
        d = deltas(strides)
        left = stride - d[index - 1] + 1
        return range(left, stride + 1)
