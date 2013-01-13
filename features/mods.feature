@mods
Feature: Mods can modify other blueprints

  Blueprints are taggable class objects. Each subclass of the
  Blueprint base class has its own tag repository.

  Scenario: Modifying a blueprint
    Given I have imported the blueprints module
    When I subclass Blueprint
    And I subclass Item
    And I subclass Weapon several times
    And I subclass Mod
    Then I can mod a Club to create a modified Club of DOOM
