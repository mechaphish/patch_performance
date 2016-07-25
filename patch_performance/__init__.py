
from cb_performance import get_all_cb_sets_perf, group_poll_results, get_perf_totals
from cb_score import compute_overhead
from perf_constants import SIZE_PERF_NAME
from farnsworth.models import PatchScore, Round, PatchType
import logging

l = logging.getLogger("patch_performance.main")


def compute_patch_performance(target_cs):
    """
        Compute patch performance for all patched binaries of given CS.
        This will update DB with results.
    :param target_cs: CS for which patch performance needs to be computed.
    :return: None.
    """
    l.info("Trying to compute patch performance for CS:" + str(target_cs.id))
    patched_bins_perf = get_all_cb_sets_perf(target_cs)
    l.info("Got Raw Perf Scores.")

    l.info("Trying to Group Raw Scores.")
    grouped_perf_results = group_poll_results(patched_bins_perf)
    l.info("Grouped Raw Scores.")

    original_cbs_perf = []
    if 'original' in grouped_perf_results:
        original_cbs_perf = grouped_perf_results['original']
        del grouped_perf_results['original']
    if len(original_cbs_perf) <= 0:
        l.warning("No polls have been evaluated against original binary. "
                  "Ignoring this round of patch performance computation.")
        return

    if len(original_cbs_perf['fail']) > 0:
        l.warning("Weired. There are some failed polls for original binary, ignoring failed polls.")

    # consider only passed polls
    original_cbs_perf = original_cbs_perf['pass']

    for curr_patch_type in grouped_perf_results:
        l.info("Computing Scores for Patch Type:" + str(curr_patch_type))
        pass_perf_objects = grouped_perf_results[curr_patch_type]['pass']
        patched_cbs_pass_poll_ids = []
        if len(pass_perf_objects) > 0:
            patched_cbs_pass_poll_ids = map(lambda perf_obj: perf_obj.poll.id, pass_perf_objects)
        else:
            l.warning("No passed polls found for Patch Type:" + str(curr_patch_type))
            # skip to next patch type
            continue
        failed_perf_objects = grouped_perf_results[curr_patch_type]['fail']
        has_fails = len(failed_perf_objects) > 0

        failed_polls = []
        if has_fails:
            failed_polls = map(lambda perf_obj: perf_obj.poll.id, failed_perf_objects)
        failed_polls_json = {'poll_ids': list(failed_polls)}

        original_cbs_pass_poll_ids = map(lambda perf_obj: perf_obj.poll.id, original_cbs_perf)

        common_pass_poll_ids = set(original_cbs_pass_poll_ids)
        common_pass_poll_ids.intersection_update(patched_cbs_pass_poll_ids)

        if not (len(common_pass_poll_ids) > 0):
            l.warning("No polls have been common between original and patched cbs. Ignoring patch type:" +
                      str(curr_patch_type))
            # skip to next patch type
            continue

        polls_included = {'poll_ids': list(common_pass_poll_ids)}

        base_perf_objects = filter(lambda perf_obj: perf_obj.poll.id in common_pass_poll_ids, original_cbs_perf)
        patched_perf_objects = filter(lambda perf_obj: perf_obj.poll.id in common_pass_poll_ids, pass_perf_objects)

        base_perf_jsons = map(lambda perf_obj: perf_obj.performances['perf']['median'], base_perf_objects)
        patched_perf_jsons = map(lambda perf_obj: perf_obj.performances['perf']['median'], patched_perf_objects)

        base_perf_total = get_perf_totals(base_perf_jsons)
        # get the size of binaries, size of the binaries will be same on all runs
        base_perf_total[SIZE_PERF_NAME] = base_perf_jsons[0][SIZE_PERF_NAME]
        patched_perf_total = get_perf_totals(patched_perf_jsons)
        # again size of binaries will be same across all tests.
        patched_perf_total[SIZE_PERF_NAME] = patched_perf_jsons[0][SIZE_PERF_NAME]

        target_score = compute_overhead(base_perf_total, patched_perf_total)

        l.info("Trying to create PatchScore into DB for patch type:" + str(curr_patch_type) + " for cs:" +
               str(target_cs.id))
        # convert patch type name to PatchType
        curr_patch_type = PatchType.get(PatchType.name == curr_patch_type)
        # create patch score
        PatchScore.create(cs=target_cs, patch_type=curr_patch_type, num_polls=len(common_pass_poll_ids),
                          polls_included=polls_included, has_failed_polls=has_fails, failed_polls=failed_polls_json,
                          round=Round.current_round(), perf_score=target_score)





