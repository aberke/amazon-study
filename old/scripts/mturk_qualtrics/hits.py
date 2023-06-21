import numpy as np
import pandas as pd
import datetime
import boto3


class HITUtils:
    def __init__(self, config):
        self.client = boto3.client(
            "mturk",
            region_name=config["region_name"],
            aws_access_key_id=config["aws_access_key_id"],
            aws_secret_access_key=config["aws_secret_access_key"],
        )
        self.client_initialized = True

    # payment
    def approve_assignments(self, assignment_data, exclude_bonus=False, dry_run=True):
        pay_record = []
        for a in assignment_data:
            a["paid_bonus"] = 0
            a["approved"] = False
            a["paid_base"] = pd.NaT
            if a["met_requirements"]:
                if not dry_run and  a["assignment_status"] != "Approved":
                    self.client.approve_assignment(AssignmentId=a["assignment_id"])
                a["approved"] = True
                a["paid_base"] = datetime.datetime.now()
                if a["bonus_amount"] > 0 and not exclude_bonus:
                    assert (
                        a["bonus_amount"] <= 0.5
                    )  # just...make sure we do not pay bonuses over $0.50
                    if not dry_run:
                        self.client.send_bonus(
                            WorkerId=a["worker_id"],
                            AssignmentId=a["assignment_id"],
                            BonusAmount=str(a["bonus_amount"]),
                            Reason="Bonus payment as described in survey",
                        )

                    a["paid_bonus"] = a["bonus_amount"]
            pay_record.append(a)
        return pay_record

    # Get HIT list
    ########################
    def get_amazon_survey_HITs(self):
        """get list of HITs"""
        assert self.client_initialized

        def delete_key(x, k):
            """deletes key k and returns x"""
            del x[k]
            return x

        # adjust depending on what criteria our HIT needs to meet in order to be included
        def is_survey_hit(hit):
            """returns True if the given hit object is a survey HIT"""
            return "online purchases" in hit["Title"]

        hit_pager = self.client.get_paginator("list_hits")
        pages = hit_pager.paginate(PaginationConfig={"MaxItems": 5000, "PageSize": 100})
        survey_HITs = []
        for page in pages:
            page_survey_hits = filter(is_survey_hit, page["HITs"])
            # 'Question' is very long, it gets annoying; delete it
            sh = map(lambda x: delete_key(x, "Question"), page_survey_hits)
            survey_HITs = survey_HITs + list(sh)
        return survey_HITs

    def get_worker_assignment_data(self, HIT_id, qualtrics_df):
        """returns a list of dicts representing HIT assignment data for payment.

        each dict in the list is of the form:
         {'worker_id': str,
          'random_id': str,
          'bonus_amount': int | np.nan,
          'passed_attention': bool | np.nan,
          'met_requirements': bool | np.nan,
          'found_randomID_in_qualtrics': bool},

        notes:
        - met_requirements and passed_attention are np.nan if we
          cannot link an assignment to a qualtrics response.
        - bonus_amount is an int, so `50` corresponds to a $.50
          bonus., `05` to $.05, etc.

        """
        assignment_results = []
        HIT_assignments = self.get_assignments_for_HIT(HIT_id)
        for assignment in HIT_assignments:
            # get qualtrics response row
            randomid_entered_on_hit = assignment[
                "Answer"
            ]  # parse_survey_answer(assignment['Answer'])
            worker_id = assignment["WorkerId"]
            this_assignment_data = {
                "assignment_id": assignment["AssignmentId"],
                "assignment_status": assignment["AssignmentStatus"],
                "worker_id": worker_id,
                "random_id": randomid_entered_on_hit,
            }
            # dc - 10/4/22
            # Note: some workers use their WorkerId as their RandomID in the qualtrics
            # survey; e.g.:
            # 'worker_id': 'A28L0Q6S2GGBJQ',
            # 'random_id': 'A28L0Q6S2GGBJQ'
            # no way to track what survey response that assignment connects to, so no way to check
            # bonuses etc.
            # the below code tries to fix for this but there are edge cases, like multiple submissions
            # from the same worker if they enter their worker ID as their random ID each time.
            assignment_qualtrics_row = qualtrics_df[
                qualtrics_df.RandomID == randomid_entered_on_hit
            ]
            if len(assignment_qualtrics_row) == 0:
                # if it's 0, we didn't find the randomID in our qualtrics responses
                this_assignment_data["found_randomID_in_qualtrics"] = False
                this_assignment_data["bonus_amount"] = 0
                this_assignment_data["passed_attention"] = np.nan
                this_assignment_data["met_requirements"] = np.nan
                assignment_results.append(this_assignment_data)
                continue
            assert len(assignment_qualtrics_row) == 1
            print("qualtrics row:", assignment_qualtrics_row.to_markdown())
            assignment_qualtrics_row = assignment_qualtrics_row.iloc[0]
            bonus_amount = get_bonus_amount(assignment_qualtrics_row)
            this_assignment_data["bonus_amount"] = (
                bonus_amount / 100.0 if bonus_amount > 0 else 0
            )
            this_assignment_data["passed_attention"] = did_pass_attention(
                assignment_qualtrics_row
            )
            this_assignment_data["found_randomID_in_qualtrics"] = True
            requirement_cols = [c for c in qualtrics_df.columns if "requirements" in c]
            # should sum to 2 if worker met both requirements
            requirement_vals = assignment_qualtrics_row[requirement_cols].dropna()
            if (len(requirement_vals) > 0):
                worker_met_requirements = (
                    assignment_qualtrics_row[requirement_cols].astype(int).sum() == 2
                )
            else:
                worker_met_requirements = True
            this_assignment_data["met_requirements"] = worker_met_requirements
            assignment_results.append(this_assignment_data)
        return assignment_results

    # Get all assignments for a given HIT id
    def get_assignments_for_HIT(self, HIT_id, filter="Submitted"):
        """returns list of assignment dicts from all iterable pages for HIT_id"""
        all_assignments = []

        assn_pager = self.client.get_paginator("list_assignments_for_hit")
        pages = assn_pager.paginate(
            HITId=HIT_id,
            # AssignmentStatuses=[filter],
            PaginationConfig={"MaxItems": 5000, "PageSize": 100},
        )
        # pgs = list(pages)
        # print("num pages:", len(pgs), pgs)
        # print("first page:", pgs[0])
        # print("first assignment:", pgs[0]["Assignments"])
        for page in pages:
            for assignment in page["Assignments"]:
                assignment["Answer"] = parse_survey_answer(assignment["Answer"])
                all_assignments.append(assignment)
        return all_assignments


# UTILITIES
##############################

# parsing mturk API responses
def parse_survey_answer(answer):
    """Needed because aws stores the answer as xml...
    returns just the code from the XML survey answer from the hit"""
    import xml.etree.ElementTree as ET

    tree = ET.fromstring(answer)
    notags = ET.tostring(tree, encoding="unicode", method="text").replace(
        "surveycode", ""
    )
    return notags


# utilities for getting information about an assignment from qualtrics
def get_bonus_amount(qualtrics_row):
    """Returns bonus amount ($.05, $.20, or $.50) if response was in bonus condition, $0 otherwise."""
    has_bonus = (
        "bonus" in qualtrics_row["incentive"]
    )  # if bonus not in incentive code, they don't get a bonus
    bonus_amt = qualtrics_row["incentive"].replace("bonus-", "") if has_bonus else 0
    return int(bonus_amt)


def did_pass_attention(qualtrics_row):
    """returns True if they passed the attention check, false otherwise."""
    # get the attention columns
    attn_cols = list(filter(lambda x: "attn" in x, list(qualtrics_row.index)))
    # they have three options. to pass they need to check all.
    assert len(attn_cols) == 3
    attn_answers = qualtrics_row[attn_cols].fillna(0).astype("int")
    # if all answers are 1 (pass), sum should be 3.
    return np.sum(attn_answers.values) == 3
