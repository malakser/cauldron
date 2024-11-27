#set GROQ_API_KEY in the secrets
import os
from groq import Groq
import re

DBG_PROMPT = False

MAX_LAST_EVENTS = 10

INITIAL_EVENT = "A pine seed settles on the ground"
#INITIAL_EVENT = "On a cold and gray Chicago mornin'\nA poor little baby child is born\nIn the ghetto"
#INITIAL_EVENT = "An empire collapses"
#INITIAL_EVENT = "Two neutron stars collide"
#INITIAL_EVENT = "Dwie gwiazdy neutronowe zderzają się"
#INITIAL_EVENT = "A nuclear reactor overheats"
#INITIAL_EVENT = "A brand new 1993 Ford Taurus leaves the production line"
#INITIAL_EVENT = "1963 Pontiac tempest enters the dull suburb of Wilbursville Wisconsin"

LANGUAGE = "English"

VIBE = """\
The writing should be interesting, nuanced, intelligent
"""

#AUTHOR = "Douglas Adams"
#AUTHOR = "William S. Burroughs"
#AUTHOR = "Jack Kerouac"
#AUTHOR = "Ernest Hemingway"
#AUTHOR = "Thomas Pynchon"
#AUTHOR = "Hunter S. Thompson"
AUTHOR = "Ayn Rand"
#AUTHOR = "Henryk Sienkiewicz"
#AUTHOR = "Thucydides"

# TODO ask the LLM to describe the style of the author

BLACKLIST = """\
social and political aspects of climate change
justice
equality
non-profits
NGOs
ethics
college
charity
empathy
community
cringey success stories
child talent stories"""

REASONING = """\
The event should be causaly related to other events.
The subject in event's title should be explicit.
Reflect on the proper time of the event as well.
Explain how you came up with specific information."""

SEP = '=' * os.get_terminal_size()[0]




client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
events= [f"<event t=0>{INITIAL_EVENT}</event>"]

style = VIBE
if AUTHOR:
  style += f"""\
Write in the style of {AUTHOR}"""


def getprompt():
  return f"""\
Your task is to generate event based on the list of previous events.
Before you generate the event, reflect on it to make sure it makes sense.

Previous events:
<list>
{os.linesep.join(events[-MAX_LAST_EVENTS:])}
</list>

Response format:
<answer>
  <reflection>
    [REFLECTION]
  </reflection>
  <event t=[TIME IN SECONDS] title="[EVENT NAME]">
    [CONTENT]
  </event>
</answer>

{REASONING}

Style of writing that applies both to reflection and the event:
{style}

Don't talk about the following:
{BLACKLIST}
YOU SHALL NEVER WRITE ABOUT THOSE TOPICS

Write in the following language:
{LANGUAGE}

Remember to strictly adhere to the response format:
<answer>
  <reflection>
    [REFLECTION]
  </reflection>
  <event t=[TIME IN SECONDS] title="[EVENT NAME]">
    [CONTENT]
  </event>
</answer>

Strictly obey the response format.
Don't generate anything before the XML.
Don't generate anything after the XML.
Don't generate anything before the XML.
Don't generate anything after the XML."""

def gettag(t, s):
  return re.search(f'<{t}.*>.*</{t}>', s, re.DOTALL).group(0)

while True:
  prompt = getprompt()
  if DBG_PROMPT: print(prompt); break
  response = client.chat.completions.create(
      model="llama3-70b-8192",
      messages=[{'role': 'user', 'content': prompt}],
      max_tokens=1000,
      temperature=1.2)
  rc = response.choices[0].message.content
  print(rc)
  print(SEP)
  ev = gettag('event', rc)
  print(ev)
  print(SEP)
  print(f'Events provided: {len(events[-MAX_LAST_EVENTS:])}')
  print(response.usage)
  print(SEP)
  events.append(ev)
  input("Press Enter to generate more...")
  print(SEP)
