def max_k_subarrays(a, k):
    """Maximum total sum of at most k non-overlapping, non-empty contiguous subarrays of `a`.

    Choosing no subarray at all is allowed and gives 0.
    """
    k = min(k, len(a))
    neg = float("-inf")
    out = [0] * (k + 1)    # best total using j subarrays, currently outside a subarray
    ins = [neg] * (k + 1)  # best total using j subarrays, currently inside the j-th one
    for x in a:
        for j in range(k, 0, -1):
            ins[j] = max(ins[j], out[j - 1]) + x
            out[j] = max(out[j], ins[j])
    return max(out)
