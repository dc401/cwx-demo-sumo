#!/usr/bin/env python3
import asyncio, json, re, os, warnings
import fastapi_poe as fp

#read secrets from environment variables
api_key = os.environ['POE_API']

#need to use async because bot will have multi-line outputs that need to complete
#https://developer.poe.com/server-bots/accessing-other-bots-on-poe
async def get_responses(api_key, messages):
  response = ""
  async for partial in fp.get_bot_response(
      messages=messages,
      #bot_name="<YOUR-PUBLIC-BOT-NAME>",
      #bot_name="SL-Simulator-Bot",
      bot_name="Claude-3.5-Sonnet",
      api_key=api_key,
      temperature=0.15):
    if isinstance(partial, fp.PartialResponse) and partial.text:
      response += partial.text

  return response


#read the buildspec file
f = open('buildspec.json', 'r').read()
buildspec = json.loads(f)
detection_path = buildspec['detection']
test_path = buildspec['test']

#grab contents into memory
detection_payload = open(detection_path, 'r').read()
test_payload = open(test_path, 'r').read()

#parse out the query logic only DOTall matches multiple lines
regex_pattern = r'query\s{0,6}=\s{0,6}"(.{10,300})"'
#query_payload = re.search(regex_pattern, detection_payload)
query_payload = re.search(regex_pattern, detection_payload, re.DOTALL)
#print(query_payload.group(1))
if query_payload:
  query_payload = query_payload.group(1)
  print('###Parsed###\n ' + query_payload)
else:
  raise Exception("Error: No query payload found")

#prepend markdown prompt
prompt_file = open('prompt.md', 'r').read()

#construct the prompt without fstrings
prompt_text = prompt_file + '\n ## Sample Log \n' + test_payload + '\n ## Correlation Sumo Logic Search \n' + query_payload
#print(prompt_text)

message = fp.ProtocolMessage(role="user", content=(prompt_text))

#main driver
if __name__ == "__main__":
  #event loop response
  bot_response = asyncio.run(get_responses(api_key, [message]))
  print(bot_response)
  if 'HIGH' in bot_response:
    print('PASS: AI Evaluation - HIGH')
    exit()
  elif 'MEDIUM' in bot_response:
    print('CAUTION: AI Evaluation - MEDIUM')
    warnings.warn('CAUTION: AI Evaluation - MEDIUM')
  elif 'LOW' in bot_response:
    print('FAIL: AI Evaluation - LOW')
    raise ValueError(
        'TEST FAIL: AI Low probability Rating. Please check test log and query.')
    exit(1)
  elif 'UNKNOWN' in bot_response:
    print('FAIL: AI Evaluation - UNKNOWN')
    raise ValueError(
        'TEST FAIL: AI cannot determine detection. Please check test log and query.'
    )
    exit(1)
