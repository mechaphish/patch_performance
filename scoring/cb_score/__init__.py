"""
Computes Performance overhead of patched binaries according to DARPA suggested methods.
"""

from ..perf_constants import *


def compute_overhead(unpatched_perf, patched_perf):
    """
        Compute overhead from the performance of the patched and unpatched binaries.

    :param unpatched_perf: Performance dictionary of unpatched or original cb.
    :param patched_perf: Performance dictionary of patched cb.
    :return: Dictionary containing overheads
    """
    to_ret = {MEM_USE_OVER_HEAD_KEY: -1, FILE_SIZE_OVER_HEAD_KEY: -1, EXEC_OVER_HEAD_KEY: -1}

    # mem use overhead
    # formula = 0.5 * (rep_max_rss/ref_max_rss + rep_min_flt/ref_min_flt)
    rep_max_rss = None
    ref_max_rss = None
    rep_min_flt = None
    ref_min_flt = None

    if RSS_PERF_NAME in unpatched_perf:
        ref_max_rss = unpatched_perf[RSS_PERF_NAME]
    if RSS_PERF_NAME in patched_perf:
        rep_max_rss = patched_perf[RSS_PERF_NAME]
    if FLT_PERF_NAME in unpatched_perf:
        ref_min_flt = unpatched_perf[FLT_PERF_NAME]
    if FLT_PERF_NAME in patched_perf:
        rep_min_flt = patched_perf[FLT_PERF_NAME]

    mem_first_term = None
    if ref_max_rss is not None and rep_max_rss is not None:
        mem_first_term = 0
        if float(ref_max_rss) != 0:
            mem_first_term = float(rep_max_rss) / float(ref_max_rss)
        else:
            mem_first_term = float(rep_max_rss)

    mem_second_term = None
    if ref_min_flt is not None and rep_min_flt is not None:
        mem_second_term = 0
        if float(ref_min_flt) != 0:
            mem_second_term = float(rep_min_flt) / float(ref_min_flt)
        else:
            mem_second_term = float(rep_min_flt)

    if mem_first_term is not None and mem_second_term is not None:
        to_ret[MEM_USE_OVER_HEAD_KEY] = 0.5 * (mem_first_term + mem_second_term)

    # exec time overhead
    # formula = rep_task_clock/ref_task_clock
    rep_task_clock = None
    ref_task_clock = None

    if TSK_CLOCK_PERF_NAME in unpatched_perf:
        ref_task_clock = unpatched_perf[TSK_CLOCK_PERF_NAME]
    if TSK_CLOCK_PERF_NAME in patched_perf:
        rep_task_clock = patched_perf[TSK_CLOCK_PERF_NAME]

    if ref_task_clock is not None and rep_task_clock is not None:
        if float(ref_task_clock) != 0:
            to_ret[EXEC_OVER_HEAD_KEY] = float(rep_task_clock) / float(ref_task_clock)
        else:
            to_ret[EXEC_OVER_HEAD_KEY] = float(rep_task_clock)

    # file size overhead
    # formula = rep_file_size/ref_file_size
    rep_file_size = None
    ref_file_size = None
    if SIZE_PERF_NAME in unpatched_perf:
        ref_file_size = unpatched_perf[SIZE_PERF_NAME]
    if SIZE_PERF_NAME in patched_perf:
        rep_file_size = patched_perf[SIZE_PERF_NAME]

    if rep_file_size is not None and ref_file_size is not None:
        if float(ref_file_size) != 0:
            to_ret[FILE_SIZE_OVER_HEAD_KEY] = float(rep_file_size) / float(ref_file_size)
        else:
            to_ret[FILE_SIZE_OVER_HEAD_KEY] = float(rep_file_size)

    return {'score': {'cfe_ratio': to_ret, 'ref': unpatched_perf, 'rep': patched_perf}}

