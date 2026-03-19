Feature: Authentication user profile
  As an authenticated API consumer
  I want to fetch my profile from the authentication endpoint
  So that I can access my account details securely

  Scenario: Retrieve current authenticated user profile
    Given an existing registered user
    And the user is authenticated with the API client
    When the user requests the authentication profile endpoint
    Then the response status code is 200
    And the response includes the authenticated username
