@dice
Feature: Rolling dice.

  Dice come in many shapes and sizes. We should be able to "roll"
  dice using standard dice expressions.

  Scenario Outline: Rolling dice
    Given I have <dice expression>
    When I compile the dice expression
    And I roll the dice 10000 times
    Then the sum should be less than <min sum>
    And the sum should not exceed <max sum>
    And the minimum individual roll should not be less than <min roll>
    And the maximum individual roll should not exceed <max roll>

  Examples: Normal dice
    | dice expression | min sum | max sum | min roll | max roll |
    |             1d6 |       1 |       6 |        1 |        6 |
    |             2d6 |       2 |      12 |        1 |        6 |


  Examples: Fudge dice
    | dice expression | min sum | max sum | min roll | max roll |
    | 1dF             |      -1 |       1 |       -1 |        1 |
    | 2dF             |      -2 |       2 |       -1 |        1 |

