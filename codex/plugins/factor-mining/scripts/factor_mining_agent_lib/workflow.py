from typing import Any, Mapping, Sequence


TERMINAL_WORKFLOW_STAGES = {"done", "failed", "cancelled", "canceled"}
TERMINAL_JOB_STATUSES = {"done", "succeeded", "success", "failed", "error", "cancelled", "canceled"}
SUCCESS_JOB_STATUSES = {"done", "succeeded", "success"}
FAILED_JOB_STATUSES = {"failed", "error"}
CANCELLED_JOB_STATUSES = {"cancelled", "canceled"}


def is_workflow_terminal(workflow: Mapping[str, Any], jobs: Sequence[Mapping[str, Any]] | None = None) -> bool:
    stage = str(workflow.get("stage") or workflow.get("status") or "").lower()
    if stage in TERMINAL_WORKFLOW_STAGES:
        return True
    jobs = jobs or []
    if jobs:
        return all(str(job.get("status") or "").lower() in TERMINAL_JOB_STATUSES for job in jobs)
    return False


def terminal_outcome(workflow: Mapping[str, Any], jobs: Sequence[Mapping[str, Any]] | None = None) -> dict[str, Any]:
    jobs = list(jobs or [])
    workflow_stage = str(workflow.get("stage") or workflow.get("status") or "").lower()
    job_statuses = [str(job.get("status") or "").lower() for job in jobs]
    failures = [
        job
        for job in jobs
        if str(job.get("status") or "").lower() in FAILED_JOB_STATUSES | CANCELLED_JOB_STATUSES
    ]

    if workflow_stage in {"failed"} or any(status in FAILED_JOB_STATUSES for status in job_statuses):
        status = "failed"
        ok = False
    elif workflow_stage in {"cancelled", "canceled"} or any(status in CANCELLED_JOB_STATUSES for status in job_statuses):
        status = "cancelled"
        ok = False
    elif jobs:
        if all(status in SUCCESS_JOB_STATUSES for status in job_statuses):
            status = "succeeded"
            ok = True
        else:
            status = "unknown_terminal"
            ok = False
    elif workflow_stage == "done":
        status = "succeeded"
        ok = True
    else:
        status = "unknown_terminal"
        ok = False

    outcome: dict[str, Any] = {
        "ok": ok,
        "status": status,
        "terminal_status": status,
    }
    if failures:
        outcome["failures"] = failures
    return outcome


def summarize_factor_card(card: Mapping[str, Any], jobs: Sequence[Mapping[str, Any]] | None = None) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "factor_name": card.get("factor_name") or card.get("name"),
        "metrics": card.get("metrics") or {},
        "artifacts": card.get("artifacts") or {},
        "jobs": list(jobs or []),
    }
    failures = [
        job
        for job in summary["jobs"]
        if str(job.get("status") or "").lower() in FAILED_JOB_STATUSES | CANCELLED_JOB_STATUSES
    ]
    if failures:
        summary["failures"] = failures
    return summary
