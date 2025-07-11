# tasks/utils.py

import json
from collections import defaultdict

def validate_submission(submission, question_paper):
    warnings = []
    marks_per_question = defaultdict(float)
    question_lookup = {str(q['id']): q for q in (question_paper.questions if question_paper else [])}
    optional_groups = defaultdict(list)

    try:
        annotation_data = json.loads(submission.canvas_json or '[]')
    except json.JSONDecodeError:
        submission.warnings = ['Invalid JSON format in canvas data.']
        return

    for canvas_str in annotation_data:
        try:
            data = json.loads(canvas_str)
        except json.JSONDecodeError:
            continue
        for obj in data.get("objects", []):
            qid = str(obj.get("question_id"))
            marks = float(obj.get("marks", 0))
            if qid and qid in question_lookup:
                marks_per_question[qid] += marks
                q_info = question_lookup[qid]
                if q_info.get("optional_group"):
                    optional_groups[q_info["optional_group"]].append(qid)

    for qid, total in marks_per_question.items():
        max_allowed = question_lookup[qid]["max_marks"]
        if total > max_allowed:
            warnings.append(f"⚠️ Question {qid} overmarked: {total}/{max_allowed}")

    for group, qids in optional_groups.items():
        answered = [qid for qid in set(qids) if marks_per_question[qid] > 0]
        if len(answered) > 2:
            warnings.append(f"⚠️ Optional group '{group}' has {len(answered)} answered. Only 2 allowed.")

    submission.total_marks = sum(
        min(marks_per_question[qid], question_lookup[qid]["max_marks"])
        for qid in marks_per_question
    )
    submission.marks_per_question = dict(marks_per_question)
    submission.warnings = warnings
