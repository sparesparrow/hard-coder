### Step 0: Write the tool functionality
```python
def get_stock_price(company):
    #Send a request to a stock market API to lookup current stock price for a given company

    #Returns a dictionary containing current stock price information for the specified company
```

### Step 1: Provide Claude with tools and a user prompt (API request)
<tool_definition>
```python
tool_definition = {
    "name": "get_stock_price",
    "description": "Retrieves the current stock price for a given company",
    "input_schema": {
        "type": "object",
        "properties": {
            "company": {
                "type": "string",
                "description": "The company name to fetch stock data for"
            }
        },
        "required": ["company"]
    }
}
```
</tool_definition>
<user_request>
```python
response = client.messages.create(
    model="claude-3-opus-20240229",
    messages=[{"role": "user", "content": "How many shares of General Motors can I buy with $500?"}],
    max_tokens=500,
    tools=[tool_definition]
)
```
</user_request>

### Step 2: Claude uses a tool (API response)

<assistant_response>
```json
{
  "stop_reason": "tool_use",
  "tool_use": {
    "name": "get_stock_price",
    "input": {
      "company": "General Motors"
    }
  }
}
```
</assistant_response>

### Step 3: Extract tool input, run code, and return results (API request)

- On the client side, we extract the tool name (get_stock_price) and input company name (General Motors) from Claude's tool use request.
```python
tool_name = 'get_stock_price'
company_name = 'General Motors'
```
- We execute the actual get_stock_price function that gets live stock market data from an API using the inputs extracted from Claude’s tool request.
<actual_function_call>
```python
stock_price = get_stock_price(company='General Motors')
```
</actual_function_call>
- The function might return data that looks like this:
<actual_function_return>
```json
{
  "symbol": "GM", 
  "price": 43.09
}
```
</actual_function_return>

### Step 4: Claude uses tool result to formulate a response (API response)
<example_api_response>
It looks like with a current share price of General Motors is 43.09.
</example_api_response>