from types import SimpleNamespace

from app.matcher import match_email

# Plain stand-in objects: the matcher only reads .name and .organization,
# so the tests don't need a database at all.
GATES = SimpleNamespace(id=1, name="Gates Scholarship", organization="Gates Foundation")
ELKS = SimpleNamespace(id=2, name="Most Valuable Student", organization="Elks National Foundation")
ALL = [GATES, ELKS]


def test_award_email_matches_and_is_flagged_awarded():
    result = match_email(
        ALL,
        sender="Gates Team <notifications@gatesfoundation.org>",
        subject="Your Gates Scholarship application",
        body="Congratulations! We are pleased to award you $5,000.",
    )
    assert result["scholarship"] is GATES
    assert result["outcome"] == "awarded"


def test_rejection_email_is_flagged_rejected():
    result = match_email(
        ALL,
        sender="scholarships@elks.org",
        subject="Update on your Most Valuable Student application",
        body="We regret to inform you that you were not selected this year.",
    )
    assert result["scholarship"] is ELKS
    assert result["outcome"] == "rejected"


def test_picks_the_right_scholarship_when_several_exist():
    result = match_email(
        ALL,
        sender="notifications@gatesfoundation.org",
        subject="Reminder",
        body="Please finish your Gates Scholarship application.",
    )
    assert result["scholarship"] is GATES


def test_unrelated_email_does_not_match():
    result = match_email(
        ALL,
        sender="news@example.com",
        subject="50% off sale",
        body="Congratulations, you have won a prize!",
    )
    assert result["scholarship"] is None
    assert result["outcome"] == "unknown"