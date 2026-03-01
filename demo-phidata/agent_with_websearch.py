from datetime import datetime

from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.newspaper4k import Newspaper4k

from dotenv import load_dotenv


def get_current_datetime() -> str:
    """Returns the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

load_dotenv()

def create_websearch_agent():
    """Creates a single conversational agent."""
    agent = Agent(
        name="Jarvis",
        model=OpenAIChat(id="gpt-4o"),
        description="You are a research assistant that searches the web for information",
        instructions=[
            "Always search for the most recent information.",
            "Include sources in your responses.",
            "Summarize findings clearly.",
            "Use the get_current_datetime tool to get today's date and time when the query involves current events, recent news, or time-sensitive information.",
            "Use the Newspaper4k tool to scrape and read the full content of a URL when deeper article details are needed beyond search snippets.",
        ],
        show_tool_calls=True,
        markdown=True,
        debug_mode=False, 
        tools=[DuckDuckGo(), Newspaper4k(), get_current_datetime]
    )
    return agent

if __name__ == "__main__":
    agent = create_websearch_agent()
    agent.print_response("what are the new movies release in hollywood and also some details about these movies", stream=True)