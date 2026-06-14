# Goal Skill Delta Record

`goal_skill_delta_record` is the per-cycle return value for `$shadow`.

It tells `/goal` what happened this cycle and what to do next. It is not a background-monitoring promise.

Required fields:

- watched session and cursor;
- evidence delta;
- decision event;
- proposed delta;
- next goal action.
