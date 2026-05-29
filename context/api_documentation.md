
# Botmaker API endpoints documentation

## List Agents

List all agents with access to the bot.

### URL: <https://api.botmaker.com/v2.0/agents>

### Query parameters

- emails (array[string])
  - Fetch agents by email. A list of emails can be used, separated by comma or repeating the emails query param.
- online (boolean)
  - Filter online agents with true. Use false to filter the offline users.

### Response example

``` json
{
  "nextPage": "string",
  "items": [
    {
      "id": "string",
      "email": "agent.name@exampleorg.com",
      "name": "string",
      "alias": "string",
      "isOnline": true,
      "status": "online",
      "role": "string",
      "queues": [
        "sales",
        "returns"
      ],
      "slots": 0,
      "priority": "never",
      "groups": [
        "string"
      ],
      "additionalInfo": {
        "property1": {},
        "property2": {}
      },
      "creationTime": "2025-08-18T14:52:30Z"
    }
  ]
} 
```

## List channels

### URL: <https://api.botmaker.com/v2.0/channels>

### Query parameters

- active (boolean)
  - Filter only active channels.
- platform (string)
  - Fetch channels from platform only.

### Response example

``` json
{
  "items": [
    {
      "id": "string",
      "platform": "string",
      "active": true,
      "name": "string",
      "webhookId": "string"
    }
  ]
}
```

## List Agents Performance

Retrieve Agents Performance (as in Agent Performance page). By default, it retrieves today metrics.You can filter by:

    Specific range of time
    Specific group
    Specific queue
    Specific agent
    Specific role

### URL: <https://api.botmaker.com/v2.0/dashboards/agent-performance>

### Query parameters

- from (string date-time)
  - Min datetime. It not sent, it will default to the last hour.
  - Examples: 2021-01-01T00:00:00.000Z
- to (string date-time)
  - Max datetime. Requires "from"
  - Examples: 2022-01-05T12:30:42.000Z

### Response example

``` json
{
  "nextPage": "string",
  "items": [
    {
      "agentEmail": "example@botmaker.io",
      "agentName": "Example Botmaker",
      "role": "ADMIN",
      "queue": [
        "suporteOso",
        "suporteOsoEmail",
        "HelpCenter_OSO_BR"
      ],
      "state": "Busy",
      "checkin": "string",
      "checkout": "string"
    }
  ]
}
```

## List Agents Metrics

List agents metrics by conversation (as in Agent Metrics page). By default, it retrieves today metrics.You can filter by:
    Specific range of time
    List of Channel IDs
    List of Agent IDs
    List of Queues
    Agent Online Status
    Session Status (open, closed, both)

### URL: <https://api.botmaker.com/v2.0/dashboards/agent-metrics>

### Query parameters

session-status
string
required

Filter metrics by session status
Examples:
openclosed
agent-ids
array[string]

A list of agents id to filter with.
Examples:
["ABC123DEF456GHI789JK","ABC123DEF456GHI789JK"]
channel-ids
array[string]

Required to filter metrics by channel id.
Examples:
botproject-whatsapp-5491147038***5491147038***5125186904100***
from
string date-time

Min datetime. It not sent, it will default to the last hour.
Examples:
2021-01-01T00:00:00.000Z
online-status
string

The operator online status to filter with
Examples:
onlineofflineall
queues
array[string]

A list of queues to filter with.
Examples:
["ABC123DEF456GHI789JK","ABC123DEF456GHI789JK"]
to
string date-time

Max datetime. Requires "from"
Examples:
2022-01-05T12:30:42.000Z

### Response example

``` json
{
  "nextPage": "string",
  "items": [
    {
      "chatId": "DN5SFU5TP46YHJXVAX3F",
      "sessionCreationTime": "2023-04-17T00:00:00Z",
      "avgAttendingTime": "3358",
      "avgResponseTime": "3358",
      "queue": "Customer Service",
      "agentName": "Juan Perez",
      "agentId": "DrSDR1DauHPbRCBZshDTW5wcYS63",
      "sessionId": "DN5SFU5TP46YHJXVAX3F_2023-04-17T00:00:00.000Z",
      "typification": "Typification",
      "closedTime": "2023-04-17T12:00:00Z",
      "openSessions": "2",
      "closedSessions": "3",
      "onHold": "1",
      "opResponseTime": "223",
      "operatorResponses": "5",
      "sessionTransferIn": "1",
      "sessionTransferOut": "2",
      "sessionTransferOutNoMessages": "1",
      "closedWithNoMessages": "2",
      "timeoutNoMessages": "3",
      "agentTimeout": "2",
      "userTimeout": "2",
      "fromQueueAsignToOpAssigned": "1",
      "fromSessionStartToOpFirstResponse": "1",
      "fromQueueAsignToOpFirstResponse": "509",
      "fromOpAssignedToOpFirstResponse": "615",
      "fromQueueAsignToSessionClosed": "579",
      "fromOpAssignationToSessionClosed": "125",
      "sessionTimeout": "1",
      "conversationLink": "https://go.botmaker.com/#/chats/DN5SFU5TP46YHJXVAX3F"
    }
  ]
}
```

(This one should not be necessary, but it is documented just in case)

## List Sessions

List sessions in a period, sorted by start datetime. For each session, you can fetch its messages, final variables ,events and AI analysis by passing include-messages, include-variables, include-events, include-ai-analysis. Each one of these will increase your BI data sources costs.
This endpoint will increase your BI data sources costs, so use it with care (save the response to avoid retrieving the same period every time).

### URL: <https://api.botmaker.com/v2.0/sessions>

### Query parameters

- emails (array[string])
  - Fetch agents by email. A list of emails can be used, separated by comma or repeating the emails query param.
- online (boolean)
  - Filter online agents with true. Use false to filter the offline users.

### Response example

``` json
{
  "nextPage": "string",
  "items": [
    {
      "id": "string",
      "email": "agent.name@exampleorg.com",
      "name": "string",
      "alias": "string",
      "isOnline": true,
      "status": "online",
      "role": "string",
      "queues": [
        "sales",
        "returns"
      ],
      "slots": 0,
      "priority": "never",
      "groups": [
        "string"
      ],
      "additionalInfo": {
        "property1": {},
        "property2": {}
      },
      "creationTime": "2025-08-18T14:52:30Z"
    }
  ]
} 
```
