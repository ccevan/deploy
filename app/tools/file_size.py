traditional = [
    (1024 ** 5, 'P'),
    (1024 ** 4, 'T'),
    (1024 ** 3, 'G'),
    (1024 ** 2, 'M'),
    (1024 ** 1, 'K'),
    (1024 ** 0, 'B'),
]

alternative = [
    (1024 ** 5, ' PB'),
    (1024 ** 4, ' TB'),
    (1024 ** 3, ' GB'),
    (1024 ** 2, ' MB'),
    (1024 ** 1, ' KB'),
    (1024 ** 0, (' byte', ' bytes')),
]

verbose = [
    (1024 ** 5, (' petabyte', ' petabytes')),
    (1024 ** 4, (' terabyte', ' terabytes')),
    (1024 ** 3, (' gigabyte', ' gigabytes')),
    (1024 ** 2, (' megabyte', ' megabytes')),
    (1024 ** 1, (' kilobyte', ' kilobytes')),
    (1024 ** 0, (' byte', ' bytes')),
]

iec = [
    (1024 ** 5, 'Pi'),
    (1024 ** 4, 'Ti'),
    (1024 ** 3, 'Gi'),
    (1024 ** 2, 'Mi'),
    (1024 ** 1, 'Ki'),
    (1024 ** 0, ''),
]

si = [
    (1000 ** 5, 'P'),
    (1000 ** 4, 'T'),
    (1000 ** 3, 'G'),
    (1000 ** 2, 'M'),
    (1000 ** 1, 'K'),
    (1000 ** 0, 'B'),
]


def size(bytes, system=traditional):
    """
    输入bytes格式数据,输出格式化数据
    :param bytes: bytes 数据
    :param system:  转换模式
    :return: 输出自定义单位数据
    """
    factor, suffix = None, None
    for factor, suffix in system:
        if bytes >= factor:
            break
    amount = int(bytes / factor)
    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return str(amount) + suffix
