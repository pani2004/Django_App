from decimal import Decimal
from statistics import median


def apply_quality_heuristics(activities, batch):
    """Flag suspicious quantities and overlapping utility periods within a batch."""
    by_type: dict[str, list] = {}
    for activity in activities:
        by_type.setdefault(activity.activity_type, []).append(activity)

    for activity_type, group in by_type.items():
        values = [
            Decimal(str(a.activity_value))
            for a in group
            if a.activity_value is not None
        ]
        if len(values) < 3:
            continue
        med = median([float(v) for v in values])
        if med == 0:
            continue
        for activity in group:
            if activity.activity_value is None:
                continue
            v = float(activity.activity_value)
            if abs(v - med) > 3 * med:
                flags = list(activity.quality_flags or [])
                if "suspicious_quantity" not in flags:
                    flags.append("suspicious_quantity")
                    activity.quality_flags = flags
                    activity.save(update_fields=["quality_flags", "updated_at"])

    if batch.source == "UTILITY":
        _flag_overlapping_utility(activities)


def _flag_overlapping_utility(activities):
    by_meter: dict[str, list] = {}
    for a in activities:
        key = f"{a.facility_code}:{a.source_record_id}"
        by_meter.setdefault(key, []).append(a)

    for group in by_meter.values():
        if len(group) < 2:
            continue
        sorted_a = sorted(group, key=lambda x: x.period_start or x.created_at.date())
        for i in range(len(sorted_a) - 1):
            a, b = sorted_a[i], sorted_a[i + 1]
            if a.period_end and b.period_start and a.period_end >= b.period_start:
                for act in (a, b):
                    flags = list(act.quality_flags or [])
                    if "overlapping_billing_period" not in flags:
                        flags.append("overlapping_billing_period")
                        act.quality_flags = flags
                        act.save(update_fields=["quality_flags", "updated_at"])
