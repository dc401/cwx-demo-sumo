#!/usr/bin/env python3
import asyncio, json, re, os, warnings
import fastapi_poe as fp

#read secrets from environment variables
api_key = os.environ['POE_API']


#need to use async because bot will have multi-line outputs that need to complete
#https://developer.poe.com/server-bots/accessing-other-bots-on-poe
#use the official botname case sensitive from poe or your custom name of one you created
async def get_responses(api_key, messages, bot_name="Claude-3.5-Sonnet"):
  response = ""
  print(f"Using bot: {bot_name}")
  async for partial in fp.get_bot_response(messages=messages,
                                           bot_name=bot_name,
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
query_payload = re.search(regex_pattern, detection_payload)
#query_payload = re.search(regex_pattern, detection_payload, re.DOTALL)
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

  #initialize variables
  high_count = 0
  medium_count = 0
  low_count = 0
  unknown_count = 0

  #collect multiple bot response
  claude_response = asyncio.run(get_responses(api_key, [message]))
  print("Claude Response: " + claude_response)
  gemini_response = asyncio.run(
      get_responses(api_key, [message], bot_name="Gemini-1.5-Pro"))
  print("Gemini Response: " + gemini_response)

  #count the response types from each bot equal weighting
  combined_response = claude_response + ' ' + gemini_response
  if '/HIGH/' in combined_response:
    high_count = combined_response.count('/HIGH/')
  if '/MEDIUM/' in combined_response:
    medium_count = combined_response.count('/MEDIUM/')
  if '/LOW/' in combined_response:
    low_count = combined_response.count('/LOW/')
  if '/UNKNOWN/' in combined_response:
    unknown_count = combined_response.count('/UNKNOWN/')

  #eval conditions
  if high_count > 1:
    print('PASS: AI Evaluation are both high.')
    exit(0)
  elif medium_count > 0 and high_count > 0:
    print('WARN: AI Evaluation high and medium')
    warnings.warn('WARN: AI Evaluation high and medium', stacklevel=1)
    exit(0)
  elif medium_count > 2 or low_count > 0:
    print('FAIL: AI evaluation confidence not high enough.')
    exit(1)
  elif unknown_count > 0:
    print('FAIL: AI evaluation unknown.')
    exit(1)

