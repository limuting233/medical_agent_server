import asyncio

from langchain_core.messages import HumanMessage

from app.graph.graph import create_graph

if __name__ == '__main__':
    graph = create_graph()

