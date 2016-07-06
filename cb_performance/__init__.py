"""

"""

import logging

l = logging.getLogger("patch_reputation.cb_performance")


def get_all_cb_sets_perf(target_cs, min_polls_tested=25):
    """
        Gets performance of all patched binaries of a CS.

        This will return performances of only those polls which have been tested
        against all patched binaries.

        So, if a poll has been tested on only one patched binary. It will not be
        considered for performance.
    :param target_cs: CS for which the performance need to be computed.
    :param min_polls_tested: Minimum number of polls that need to tested for a cb to be considered.
    :return: Dictionary of {patch_type: {poll_id: perf_obj, ..}, ..}
    """
    to_ret = {}
    # Here we get all performance objects that belong to a CB
    # whose cs is same as the provided CS.
    # TODO: Complete this
    # TODO: also, consider only those binaries for which certain number of polls have been tested.
    l.info("Trying to get perf objects from DB.")
    raw_perf_objs = []
    l.info("Got :" + str(len(raw_perf_objs)) + " perf objects from DB.")

    l.info("Trying to get polls which every patched binary have been tested.")

    # get patched binary set, poll id, perf object dict
    cb_set_perf_dict = {}
    for curr_perf_obj in raw_perf_objs:
        # TODO: Change this to patched binary set
        curr_patch_type = curr_perf_obj.patch_type
        if curr_patch_type not in cb_set_perf_dict:
            cb_set_perf_dict[curr_patch_type] = {}
        cb_set_perf_dict[curr_patch_type][curr_perf_obj.poll.id] = curr_perf_obj

    # get common poll ids across all perf objects.
    common_valid_poll_ids = None
    # This is so that we can remove patch_types which does not satisfy the minimum testing criteria
    cb_set_perf_dict_copy = dict(cb_set_perf_dict)
    for curr_patch_type in cb_set_perf_dict:
        curr_key_list = cb_set_perf_dict[curr_patch_type].keys()
        # see that the patched binary is tested against minimum number of polls.
        # if not, ignore it.
        if len(curr_key_list) >= min_polls_tested:
            if common_valid_poll_ids is None:
                common_valid_poll_ids = set(curr_key_list)
            common_valid_poll_ids.intersection_update(set(curr_key_list))
        else:
            del cb_set_perf_dict_copy[curr_patch_type]

    # get redacted dictionary
    cb_set_perf_dict = dict(cb_set_perf_dict_copy)
    if common_valid_poll_ids is not None:
        l.info("Got:" + str(len(common_valid_poll_ids)) + " Polls that are common.")
    else:
        if len(raw_perf_objs) != 0:
            l.warning("common valid polls is None, although there are some raw_perf_objs.")
        else:
            l.info("No common valid polls.")

    # for each of this common poll, get performance of all patched binaries.
    if (common_valid_poll_ids is not None) and (len(common_valid_poll_ids) > 0):
        l.info("Trying to get perf objects for:" + str(len(common_valid_poll_ids)) + " common poll ids.")
        # iterate for each patched binary set
        for curr_patch_type in cb_set_perf_dict:
            # iterate thru each common poll id
            for common_valid_poll_id in common_valid_poll_ids:
                if curr_patch_type not in to_ret:
                    to_ret[curr_patch_type] = {}
                # get perf object ans update the return.
                to_ret[curr_patch_type][common_valid_poll_id] = cb_set_perf_dict[curr_patch_type][common_valid_poll_id]
        l.info("Got performance objects for all common valid polls.")
    else:
        l.warning("No performance objects can be returned. Not a single poll has been tested on all "
                  "patched binaries set")

    return to_ret


def group_poll_results(cbset_perf_dict):
    """
        Given, Dictionary of {patch_type: {poll_id: perf_obj, ..}, ..}
        Groups poll results into pass and fail
    :param cbset_perf_dict: Dictionary of {patch_type: {poll_id: perf_obj, ..}, ..}
    :return: Dictionary {patch_type: {'pass': [List of perf objects], 'fail': [List of perf objects]}
    """
    to_ret = {}
    if cbset_perf_dict:
        l.info("Trying to group poll results of:" + str(len(cbset_perf_dict)) + " patched binaries set.")
        for curr_patch_type in cbset_perf_dict:
            curr_dict = {"pass": [], "fail": []}
            if curr_patch_type not in to_ret:
                to_ret[curr_patch_type] = curr_dict
            else:
                curr_dict = to_ret[curr_patch_type]
            for curr_perf_id in cbset_perf_dict[curr_patch_type]:
                perf_obj = cbset_perf_dict[curr_patch_type][curr_perf_id]
                if perf_obj.is_poll_ok:
                    curr_dict["pass"].append(perf_obj)
                else:
                    curr_dict["fail"].append(perf_obj)
        l.info("Grouped Poll Results into pass and fail results.")
    else:
        l.warning("No poll results to group.")
    return to_ret


def get_perf_totals(perf_json_list):
    """
        Get Totals of all performance numbers.
    :param perf_json_list: list of jsons (or dictionaries) of all performance values.
    :return: Dictionary containing totals of all perf counters.
    """
    RSS_PERF_NAME = "rss"
    FLT_PERF_NAME = "flt"
    CPU_CLOCK_PERF_NAME = "cpu_clock"
    TSK_CLOCK_PERF_NAME = "task_clock"
    to_ret = {RSS_PERF_NAME: 0.0, FLT_PERF_NAME: 0.0,
              CPU_CLOCK_PERF_NAME: 0.0, TSK_CLOCK_PERF_NAME: 0.0}
    perf_keys = [RSS_PERF_NAME, FLT_PERF_NAME, CPU_CLOCK_PERF_NAME, TSK_CLOCK_PERF_NAME]

    # iterate thru each performance dict
    for curr_json in perf_json_list:
        # sum each of the performance value.
        for curr_perf_key in perf_keys:
            if curr_perf_key in curr_json:
                to_ret[curr_perf_key] += curr_json[curr_perf_key]

    return to_ret

