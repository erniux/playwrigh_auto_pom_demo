Feature: Login functionality
  Scenario: Successful login
    Given the user is on the login page
    When the user enters valid credentials
    #And clicks on the login button
    #Then the user should see the secure area
    #And the user should see a logout button

Scenario: Logout from secure page
    Given the user is logged in
    When the user clicks logout
    Then the user should return to the login page