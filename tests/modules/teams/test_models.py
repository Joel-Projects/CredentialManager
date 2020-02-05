# pylint: disable=missing-docstring,invalid-name
#
#
# def test_ApiToken_check_owner(readonly_user, regular_user):
#     regular_user_team_member = models.TeamMember.query.filter(models.TeamMember.team == team_for_regular_user, models.TeamMember.user == readonly_user).first()
#     assert regular_user_team_member.check_owner(readonly_user)
#     assert not regular_user_team_member.check_owner(None)
#     assert not regular_user_team_member.check_owner(regular_user)
#
# def test_Team_check_owner(readonly_user, regular_user, team_for_regular_user):
#     assert team_for_regular_user.check_owner(regular_user)
#     assert not team_for_regular_user.check_owner(None)
#     assert not team_for_regular_user.check_owner(readonly_user)
