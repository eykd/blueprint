# -*- coding: utf-8 -*-
"""queries -- tag query step definitions.
"""
from blueprint import taggables


@given(u'a tag repository with taggables in it')
def step(context):
    repo = context.repo = taggables.TagRepository()
    context.t1 = taggables.Taggable(repo, 't1', 'foo')
    context.t2 = taggables.Taggable(repo, 't2', 'foo', 'bar')
    context.t3 = taggables.Taggable(repo, 't3', 'foo', 'bar', 'baz')
    context.t4 = taggables.Taggable(repo, 't3', 'boo')


### Union Queries
@when(u'I query the repository with a tag union query')
def step(context):
    context.q1 = context.repo.queryTagsUnion('foo', 'bar', 'boo')
    context.q2 = context.repo.queryTagsUnion('bar', 'boo')


@then(u'I receive back the union of all taggables with any of the union query tags.')
def step(context):
    assert context.t1 in context.q1
    assert context.t2 in context.q1
    assert context.t3 in context.q1
    assert context.t4 in context.q1

    assert context.t1 not in context.q2
    assert context.t2 in context.q2
    assert context.t3 in context.q2
    assert context.t4 in context.q2


### Intersection Queries
@when(u'I query the repository with a tag intersection query')
def step(context):
    context.q1 = context.repo.queryTagsIntersection('foo', 'bar')
    context.q2 = context.repo.queryTagsIntersection('foo', 'boo')
    

@then(u'I receive back the intersection of all taggables with all the intersection query tags.')
def step(context):
    assert context.t1 not in context.q1
    assert context.t2 in context.q1, (context.t2, context.q1)
    assert context.t3 in context.q1
    assert context.t4 not in context.q1

    assert context.t1 not in context.q2
    assert context.t2 not in context.q2
    assert context.t3 not in context.q2
    assert context.t4 not in context.q2


### Difference Queries
@when(u'I query the repository with a tag difference query')
def step(context):
    context.q1 = context.repo.queryTagsDifference('foo')
    context.q2 = context.repo.queryTagsDifference('baz', 'boo')


@then(u'I receive back all taggables that do not have the difference query tags.')
def step(context):
    assert context.t1 not in context.q1
    assert context.t2 not in context.q1
    assert context.t3 not in context.q1
    assert context.t4 in context.q1

    assert context.t1 in context.q2
    assert context.t2 in context.q2
    assert context.t3 not in context.q2
    assert context.t4 not in context.q2
