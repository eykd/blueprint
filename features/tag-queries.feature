Feature: Tag Queries on Repositories

  We organize taggable objects inside a repository by tag. We can then
  query the repository by tag union, intersection, and difference.

  Scenario: Tag Union Query
    Given a tag repository with taggables in it
    When I query the repository with a tag union query
    Then I receive back the union of all taggables with any of the union query tags.

  Scenario: Tag Intersection Query
    Given a tag repository with taggables in it
    When I query the repository with a tag intersection query
    Then I receive back the intersection of all taggables with all the intersection query tags.

  Scenario: Tag Difference Query
    Given a tag repository with taggables in it
    When I query the repository with a tag difference query
    Then I receive back all taggables that do not have the difference query tags.
