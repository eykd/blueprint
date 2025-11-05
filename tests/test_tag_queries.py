"""Tests for tag query functionality on repositories.

Converted from features/tag-queries.feature
"""

from blueprint import taggables


def test_tag_union_query(
    repo: taggables.TagRepository,
    t1: taggables.Taggable,
    t2: taggables.Taggable,
    t3: taggables.Taggable,
    t4: taggables.Taggable,
) -> None:
    """Test tag union queries on repositories.

    Scenario: Tag Union Query
    - Query repository with union of tags
    - Receive back all taggables with ANY of the query tags
    """
    # Query 1: union of foo, bar, boo - should match all taggables
    q1 = repo.query_tags_union('foo', 'bar', 'boo')
    assert t1 in q1
    assert t2 in q1
    assert t3 in q1
    assert t4 in q1

    # Query 2: union of bar, boo - should match t2, t3, t4 but not t1
    q2 = repo.query_tags_union('bar', 'boo')
    assert t1 not in q2
    assert t2 in q2
    assert t3 in q2
    assert t4 in q2


def test_tag_intersection_query(
    repo: taggables.TagRepository,
    t1: taggables.Taggable,
    t2: taggables.Taggable,
    t3: taggables.Taggable,
    t4: taggables.Taggable,
) -> None:
    """Test tag intersection queries on repositories.

    Scenario: Tag Intersection Query
    - Query repository with intersection of tags
    - Receive back all taggables with ALL of the query tags
    """
    # Query 1: intersection of foo and bar - should match t2 and t3
    q1 = repo.query_tags_intersection('foo', 'bar')
    assert t1 not in q1
    assert t2 in q1, f'{t2} should be in {q1}'
    assert t3 in q1
    assert t4 not in q1

    # Query 2: intersection of foo and boo - should match nothing
    q2 = repo.query_tags_intersection('foo', 'boo')
    assert t1 not in q2
    assert t2 not in q2
    assert t3 not in q2
    assert t4 not in q2


def test_tag_difference_query(
    repo: taggables.TagRepository,
    t1: taggables.Taggable,
    t2: taggables.Taggable,
    t3: taggables.Taggable,
    t4: taggables.Taggable,
) -> None:
    """Test tag difference queries on repositories.

    Scenario: Tag Difference Query
    - Query repository with difference of tags
    - Receive back all taggables that do NOT have the query tags
    """
    # Query 1: difference of foo - should only match t4
    q1 = repo.query_tags_difference('foo')
    assert t1 not in q1
    assert t2 not in q1
    assert t3 not in q1
    assert t4 in q1

    # Query 2: difference of baz and boo - should match t1 and t2
    q2 = repo.query_tags_difference('baz', 'boo')
    assert t1 in q2
    assert t2 in q2
    assert t3 not in q2
    assert t4 not in q2
