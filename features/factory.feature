Feature: Factories can produce mastered blueprints

  Scenario: Producing a mastered, modded blueprint
    Given I have imported the blueprints module
    When I subclass Blueprint
    And I subclass Item
    And I subclass Weapon several times
    And I subclass Mod
    And I subclass Factory
    Then I can produce a magical weapon of DOOM
