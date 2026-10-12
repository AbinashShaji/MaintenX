"""
MaintenX Workflow State Machine and Security Module.

Defines the authoritative state machine for maintenance requests:
REQUESTED (pending) → APPROVED/ASSIGNED (assigned)
ASSIGNED (assigned) → ON WORK (in_progress)
ON WORK (in_progress) → RECTIFIED (resolved)
RECTIFIED (resolved) → CLOSED (closed)

Any transition violating this pipeline is strictly rejected.
"""

from typing import Tuple, Optional

# Status Constants
STATUS_REQUESTED = 'pending'
STATUS_ASSIGNED = 'assigned'
STATUS_ON_WORK = 'in_progress'
STATUS_RECTIFIED = 'resolved'
STATUS_CLOSED = 'closed'

STATUS_LABELS = {
    STATUS_REQUESTED: 'Requested',
    STATUS_ASSIGNED: 'Assigned',
    STATUS_ON_WORK: 'On Work',
    STATUS_RECTIFIED: 'Rectified',
    STATUS_CLOSED: 'Closed'
}

# Strict Allowed Transitions Map
ALLOWED_TRANSITIONS = {
    STATUS_REQUESTED: {STATUS_ASSIGNED},
    STATUS_ASSIGNED: {STATUS_ON_WORK, STATUS_ASSIGNED},  # Re-assignment permitted while in assigned
    STATUS_ON_WORK: {STATUS_RECTIFIED},
    STATUS_RECTIFIED: {STATUS_CLOSED},
    STATUS_CLOSED: set()  # Terminal state: no further transitions permitted
}

def can_transition(current_status: str, target_status: str) -> bool:
    """
    Checks if moving from current_status to target_status is permitted.
    """
    if current_status not in ALLOWED_TRANSITIONS:
        return False
    return target_status in ALLOWED_TRANSITIONS[current_status]

def validate_transition(current_status: str, target_status: str) -> Tuple[bool, str]:
    """
    Validates a transition according to the strict state machine.
    Returns (is_valid: bool, error_message: str).
    """
    if current_status not in ALLOWED_TRANSITIONS:
        return False, f"Unknown status: '{current_status}'."
    if target_status not in STATUS_LABELS:
        return False, f"Unknown target status: '{target_status}'."

    if not can_transition(current_status, target_status):
        curr_lbl = STATUS_LABELS.get(current_status, current_status)
        tgt_lbl = STATUS_LABELS.get(target_status, target_status)
        return False, (
            f"Invalid transition: Cannot move request from '{curr_lbl}' to '{tgt_lbl}'. "
            "Workflow must follow: REQUESTED → APPROVED/ASSIGNED → ON WORK → RECTIFIED → CLOSED."
        )

    return True, ""

def log_request_update(cursor, request_id: int, user_id: int, old_status: Optional[str], new_status: str, note: str):
    """
    Guarantees every status change stores:
    - user_id (User performing action)
    - old_status (Previous status)
    - new_status (New status)
    - note (Action note)
    - created_at (Timestamp)
    """
    cursor.execute("""
        INSERT INTO request_updates (request_id, user_id, old_status, new_status, note, created_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (request_id, user_id, old_status, new_status, note))
