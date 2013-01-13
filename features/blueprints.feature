@blueprints
Feature: Blueprints as Taggable Classes

  Blueprints are taggable class objects. Each subclass of the
  Blueprint base class has its own tag repository.

  Scenario: Subclassing Blueprint
    Given I have imported the blueprints module
    When I subclass Blueprint
    Then my blueprint subclass will have a tag repository
    And my blueprint subclass will be tagged with its class name
    And my blueprint subclass will have any other defined tags.

  Scenario: Subclassing an Item
    Given I have imported the blueprints module
    When I subclass Blueprint
    And I subclass Item
    Then my item subclass will have a tag repository
    Then my item subclass tag repository will be the same as Item's
    And my item subclass will be tagged with its class name
    And my item subclass will inherit tags from Item
    And my item subclass will have any other defined tags.

  Scenario: Selecting blueprints by tag
    Given I have imported the blueprints module
    When I subclass Blueprint
    And I subclass Item
    And I subclass Weapon several times
    Then I can query Weapon subclasses by tag.
    And I can select a Weapon subclass by tag.
