## Table of Contents
- [Create New Order](#1-create-new-order-api-endpoint)
- [Check Order Status](#2-check-order-status-api-endpoint)
- [Check Access Code Status](#3-check-access-code-status-api-endpoint)
- [Check Assessment List for Access Code](#4-check-assessment-list-for-access-code-api-endpoint)
- [Check Self Status](#5-check-self-status-api-endpoint)
- [Create New Assessment for Access Code](#6-create-new-assessment-for-access-code-api-endpoint)


# Base API URL

**URL** `https://chainvet-backend.herokuapp.com/api/v1`


# 1 Create New Order API Endpoint

## Endpoint

**POST** `/order/create/`

This endpoint is used to create a new order in the system. It supports both authenticated users and guests with a valid API key.

## Permissions

- Open to all users; however, authentication via a user account or a valid API key is required.

## Request Parameters

| Parameter        | Type    | Required | Description                                                                                                                                 |
|------------------|---------|----------|---------------------------------------------------------------------------------------------------------------------------------------------|
| `number_of_credits` | integer | Yes      | The number of credits to purchase.                                                                                                          |
| `payment_coin`     | string  | Yes      | The cryptocurrency coin to use for payment.                                                                                                 |
| `payment_network`  | string  | Yes      | The network of the cryptocurrency coin to use for payment.                                                                                  |
| `order_is_for_self`| boolean | Yes      | Indicates whether the order is for the user making the request. If false, an `access_code` must be provided for whom the order is intended. |
| `access_code`      | string  | Conditional | Required if `order_is_for_self` is false. The access code of the user for whom the order is intended.                                       |

## Success Response

- **Status Code**: 201 Created
- **Content**:
  ```json
  {
    "order_id": "string",
    "number_of_credits": "integer",
    "payment_coin": "string",
    "payment_network": "string",
    "created_at": "datetime",
    "status": "string"
  }

## Error Responses

- **Missing Required Parameters**:
  - **Status Code**: 400 Bad Request
  - **Content**: `{"detail": "Missing [parameter_name] parameter"}`

- **Invalid API Key or Credentials**:
  - **Status Code**: 403 Forbidden
  - **Content**: `{"detail": "Invalid API key."}` or `{"detail": "Invalid credentials. Please log in"}`

- **Invalid Access Code**:
  - **Status Code**: 400 Bad Request
  - **Content**: `{"detail": "Invalid access code"}`

- **Unable to Create Order**:
  - **Status Code**: 500 Internal Server Error
  - **Content**: `{"detail": "Unable to create order"}`

- **Unhandled Exception**:
  - **Status Code**: 500 Internal Server Error
  - **Content**: `{"error": "error message"}`

## Notes

- The endpoint requires the request to be made with a content type of `application/json`.
- Ensure your API key is included in the request header if you are not using an authenticated user session.
- This endpoint is atomic; if any part of the order creation fails, no changes will be committed to the database.

## Example cURL Request

```bash
curl -X POST 'https://chainvet-backend.herokuapp.com/api/v1/order/create/' \
-H 'Content-Type: application/json' \
-H 'X-API-KEY: YOUR_API_KEY' \
-d '{
  "number_of_credits": 10,
  "payment_coin": "Bitcoin",
  "payment_network": "BTC",
  "order_is_for_self": true
}'
```

# 2 Check Order Status API Endpoint

## Endpoint

**POST** `/order/status/`

Allows users and entities with a valid API key to check the status of an order by providing the order's ID.

## Permissions

- Open to all users; however, authentication via a user account or a valid API key is required.

## Request Parameters

| Parameter    | Type   | Required | Description                                                                                     |
|--------------|--------|----------|-------------------------------------------------------------------------------------------------|
| `order_id`   | string | Yes      | The unique identifier of the order for which status is being checked.                           |
| `access_code`| string | Conditional | Required if the request is made using an AccessCode for non-user entities to check order status.|

## Success Response

- **Status Code**: 200 OK
- **Content**:
  ```json
  {
    "order_id": "string",
    "status": "string",
    "created_at": "datetime",
    "updated_at": "datetime",
    "number_of_credits": "integer",
    "payment_coin": "string",
    "payment_network": "string",
  }
  ```

## Error Responses

- **Missing Required Parameters**:
  - **Status Code**: 400 Bad Request
  - **Content**:
    ```json
    {"detail": "Missing order_id parameter"}
    ```

- **Invalid API Key or Credentials**:
  - **Status Code**: 403 Forbidden
  - **Content**:
    ```json
    {"detail": "Invalid API key."}
    ```
    or
    ```json
    {"detail": "Invalid credentials. Please log in"}
    ```

- **Invalid Access Code** (If applicable):
  - **Status Code**: 400 Bad Request
  - **Content**:
    ```json
    {"detail": "Invalid access_code"}
    ```

- **Invalid Order ID**:
  - **Status Code**: 400 Bad Request
  - **Content**:
    ```json
    {"detail": "Invalid order_id"}
    ```

## Notes

- Ensure the `Content-Type` header is set to `application/json`.
- If using an AccessCode for authorization, include the `access_code` parameter in the request body.
- The response includes detailed order information, including its current status, creation and update timestamps, and other relevant details.

## Example cURL Request

```bash
curl -X POST 'https://chainvet-backend.herokuapp.com/api/v1/order/status/' \
-H 'Content-Type: application/json' \
-H 'X-API-KEY: YOUR_API_KEY' \
-d '{
  "order_id": "unique_order_id_here"
}'
```


# 3 Check Access Code Status API Endpoint

## Endpoint

**POST** `/accesscode/status/`

This endpoint allows users and entities with a valid API key to check the status of an access code.

## Permissions

- Open to all users; however, authentication via a user account or a valid API key is required.

## Request Parameters

| Parameter    | Type   | Required | Description                                   |
|--------------|--------|----------|-----------------------------------------------|
| `access_code`| string | Yes      | The access code whose status is being checked.|
## Success Response

- **Status Code**: 200 OK
- **Content**:
  ```json
  {
    "access_code": "string",
    "status": "string",
    "created_at": "datetime",
    "expires_at": "datetime",
    "affiliate_origin": "string",
    // Additional details about the access code
  }

### Error Responses


## Error Responses

- **Missing Required Parameters**:
  - **Status Code**: 400 Bad Request
  - **Content**:
    ```json
    {"detail": "Missing access_code parameter"}
    ```

- **Invalid API Key or Credentials**:
  - **Status Code**: 403 Forbidden
  - **Content**:
    ```json
    {"detail": "Invalid API key."}
    ```
    or
    ```json
    {"detail": "Credentials invalid or not provided. Please log in"}
    ```

- **Access Code Not Found**:
  - **Status Code**: 400 Bad Request
  - **Content**:
    ```json
    {"detail": "access_code not found"}
    ```


## Notes

- The request must include the `Content-Type: application/json` header.
- An API key must be included in the request header for API key-based authentication, or the user must be logged in.
- The response includes detailed information about the access code, including its current status and expiration details.

## Example cURL Request

```bash
curl -X POST 'https://chainvet-backend.herokuapp.com/api/v1/accesscode/status/' \
-H 'Content-Type: application/json' \
-H 'X-API-KEY: YOUR_API_KEY' \
-d '{
  "access_code": "your_access_code_here"
}'
```

# 4 Check Assessment List for Access Code API Endpoint

## Endpoint

**POST** `/accesscode/assessments/`

This endpoint allows users and entities with a valid API key to check a list of assessments associated with a given access code.

## Permissions

- Open to all users; however, authentication via a user account or a valid API key is required.
## Request Parameters

| Parameter            | Type  | Required | Description                                                                                          |
|----------------------|-------|----------|------------------------------------------------------------------------------------------------------|
| `access_code`        | string| Yes      | The access code associated with the assessments to be checked.                                       |
| `assessment_id_list` | list  | Yes      | A list of assessment IDs to be checked against the provided access code.                            |
## Success Response

- **Status Code**: 200 OK
- **Content**:
  ```json
  [
    {
      "assessment_id": "string",
      "status": "string",
      "created_at": "datetime",
      "updated_at": "datetime",
      // Additional details about each assessment
    },
    // More assessments...
  ]
  ```

## Error Responses

- **Missing Required Parameters**:
  - **Status Code**: 400 Bad Request
  - **Content**:
    ```json
    {"detail": "Missing access_code parameter"}
    ```
    or
    ```json
    {"detail": "Missing assessment_id_list parameter"}
    ```
    or
    ```json
    {"detail": "assessment_id_list must be a list"}
    ```

- **Invalid API Key or Credentials**:
  - **Status Code**: 403 Forbidden
  - **Content**:
    ```json
    {"detail": "Invalid API key."}
    ```
    or
    ```json
    {"detail": "Credentials invalid or not provided. Please log in"}
    ```

- **Access Code Not Found**:
  - **Status Code**: 400 Bad Request
  - **Content**:
    ```json
    {"detail": "access_code not found"}
    ```

- **No Assessments Found**:
  - **Status Code**: 404 Not Found
  - **Content**:
    ```json
    {"detail": "No assessments found"}
    ```

- **Unhandled Exception**:
  - **Status Code**: 500 Internal Server Error
  - **Content**:
    ```json
    {"detail": "Failure to fetch user data. Please contact support with error code KY53D and the current time: YYYY-MM-DD HH:MM:SS."}
    ```


## Notes

- The request must include the `Content-Type: application/json` header.
- An API key must be included in the request header for API key-based authentication, or the user must be logged in.
- The endpoint expects `assessment_id_list` to be a JSON array of assessment IDs.
- This endpoint is designed to provide detailed information about each assessment in the list for the given access code.
## Example cURL Request

```bash
curl -X POST 'https://chainvet-backend.herokuapp.com/api/v1/accesscode/assessments/' \
-H 'Content-Type: application/json' \
-H 'X-API-KEY: YOUR_API_KEY' \
-d '{
  "access_code": "your_access_code_here",
  "assessment_id_list": ["assessment_id_1", "assessment_id_2"]
}'
```

# 5 Check Self Status API Endpoint

## Endpoint

**GET** `/user/status/`

This endpoint allows users or entities with a valid API key to check their own status within the system.

## Permissions

- Open to all users; however, authentication via a user account or a valid API key is required.

## Success Response

- **Status Code**: 200 OK
- **Content**:
  ```json
  {
    // User or Access Code specific information
    "id": "string",
    "type": "User/AccessCode",
    "status": "Active/Inactive",
    // Additional details specific to the user or access code
  }
  ```


## Error Responses

- **Invalid API Key or Credentials**:
  - **Status Code**: 403 Forbidden
  - **Content**:
    ```json
    {"detail": "Invalid API key."}
    ```
    or
    ```json
    {"detail": "Credentials invalid or not provided. Please log in"}
    ```

- **User Not Identified by API Key**:
  - **Status Code**: 403 Forbidden
  - **Content**:
    ```json
    {"detail": "User not identified by APIKey"}
    ```

- **Unhandled Exception**:
  - **Status Code**: 500 Internal Server Error
  - **Content**:
    ```json
    {"detail": "Failure to fetch user data. Please contact support with error code 4W9Y2."}
    ```

## Notes

- No URL parameters or request body is needed for this endpoint; authentication is performed based on the API key or user session.
- The response content will vary depending on whether the authenticated entity is a User or an Access Code.
- Ensure that the API key or user session token is included in the request header for authentication.

## Example cURL Request

```bash
curl -X GET 'https://chainvet-backend.herokuapp.com/api/v1/user/status/' \
-H 'X-API-KEY: YOUR_API_KEY'
```

# 6 Create New Assessment for Access Code API Endpoint

## Endpoint

**POST** `/accesscode/create/assessment/`

This endpoint initiates the creation of a new assessment for a given access code, allowing users and entities with a valid API key to submit assessment requests.

## Permissions

- Open to all users; however, authentication via a user account or a valid API key is required.

## Request Parameters

| Parameter         | Type   | Required | Description                                                                                   |
|-------------------|--------|----------|-----------------------------------------------------------------------------------------------|
| `access_code`     | string | Yes      | The access code for which the assessment is being created.                                    |
| `assessment_type` | string | Yes      | The type of assessment to be conducted (e.g., "transaction").                                 |
| `address`         | string | Yes      | The blockchain address involved in the assessment.                                            |
| `currency`        | string | Yes      | The cryptocurrency involved in the assessment (e.g., "BTC").                                  |
| `tx_hash`         | string | Conditional | The transaction hash, required if the assessment type is "transaction".                       |

## Success Response

- **Status Code**: 201 Created
- **Content**:
  ```json
  {
    "assessment_id": "string",
    "status": "string",
    "created_at": "datetime",
    // Additional details about the created assessment
  }
  ```


## Error Responses

- **Missing Required Parameters**:
  - **Status Code**: 400 Bad Request
  - **Content**:
    ```json
    {"detail": "Missing [parameter_name] parameter"}
    ```

- **Invalid API Key or Credentials**:
  - **Status Code**: 403 Forbidden
  - **Content**:
    ```json
    {"detail": "Invalid API key."}
    ```
    or
    ```json
    {"detail": "Credentials invalid or not provided. Please log in"}
    ```

- **Access Code Not Found**:
  - **Status Code**: 400 Bad Request
  - **Content**:
    ```json
    {"detail": "access_code not found"}
    ```

- **Failure to Create New Assessment**:
  - **Status Code**: 500 Internal Server Error
  - **Content**:
    ```json
    {"detail": "Failure to create new assessment. Please contact support with error code 4J9Y1. Error: [error_description]"}
    ```


## Notes

- The request must include the `Content-Type: application/json` header.
- An API key or user session token must be included in the request header for authentication.
- Specific parameters are required based on the assessment type; for a "transaction" type, `tx_hash` is mandatory.
- The response will include details of the newly created assessment, including its ID and status.

## Example cURL Request

```bash
curl -X POST 'https://chainvet-backend.herokuapp.com/api/v1/accesscode/create/assessment/' \
-H 'Content-Type: application/json' \
-H 'X-API-KEY: YOUR_API_KEY' \
-d '{
  "access_code": "your_access_code_here",
  "assessment_type": "transaction",
  "address": "blockchain_address_here",
  "currency": "BTC",
  "tx_hash": "transaction_hash_here"
}'
```